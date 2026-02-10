"""
Plan management endpoints (T104).

Provides endpoints for viewing and managing execution plans.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from chatbot.api.dependencies import CurrentUser, get_current_user, validate_user_access
from chatbot.api.schemas import (
    GetPlanResponse,
    ApprovePlanRequest,
    ApprovePlanResponse,
    APIResponse,
    PlanResponse,
    PlanStepSchema,
)
from chatbot.agent.session import (
    get_session,
    get_session_confirmation,
    set_session_confirmation,
)
from chatbot.agent.confirmation import ConfirmationManager
from chatbot.agent.models import ConfirmationStatus


router = APIRouter()


# In-memory plan storage (production should use database)
_plans: dict = {}


@router.get("/sessions/{session_id}/plan", response_model=GetPlanResponse)
async def get_current_plan(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> GetPlanResponse:
    """
    Get current execution plan (T104).

    Returns details of any pending execution plan for the session.

    Args:
        session_id: Session UUID

    Returns:
        Plan details or empty if no plan

    Raises:
        404: Session not found
        403: Session belongs to different user
    """
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    # Check if there's a pending plan approval
    confirmation_state = await get_session_confirmation(session_id)

    if confirmation_state is None:
        return GetPlanResponse(
            success=True,
            data={"plan": None, "message": "No active plan"},
        )

    if confirmation_state.state != ConfirmationStatus.AWAITING_PLAN_APPROVAL:
        return GetPlanResponse(
            success=True,
            data={"plan": None, "message": "No pending plan approval"},
        )

    # Get the plan from storage
    plan_id = confirmation_state.affected_ids[0] if confirmation_state.affected_ids else None
    if plan_id and plan_id in _plans:
        plan = _plans[plan_id]
        return GetPlanResponse(
            success=True,
            data={
                "plan": PlanResponse(
                    plan_id=plan.plan_id,
                    status=plan.status.value,
                    steps=[
                        PlanStepSchema(
                            order=step.order,
                            action=step.action.value,
                            description=f"{step.action.value}: {step.params.get('reference', '')}",
                            status="pending",
                        )
                        for step in plan.steps
                    ],
                    current_step=None,
                )
            },
        )

    return GetPlanResponse(
        success=True,
        data={
            "plan": None,
            "description": confirmation_state.action_description,
        },
    )


@router.post("/sessions/{session_id}/plan/approve", response_model=ApprovePlanResponse)
async def approve_plan(
    session_id: UUID,
    request: ApprovePlanRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> ApprovePlanResponse:
    """
    Approve or reject execution plan (T104).

    Approves the pending plan for execution or rejects it.

    Args:
        session_id: Session UUID
        request: Approval request

    Returns:
        Result of approval action

    Raises:
        404: Session not found
        403: Session belongs to different user
        400: No pending plan
    """
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    confirmation_state = await get_session_confirmation(session_id)

    if confirmation_state is None or confirmation_state.state != ConfirmationStatus.AWAITING_PLAN_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending plan approval",
        )

    manager = ConfirmationManager(state=confirmation_state)

    if request.approve:
        manager.confirm()
        message = "Plan approved. Executing..."
        # TODO: Execute the plan
    else:
        manager.cancel()
        message = "Plan cancelled."

    await set_session_confirmation(session_id, manager.state)

    return ApprovePlanResponse(
        success=True,
        data={
            "approved": request.approve,
            "message": message,
        },
    )


@router.delete("/sessions/{session_id}/plan", response_model=APIResponse)
async def cancel_plan(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> APIResponse:
    """
    Cancel current execution plan (T104).

    Cancels any pending plan without executing it.

    Args:
        session_id: Session UUID

    Returns:
        Cancellation confirmation

    Raises:
        404: Session not found
        403: Session belongs to different user
    """
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    confirmation_state = await get_session_confirmation(session_id)

    if confirmation_state and confirmation_state.state == ConfirmationStatus.AWAITING_PLAN_APPROVAL:
        manager = ConfirmationManager(state=confirmation_state)
        manager.cancel()
        await set_session_confirmation(session_id, manager.state)

        return APIResponse(
            success=True,
            data={"message": "Plan cancelled"},
        )

    return APIResponse(
        success=True,
        data={"message": "No active plan to cancel"},
    )
