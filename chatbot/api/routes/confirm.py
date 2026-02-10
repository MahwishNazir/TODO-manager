"""
Confirmation action endpoint (T103).

Provides endpoint for confirming or cancelling pending actions.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from chatbot.api.dependencies import CurrentUser, get_current_user, validate_user_access
from chatbot.api.schemas import ConfirmActionRequest, ConfirmActionResponse
from chatbot.agent.session import (
    get_session,
    get_session_confirmation,
    set_session_confirmation,
)
from chatbot.agent.confirmation import ConfirmationManager


router = APIRouter()


@router.post("/sessions/{session_id}/confirm", response_model=ConfirmActionResponse)
async def confirm_action(
    session_id: UUID,
    request: ConfirmActionRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> ConfirmActionResponse:
    """
    Confirm or cancel a pending action (T103).

    Processes the user's confirmation response (yes/no/cancel).

    Args:
        session_id: Session UUID
        request: Confirmation response

    Returns:
        Result of confirmation processing

    Raises:
        404: Session not found
        403: Session belongs to different user
        400: No pending confirmation
    """
    # Validate session
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    # Get confirmation state
    confirmation_state = await get_session_confirmation(session_id)
    if confirmation_state is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending confirmation",
        )

    manager = ConfirmationManager(state=confirmation_state)

    if not manager.has_pending_confirmation():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending confirmation",
        )

    # Process the response
    result = manager.process_response(request.response)

    # Save updated state
    await set_session_confirmation(session_id, manager.state)

    if result["unclear"]:
        return ConfirmActionResponse(
            success=True,
            data={
                "confirmed": False,
                "cancelled": False,
                "unclear": True,
                "message": result["message"],
                "pending_action": result["action"],
            },
        )

    return ConfirmActionResponse(
        success=True,
        data={
            "confirmed": result["confirmed"],
            "cancelled": result["cancelled"],
            "unclear": False,
            "action": result["action"],
            "affected_ids": result["affected_ids"],
            "message": result["message"],
        },
    )


@router.get("/sessions/{session_id}/confirm/status")
async def get_confirmation_status(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> ConfirmActionResponse:
    """
    Get current confirmation status.

    Returns details about any pending confirmation.

    Args:
        session_id: Session UUID

    Returns:
        Confirmation status details
    """
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    confirmation_state = await get_session_confirmation(session_id)

    if confirmation_state is None or confirmation_state.is_idle():
        return ConfirmActionResponse(
            success=True,
            data={
                "has_pending": False,
                "state": "IDLE",
            },
        )

    manager = ConfirmationManager(state=confirmation_state)

    # Check for expiration
    if not manager.has_pending_confirmation():
        return ConfirmActionResponse(
            success=True,
            data={
                "has_pending": False,
                "state": "EXPIRED",
                "message": manager.get_expiration_message(),
            },
        )

    return ConfirmActionResponse(
        success=True,
        data={
            "has_pending": True,
            "state": confirmation_state.state.value,
            "action": confirmation_state.pending_action,
            "affected_ids": confirmation_state.affected_ids,
            "description": confirmation_state.action_description,
        },
    )
