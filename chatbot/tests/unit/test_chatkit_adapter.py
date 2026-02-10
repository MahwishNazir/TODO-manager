"""
Unit tests for ChatKit Streaming Adapter (T003).

Tests request parsing, SSE formatting, and streaming utilities.
"""

import json
import pytest
from chatbot.chatkit.adapter import (
    ChatKitRequest,
    parse_chatkit_request,
    format_sse_event,
    stream_sse_events,
    StreamingResult,
    JsonResult,
)


class TestChatKitRequest:
    """Tests for ChatKitRequest dataclass."""

    def test_defaults(self):
        req = ChatKitRequest(thread_id="t1", message_content="hi")
        assert req.message_type == "user_message"
        assert req.metadata == {}

    def test_custom_values(self):
        req = ChatKitRequest(
            thread_id="t1",
            message_content="hi",
            message_type="system",
            metadata={"key": "val"},
        )
        assert req.message_type == "system"
        assert req.metadata == {"key": "val"}

    def test_none_metadata_defaults(self):
        req = ChatKitRequest(thread_id="t1", message_content="hi", metadata=None)
        assert req.metadata == {}


class TestParseRequest:
    """Tests for parse_chatkit_request."""

    def test_valid_request(self):
        body = json.dumps({
            "thread_id": "t1",
            "message": {"type": "user_message", "content": "hello"},
            "metadata": {"source": "web"},
        }).encode()
        req = parse_chatkit_request(body)
        assert req.thread_id == "t1"
        assert req.message_content == "hello"
        assert req.message_type == "user_message"
        assert req.metadata == {"source": "web"}

    def test_missing_thread_id(self):
        body = json.dumps({"message": {"content": "hello"}}).encode()
        with pytest.raises(ValueError, match="Missing thread_id"):
            parse_chatkit_request(body)

    def test_invalid_json(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_chatkit_request(b"not json")

    def test_minimal_request(self):
        body = json.dumps({"thread_id": "t1"}).encode()
        req = parse_chatkit_request(body)
        assert req.thread_id == "t1"
        assert req.message_content is None

    def test_empty_message(self):
        body = json.dumps({"thread_id": "t1", "message": {}}).encode()
        req = parse_chatkit_request(body)
        assert req.message_content is None
        assert req.message_type == "user_message"


class TestFormatSSE:
    """Tests for format_sse_event."""

    @pytest.mark.asyncio
    async def test_text_delta_event(self):
        event = {"event": "text_delta", "data": {"text": "Hello"}}
        result = await format_sse_event(event)
        assert "event: text_delta" in result
        assert '"text": "Hello"' in result
        assert result.endswith("\n\n")

    @pytest.mark.asyncio
    async def test_error_event(self):
        event = {"event": "error", "data": {"code": "ERR", "message": "fail"}}
        result = await format_sse_event(event)
        assert "event: error" in result

    @pytest.mark.asyncio
    async def test_default_event_type(self):
        event = {"data": {"text": "hi"}}
        result = await format_sse_event(event)
        assert "event: message" in result

    @pytest.mark.asyncio
    async def test_empty_data(self):
        event = {"event": "done", "data": {}}
        result = await format_sse_event(event)
        assert "event: done" in result
        assert "data: {}" in result


class TestStreamSSE:
    """Tests for stream_sse_events."""

    @pytest.mark.asyncio
    async def test_streams_multiple_events(self):
        async def event_gen():
            yield {"event": "text_delta", "data": {"text": "Hi"}}
            yield {"event": "done", "data": {}}

        results = []
        async for sse in stream_sse_events(event_gen()):
            results.append(sse)
        assert len(results) == 2
        assert "text_delta" in results[0]
        assert "done" in results[1]

    @pytest.mark.asyncio
    async def test_empty_stream(self):
        async def empty_gen():
            return
            yield  # noqa: unreachable

        results = []
        async for sse in stream_sse_events(empty_gen()):
            results.append(sse)
        assert len(results) == 0


class TestStreamingResult:
    """Tests for StreamingResult."""

    @pytest.mark.asyncio
    async def test_stream(self):
        async def event_gen():
            yield {"event": "text_delta", "data": {"text": "Hello"}}
            yield {"event": "done", "data": {}}

        result = StreamingResult(event_gen())
        chunks = []
        async for chunk in result:
            chunks.append(chunk)
        assert len(chunks) == 2
        assert "Hello" in chunks[0]


class TestJsonResult:
    """Tests for JsonResult."""

    def test_json_output(self):
        result = JsonResult({"status": "ok"})
        assert json.loads(result.json) == {"status": "ok"}

    def test_data_property(self):
        data = {"status": "ok", "count": 42}
        result = JsonResult(data)
        assert result.data == data
