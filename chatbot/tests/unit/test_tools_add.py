"""
Unit tests for add_task tool bridge (T028).

Tests the add_task function with mocked MCP client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from chatbot.agent.tools import (
    add_task,
    set_tool_context,
    clear_tool_context,
    get_tool_context,
)
from chatbot.agent.mcp_client import MCPClientError


class TestAddTaskTool:
    """Tests for add_task tool function."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Clear tool context before and after each test."""
        clear_tool_context()
        yield
        clear_tool_context()

    @pytest.mark.asyncio
    async def test_add_task_success(self):
        """Should create task successfully."""
        mock_result = {
            "success": True,
            "data": {
                "task": {
                    "id": "task-123",
                    "user_id": "user-1",
                    "title": "Buy groceries",
                    "description": "Get milk and bread",
                    "status": "pending",
                }
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await add_task(
                user_id="user-1",
                title="Buy groceries",
                description="Get milk and bread",
            )

            assert result["success"] is True
            assert result["data"]["task"]["id"] == "task-123"
            mock_invoke.assert_called_once()
            call_args = mock_invoke.call_args
            assert call_args.kwargs["tool_name"] == "add_task"
            assert call_args.kwargs["params"]["title"] == "Buy groceries"

    @pytest.mark.asyncio
    async def test_add_task_without_description(self):
        """Should create task without description."""
        mock_result = {
            "success": True,
            "data": {"task": {"id": "task-456", "title": "Simple task"}}
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await add_task(
                user_id="user-1",
                title="Simple task",
            )

            assert result["success"] is True
            # Description should be excluded from params when None
            call_args = mock_invoke.call_args
            assert "description" not in call_args.kwargs["params"]

    @pytest.mark.asyncio
    async def test_add_task_with_tool_context(self):
        """Should pass session/user context for audit."""
        session_id = uuid4()
        set_tool_context(session_id=session_id, user_id="user-1")

        mock_result = {"success": True, "data": {"task": {"id": "task-789"}}}

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            await add_task(user_id="user-1", title="Test task")

            call_args = mock_invoke.call_args
            assert call_args.kwargs["session_id"] == session_id
            assert call_args.kwargs["user_id"] == "user-1"

    @pytest.mark.asyncio
    async def test_add_task_mcp_error(self):
        """Should handle MCP errors gracefully."""
        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPClientError(
                code="INVALID_INPUT",
                message="Title is required",
                details={"field": "title"},
            )

            result = await add_task(user_id="user-1", title="")

            assert result["success"] is False
            assert result["error"]["code"] == "INVALID_INPUT"
            assert result["error"]["message"] == "Title is required"

    @pytest.mark.asyncio
    async def test_add_task_validates_title_length(self):
        """Should validate title length constraints."""
        # Test with very long title (>500 chars)
        long_title = "A" * 600

        # The Pydantic schema should reject this
        with pytest.raises(Exception):  # Pydantic ValidationError
            await add_task(user_id="user-1", title=long_title)

    @pytest.mark.asyncio
    async def test_add_task_validates_empty_title(self):
        """Should reject empty title."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            await add_task(user_id="user-1", title="")


class TestToolContext:
    """Tests for tool context management."""

    def test_set_and_get_context(self):
        """Should set and retrieve context."""
        clear_tool_context()
        session_id = uuid4()

        set_tool_context(session_id=session_id, user_id="user-123")
        ctx = get_tool_context()

        assert ctx["session_id"] == session_id
        assert ctx["user_id"] == "user-123"

    def test_clear_context(self):
        """Should clear context."""
        set_tool_context(session_id=uuid4(), user_id="user-1")
        clear_tool_context()

        ctx = get_tool_context()
        assert ctx == {}

    def test_get_context_returns_copy(self):
        """Should return a copy, not the original."""
        set_tool_context(session_id=uuid4(), user_id="user-1")
        ctx = get_tool_context()

        # Modifying the copy should not affect the original
        ctx["extra"] = "value"
        original = get_tool_context()

        assert "extra" not in original
