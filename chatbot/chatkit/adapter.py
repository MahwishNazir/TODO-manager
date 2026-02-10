"""
ChatKit Streaming Adapter (T003).

Converts between ChatKit protocol and OpenAI Agents SDK streaming formats.
Provides utilities for request/response transformation.
"""

import json
from typing import Any, AsyncIterator, Optional
from dataclasses import dataclass


@dataclass
class ChatKitRequest:
    """
    Parsed ChatKit request.

    Represents the incoming request from ChatKit frontend.
    """

    thread_id: str
    message_content: Optional[str]
    message_type: str = "user_message"
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def parse_chatkit_request(body: bytes) -> ChatKitRequest:
    """
    Parse ChatKit request body.

    Args:
        body: Raw request body bytes

    Returns:
        ChatKitRequest object

    Raises:
        ValueError: If request is malformed
    """
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    thread_id = data.get("thread_id")
    if not thread_id:
        raise ValueError("Missing thread_id")

    message = data.get("message", {})
    message_content = message.get("content")
    message_type = message.get("type", "user_message")
    metadata = data.get("metadata", {})

    return ChatKitRequest(
        thread_id=thread_id,
        message_content=message_content,
        message_type=message_type,
        metadata=metadata,
    )


async def format_sse_event(event: dict[str, Any]) -> str:
    """
    Format an event as Server-Sent Events data.

    Args:
        event: Event dictionary with 'event' and 'data' keys

    Returns:
        SSE-formatted string
    """
    event_type = event.get("event", "message")
    event_data = event.get("data", {})

    return f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"


async def stream_sse_events(
    events: AsyncIterator[dict[str, Any]],
) -> AsyncIterator[str]:
    """
    Convert event stream to SSE format.

    Args:
        events: Async iterator of event dictionaries

    Yields:
        SSE-formatted strings
    """
    async for event in events:
        yield await format_sse_event(event)


class StreamingResult:
    """
    Wrapper for streaming response.

    Provides an async iterator interface for SSE streaming.
    """

    def __init__(self, events: AsyncIterator[dict[str, Any]]):
        self._events = events

    async def stream(self) -> AsyncIterator[str]:
        """
        Stream events as SSE-formatted strings.

        Yields:
            SSE-formatted event strings
        """
        async for event in self._events:
            yield await format_sse_event(event)

    def __aiter__(self):
        return self.stream()


class JsonResult:
    """
    Wrapper for non-streaming JSON response.
    """

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def json(self) -> str:
        """Get JSON string representation."""
        return json.dumps(self._data)

    @property
    def data(self) -> dict[str, Any]:
        """Get raw data dictionary."""
        return self._data
