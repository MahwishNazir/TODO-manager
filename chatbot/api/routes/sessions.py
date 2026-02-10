"""
Session management endpoints (T097-T099).

Provides endpoints for creating, getting, and deleting agent sessions.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from chatbot.api.dependencies import CurrentUser, get_current_user, validate_user_access
from chatbot.api.schemas import (
    CreateSessionResponse,
    GetSessionResponse,
    APIResponse,
    SessionResponse,
)
from chatbot.agent.session import (
    create_session,
    get_session,
    delete_session,
    get_session_store,
)


router = APIRouter()


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_new_session(
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CreateSessionResponse:
    """
    Create a new agent session (T097).

    Creates a new conversation session for the authenticated user.
    Sessions expire after 30 minutes of inactivity.

    Returns:
        Created session details
    """
    session = await create_session(current_user.user_id)

    return CreateSessionResponse(
        success=True,
        data={
            "session": SessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                created_at=session.created_at,
                last_active=session.last_active,
                status=session.status.value,
            )
        },
    )


@router.get("/sessions/{session_id}", response_model=GetSessionResponse)
async def get_session_details(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> GetSessionResponse:
    """
    Get session details (T098).

    Returns details about an existing session.
    Session must belong to the authenticated user.

    Args:
        session_id: Session UUID

    Returns:
        Session details

    Raises:
        404: Session not found or expired
        403: Session belongs to different user
    """
    session = await get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    return GetSessionResponse(
        success=True,
        data={
            "session": SessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                created_at=session.created_at,
                last_active=session.last_active,
                status=session.status.value,
            )
        },
    )


@router.delete("/sessions/{session_id}", response_model=APIResponse)
async def delete_session_endpoint(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> APIResponse:
    """
    Delete a session (T099).

    Permanently deletes a session and all associated data.
    Session must belong to the authenticated user.

    Args:
        session_id: Session UUID

    Returns:
        Success confirmation

    Raises:
        404: Session not found
        403: Session belongs to different user
    """
    # First verify the session exists and user has access
    session = await get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    validate_user_access(session.user_id, current_user)

    # Delete the session
    deleted = await delete_session(session_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return APIResponse(
        success=True,
        data={"message": "Session deleted successfully"},
    )
