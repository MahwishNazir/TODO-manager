"""
ChatKit API Route (T004).

FastAPI endpoint that handles ChatKit protocol requests with JWT authentication.
Bridges the ChatKit frontend to the TodoChatKitServer.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse

from chatbot.api.dependencies import get_current_user, CurrentUser
from chatbot.chatkit.store import MemoryStore, ThreadItem
from chatbot.chatkit.server import TodoChatKitServer, AgentContext
from chatbot.chatkit.adapter import (
    parse_chatkit_request,
    StreamingResult,
)


router = APIRouter(tags=["chatkit"])

# Singleton store and server (per-process)
_store: MemoryStore | None = None
_server: TodoChatKitServer | None = None


def get_store() -> MemoryStore:
    """Get or create the memory store singleton."""
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store


def get_server() -> TodoChatKitServer:
    """Get or create the ChatKit server singleton."""
    global _server
    if _server is None:
        _server = TodoChatKitServer(store=get_store())
    return _server


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Handle ChatKit protocol requests.

    This endpoint:
    1. Validates JWT authentication
    2. Parses the ChatKit request format
    3. Processes through TodoChatKitServer
    4. Returns streaming SSE response

    Request Body:
        {
            "thread_id": "thread_abc123",
            "message": {
                "type": "user_message",
                "content": "Add a task to buy groceries"
            },
            "metadata": {}
        }

    Response:
        Server-Sent Events stream with:
        - text_delta: Partial text response
        - tool_call: Tool invocation
        - tool_result: Tool execution result
        - error: Error occurred
        - done: Stream completed

    Raises:
        401 Unauthorized: Invalid or missing JWT
        400 Bad Request: Malformed request
        500 Internal Server Error: Processing error
    """
    # Parse request body
    try:
        body = await request.body()
        chatkit_req = parse_chatkit_request(body)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": str(e),
                }
            },
        )

    # Get server instance
    server = get_server()
    store = get_store()

    # Get or create thread
    thread = await server.get_or_create_thread(
        thread_id=chatkit_req.thread_id,
        user_id=current_user.user_id,
    )

    # Create user message item if content provided
    input_message = None
    if chatkit_req.message_content:
        input_message = ThreadItem(
            id=store.generate_id(),
            thread_id=chatkit_req.thread_id,
            type=chatkit_req.message_type,
            content=chatkit_req.message_content,
            metadata=chatkit_req.metadata,
        )

    # Create agent context
    context = AgentContext(
        thread=thread,
        store=store,
        user_id=current_user.user_id,
        request_context=chatkit_req.metadata,
    )

    # Get response stream
    events = server.respond(thread, input_message, context)

    # Wrap in StreamingResult and return as SSE
    result = StreamingResult(events)
    return StreamingResponse(
        result.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
