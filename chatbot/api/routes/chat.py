"""
Stateless Chat API endpoint (Phase III Part 5).

Provides a single endpoint for AI agent chat interactions with full statelessness.
All conversation context is provided by the client in each request.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from chatbot.api.dependencies import CurrentUser, get_current_user, validate_user_id_match
from chatbot.api.schemas import StatelessChatRequest, StatelessChatResponse
from chatbot.agent.stateless_runner import get_stateless_runner


router = APIRouter()


MAX_MESSAGE_LENGTH = 10000
VALID_ROLES = {"user", "assistant"}
MAX_MESSAGES = 50


@router.post(
    "/{user_id}/chat",
    response_model=StatelessChatResponse,
    status_code=200,
)
async def stateless_chat(
    user_id: str,
    request: StatelessChatRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Process a stateless chat request.

    All conversation context must be provided in the request body.
    No server-side state is maintained between calls.
    """
    # Validate user_id matches JWT subject
    validate_user_id_match(user_id, current_user)

    # Validate messages are not empty (Pydantic min_length=1 handles this,
    # but we provide a clear error response)
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMPTY_MESSAGES",
                "message": "Messages array must not be empty",
            },
        )

    # Validate message count
    if len(request.messages) > MAX_MESSAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "HISTORY_LIMIT_EXCEEDED",
                "message": f"Maximum {MAX_MESSAGES} messages allowed per request",
            },
        )

    # Validate individual messages
    for msg in request.messages:
        if msg.role not in VALID_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_MESSAGE_FORMAT",
                    "message": f"Invalid role '{msg.role}'. Must be 'user' or 'assistant'",
                },
            )
        if len(msg.content) > MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "MESSAGE_TOO_LONG",
                    "message": f"Message content exceeds {MAX_MESSAGE_LENGTH} character limit",
                },
            )

    # Convert Pydantic models to dicts for the runner
    messages_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    # Execute via the stateless runner
    runner = get_stateless_runner()
    result = await runner.run(messages=messages_dicts, user_id=user_id)

    return result
