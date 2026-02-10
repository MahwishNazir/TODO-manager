"""
Unit tests for TodoChatKitServer (T002).

Tests server initialization, thread management, input conversion,
and streaming response handling.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from chatbot.chatkit.store import MemoryStore, Thread, ThreadItem
from chatbot.chatkit.server import TodoChatKitServer, AgentContext


class TestTodoChatKitServer:
    """Unit tests for TodoChatKitServer."""

    @pytest.fixture
    def store(self):
        return MemoryStore()

    @pytest.fixture
    def server(self, store):
        with patch("chatbot.chatkit.server.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                agent_model="gpt-4",
                agent_temperature=0.0,
                agent_max_tokens=4096,
            )
            return TodoChatKitServer(store=store)

    def test_server_initialization(self, server):
        assert server._store is not None
        assert server._agent is None

    def test_agent_lazy_initialization(self, server):
        with patch("chatbot.chatkit.server.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            agent = server.agent
            assert agent is not None
            MockAgent.assert_called_once()
            agent2 = server.agent
            assert agent is agent2

    @pytest.mark.asyncio
    async def test_get_or_create_thread_new(self, server, store):
        thread = await server.get_or_create_thread("t1", "user1")
        assert thread.id == "t1"
        assert thread.metadata["user_id"] == "user1"
        loaded = await store.load_thread("t1")
        assert loaded is not None

    @pytest.mark.asyncio
    async def test_get_or_create_thread_existing(self, server, store):
        existing = Thread(id="t1", metadata={"user_id": "user1"})
        await store.save_thread(existing)
        thread = await server.get_or_create_thread("t1", "user1")
        assert thread.id == "t1"

    def test_convert_items_to_agent_input(self, server):
        items = [
            ThreadItem(id="1", thread_id="t1", type="user_message", content="hello"),
            ThreadItem(id="2", thread_id="t1", type="assistant_message", content="hi there"),
            ThreadItem(id="3", thread_id="t1", type="tool_call", content=None),
        ]
        result = server.convert_items_to_agent_input(items)
        assert len(result) == 2
        assert result[0] == {"role": "user", "content": "hello"}
        assert result[1] == {"role": "assistant", "content": "hi there"}

    def test_convert_items_empty_content_skipped(self, server):
        items = [
            ThreadItem(id="1", thread_id="t1", type="user_message", content=None),
            ThreadItem(id="2", thread_id="t1", type="user_message", content=""),
        ]
        result = server.convert_items_to_agent_input(items)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_respond_empty_input(self, server, store):
        thread = Thread(id="t1", metadata={})
        await store.save_thread(thread)
        context = AgentContext(thread=thread, store=store, user_id="user1")
        events = []
        async for event in server.respond(thread, None, context):
            events.append(event)
        assert any(e["event"] == "error" for e in events)
        assert any(e["event"] == "done" for e in events)

    @pytest.mark.asyncio
    async def test_respond_streams_text_events(self, server, store):
        thread = Thread(id="t1", metadata={})
        await store.save_thread(thread)
        user_msg = ThreadItem(id="m1", thread_id="t1", type="user_message", content="hello")
        context = AgentContext(thread=thread, store=store, user_id="user1")

        mock_event = MagicMock()
        mock_event.type = "raw_response_event"
        mock_delta = MagicMock()
        mock_delta.content = "Hello!"
        mock_event.data = MagicMock()
        mock_event.data.delta = mock_delta

        async def fake_stream():
            yield mock_event

        mock_result = MagicMock()
        mock_result.stream_events = MagicMock(return_value=fake_stream())

        with patch("chatbot.chatkit.server.Runner") as MockRunner:
            MockRunner.run_streamed.return_value = mock_result
            events = []
            async for event in server.respond(thread, user_msg, context):
                events.append(event)

        assert any(e["event"] == "text_delta" for e in events)
        text_event = next(e for e in events if e["event"] == "text_delta")
        assert text_event["data"]["text"] == "Hello!"
        assert any(e["event"] == "done" for e in events)

    @pytest.mark.asyncio
    async def test_respond_handles_error(self, server, store):
        thread = Thread(id="t1", metadata={})
        await store.save_thread(thread)
        user_msg = ThreadItem(id="m1", thread_id="t1", type="user_message", content="hello")
        context = AgentContext(thread=thread, store=store, user_id="user1")

        with patch("chatbot.chatkit.server.Runner") as MockRunner:
            MockRunner.run_streamed.side_effect = Exception("Agent failed")
            events = []
            async for event in server.respond(thread, user_msg, context):
                events.append(event)

        error_events = [e for e in events if e["event"] == "error"]
        assert len(error_events) == 1
        assert "Agent failed" in error_events[0]["data"]["message"]
        assert any(e["event"] == "done" for e in events)

    @pytest.mark.asyncio
    async def test_respond_saves_assistant_message(self, server, store):
        thread = Thread(id="t1", metadata={})
        await store.save_thread(thread)
        user_msg = ThreadItem(id="m1", thread_id="t1", type="user_message", content="hello")
        context = AgentContext(thread=thread, store=store, user_id="user1")

        mock_event = MagicMock()
        mock_event.type = "raw_response_event"
        mock_delta = MagicMock()
        mock_delta.content = "Response"
        mock_event.data = MagicMock()
        mock_event.data.delta = mock_delta

        async def fake_stream():
            yield mock_event

        mock_result = MagicMock()
        mock_result.stream_events = MagicMock(return_value=fake_stream())

        with patch("chatbot.chatkit.server.Runner") as MockRunner:
            MockRunner.run_streamed.return_value = mock_result
            async for _ in server.respond(thread, user_msg, context):
                pass

        page = await store.load_thread_items("t1")
        assistant_items = [i for i in page.data if i.type == "assistant_message"]
        assert len(assistant_items) == 1
        assert assistant_items[0].content == "Response"
