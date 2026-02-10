"""
Unit tests for update_task tool bridge (T046).

Tests the update_task function with mocked MCP client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from chatbot.agent.tools import update_task, set_tool_context, clear_tool_context
from chatbot.agent.mcp_client import MCPClientError


class TestUpdateTaskTool:
    """Tests for update_task tool function."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Clear tool context before and after each test."""
        clear_tool_context()
        yield
        clear_tool_context()

    @pytest.mark.asyncio
    async def test_update_task_title(self):
        """Should update task title."""
        mock_result = {
            "success": True,
            "data": {
                "task": {
                    "id": "task-123",
                    "title": "Updated title",
                    "description": "Original description",
                }
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await update_task(
                user_id="user-1",
                task_id="task-123",
                title="Updated title",
            )

            assert result["success"] is True
            call_args = mock_invoke.call_args
            assert call_args.kwargs["tool_name"] == "update_task"
            assert call_args.kwargs["params"]["title"] == "Updated title"

    @pytest.mark.asyncio
    async def test_update_task_description(self):
        """Should update task description."""
        mock_result = {
            "success": True,
            "data": {"task": {"id": "task-123", "description": "New description"}}
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await update_task(
                user_id="user-1",
                task_id="task-123",
                description="New description",
            )

            assert result["success"] is True
            call_args = mock_invoke.call_args
            assert call_args.kwargs["params"]["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_task_multiple_fields(self):
        """Should update multiple fields at once."""
        mock_result = {
            "success": True,
            "data": {
                "task": {
                    "id": "task-123",
                    "title": "New title",
                    "description": "New description",
                }
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await update_task(
                user_id="user-1",
                task_id="task-123",
                title="New title",
                description="New description",
            )

            assert result["success"] is True
            call_args = mock_invoke.call_args
            assert call_args.kwargs["params"]["title"] == "New title"
            assert call_args.kwargs["params"]["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_task_not_found(self):
        """Should handle task not found error."""
        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPClientError(
                code="TASK_NOT_FOUND",
                message="Task not found",
                details={"task_id": "nonexistent"},
            )

            result = await update_task(
                user_id="user-1",
                task_id="nonexistent",
                title="New title",
            )

            assert result["success"] is False
            assert result["error"]["code"] == "TASK_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_update_task_no_fields_error(self):
        """Should reject update with no fields to change."""
        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPClientError(
                code="NO_FIELDS_TO_UPDATE",
                message="At least one field must be provided",
            )

            result = await update_task(
                user_id="user-1",
                task_id="task-123",
                # No title or description provided
            )

            assert result["success"] is False
            assert result["error"]["code"] == "NO_FIELDS_TO_UPDATE"

    @pytest.mark.asyncio
    async def test_update_task_with_tool_context(self):
        """Should pass session/user context for audit."""
        session_id = uuid4()
        set_tool_context(session_id=session_id, user_id="user-1")

        mock_result = {"success": True, "data": {"task": {"id": "task-123"}}}

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            await update_task(
                user_id="user-1",
                task_id="task-123",
                title="Updated",
            )

            call_args = mock_invoke.call_args
            assert call_args.kwargs["session_id"] == session_id
