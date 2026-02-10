"""
Unit tests for complete_task tool bridge (T047).

Tests the complete_task function with mocked MCP client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from chatbot.agent.tools import complete_task, set_tool_context, clear_tool_context
from chatbot.agent.mcp_client import MCPClientError


class TestCompleteTaskTool:
    """Tests for complete_task tool function."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Clear tool context before and after each test."""
        clear_tool_context()
        yield
        clear_tool_context()

    @pytest.mark.asyncio
    async def test_complete_task_success(self):
        """Should mark task as completed."""
        mock_result = {
            "success": True,
            "data": {
                "task": {
                    "id": "task-123",
                    "title": "Buy groceries",
                    "status": "completed",
                }
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await complete_task(
                user_id="user-1",
                task_id="task-123",
            )

            assert result["success"] is True
            assert result["data"]["task"]["status"] == "completed"
            call_args = mock_invoke.call_args
            assert call_args.kwargs["tool_name"] == "complete_task"
            assert call_args.kwargs["params"]["task_id"] == "task-123"

    @pytest.mark.asyncio
    async def test_complete_task_already_completed(self):
        """Should handle already completed task (idempotent)."""
        mock_result = {
            "success": True,
            "data": {
                "task": {
                    "id": "task-123",
                    "status": "completed",
                }
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await complete_task(
                user_id="user-1",
                task_id="task-123",
            )

            # Should succeed even if already completed
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self):
        """Should handle task not found error."""
        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPClientError(
                code="TASK_NOT_FOUND",
                message="Task not found",
                details={"task_id": "nonexistent"},
            )

            result = await complete_task(
                user_id="user-1",
                task_id="nonexistent",
            )

            assert result["success"] is False
            assert result["error"]["code"] == "TASK_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_complete_task_unauthorized(self):
        """Should handle unauthorized access."""
        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPClientError(
                code="UNAUTHORIZED",
                message="Not authorized to complete this task",
            )

            result = await complete_task(
                user_id="user-1",
                task_id="other-user-task",
            )

            assert result["success"] is False
            assert result["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_complete_task_with_tool_context(self):
        """Should pass session/user context for audit."""
        session_id = uuid4()
        set_tool_context(session_id=session_id, user_id="user-1")

        mock_result = {"success": True, "data": {"task": {"id": "task-123"}}}

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            await complete_task(user_id="user-1", task_id="task-123")

            call_args = mock_invoke.call_args
            assert call_args.kwargs["session_id"] == session_id
