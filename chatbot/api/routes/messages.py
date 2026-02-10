"""
Message handling endpoints (T100-T102).

Provides endpoints for sending messages and getting conversation history.
"""

import asyncio
import json
from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from chatbot.api.dependencies import CurrentUser, get_current_user, validate_user_access
from chatbot.api.schemas import (
    SendMessageRequest,
    SendMessageResponse,
    GetHistoryResponse,
    MessageResponse,
)
from chatbot.agent.session import (
    get_session,
    update_session,
    get_session_context,
    set_session_context,
    get_session_confirmation,
    set_session_confirmation,
)
from chatbot.agent.core import process_message
from chatbot.agent.confirmation import ConfirmationManager


router = APIRouter()


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: UUID,
    request: SendMessageRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> SendMessageResponse:
    """
    Send a message to the agent (T100).

    Processes a user message through the agent and returns the response.
    May trigger confirmation requests for destructive actions.

    Args:
        session_id: Session UUID
        request: Message request body

    Returns:
        Agent response and any required confirmation state

    Raises:
        404: Session not found
        403: Session belongs to different user
    """
    # Get and validate session
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    # Get current context and confirmation state
    context = await get_session_context(session_id)
    confirmation_state = await get_session_confirmation(session_id)

    # Check for pending confirmation
    if confirmation_state:
        manager = ConfirmationManager(state=confirmation_state)
        if manager.has_pending_confirmation():
            # Process as confirmation response
            result = manager.process_response(request.message)
            await set_session_confirmation(session_id, manager.state)

            if result["unclear"]:
                return SendMessageResponse(
                    success=True,
                    data={
                        "response": result["message"],
                        "requires_confirmation": True,
                        "confirmation_type": manager.state.state.value,
                    },
                )
            else:
                # Confirmation processed, now execute if confirmed
                # For now, return the confirmation result
                return SendMessageResponse(
                    success=True,
                    data={
                        "response": result["message"],
                        "confirmed": result["confirmed"],
                        "cancelled": result["cancelled"],
                    },
                )

    # Process message through agent
    result = await process_message(
        user_message=request.message,
        user_id=current_user.user_id,
        session=session,
        context=context,
        confirmation_state=confirmation_state,
    )

    # Update session last_active
    await update_session(session)

    # Save updated context and confirmation state
    if result.get("context"):
        await set_session_context(session_id, result["context"])
    if result.get("confirmation_state"):
        await set_session_confirmation(session_id, result["confirmation_state"])

    if not result["success"]:
        return SendMessageResponse(
            success=False,
            error={
                "code": "PROCESSING_ERROR",
                "message": result.get("error", "Failed to process message"),
            },
        )

    # Check if confirmation is now required
    requires_confirmation = False
    confirmation_type = None
    if result.get("confirmation_state"):
        state = result["confirmation_state"]
        if state.is_awaiting_confirmation():
            requires_confirmation = True
            confirmation_type = state.state.value

    return SendMessageResponse(
        success=True,
        data={
            "response": result["response"],
            "requires_confirmation": requires_confirmation,
            "confirmation_type": confirmation_type,
        },
    )


@router.post("/sessions/{session_id}/messages/stream")
async def send_message_stream(
    session_id: UUID,
    request: SendMessageRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> StreamingResponse:
    """
    Send a message with streaming response (T101).

    Returns Server-Sent Events (SSE) stream for real-time response.

    Args:
        session_id: Session UUID
        request: Message request body

    Returns:
        SSE stream with agent response chunks
    """
    # Validate session
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    validate_user_access(session.user_id, current_user)

    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        try:
            # Get context
            context = await get_session_context(session_id)
            confirmation_state = await get_session_confirmation(session_id)

            # Process message
            result = await process_message(
                user_message=request.message,
                user_id=current_user.user_id,
                session=session,
                context=context,
                confirmation_state=confirmation_state,
            )

            # Update session
            await update_session(session)

            # Save context
            if result.get("context"):
                await set_session_context(session_id, result["context"])

            # Stream the response
            if result["success"]:
                # For now, send full response as single event
                # Future: integrate with streaming LLM API
                response = result["response"]
                data = json.dumps({
                    "type": "message",
                    "content": response,
                })
                yield f"data: {data}\n\n"

                # Send completion event
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            else:
                error_data = json.dumps({
                    "type": "error",
                    "error": result.get("error", "Processing failed"),
                })
                yield f"data: {error_data}\n\n"

        except Exception as e:
            error_data = json.dumps({
                "type": "error",
                "error": "An error occurred",
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/sessions/{session_id}/history", response_model=GetHistoryResponse)
async def get_conversation_history(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> GetHistoryResponse:
    """
    Get conversation history (T102).

    Returns the message history for a session.

    Args:
        session_id: Session UUID

    Returns:
        List of messages in the conversation

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

    # Get context with message history
    context = await get_session_context(session_id)

    messages = []
    if context:
        for msg in context.messages:
            messages.append(MessageResponse(
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp,
            ))

    return GetHistoryResponse(
        success=True,
        data={"messages": messages},
    )
