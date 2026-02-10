"""
Unit tests for list_tasks tool bridge (T037).

Tests the list_tasks function with mocked MCP client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from chatbot.agent.tools import list_tasks, set_tool_context, clear_tool_context


class TestListTasksTool:
    """Tests for list_tasks tool function."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Clear tool context before and after each test."""
        clear_tool_context()
        yield
        clear_tool_context()

    @pytest.mark.asyncio
    async def test_list_tasks_all(self):
        """Should list all tasks."""
        mock_result = {
            "success": True,
            "data": {
                "tasks": [
                    {"id": "t1", "title": "Task 1", "status": "pending"},
                    {"id": "t2", "title": "Task 2", "status": "completed"},
                ],
                "total_count": 2,
                "has_more": False,
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await list_tasks(user_id="user-1")

            assert result["success"] is True
            assert len(result["data"]["tasks"]) == 2
            mock_invoke.assert_called_once()
            call_args = mock_invoke.call_args
            assert call_args.kwargs["tool_name"] == "list_tasks"

    @pytest.mark.asyncio
    async def test_list_tasks_with_status_filter(self):
        """Should filter tasks by status."""
        mock_result = {
            "success": True,
            "data": {
                "tasks": [
                    {"id": "t1", "title": "Task 1", "status": "pending"},
                ],
                "total_count": 1,
                "has_more": False,
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await list_tasks(user_id="user-1", status="pending")

            assert result["success"] is True
            call_args = mock_invoke.call_args
            assert call_args.kwargs["params"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_tasks_with_pagination(self):
        """Should support pagination."""
        mock_result = {
            "success": True,
            "data": {
                "tasks": [{"id": "t1", "title": "Task 1"}],
                "total_count": 50,
                "has_more": True,
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await list_tasks(
                user_id="user-1",
                limit=10,
                offset=0,
            )

            assert result["success"] is True
            assert result["data"]["has_more"] is True
            call_args = mock_invoke.call_args
            assert call_args.kwargs["params"]["limit"] == 10
            assert call_args.kwargs["params"]["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_empty_result(self):
        """Should handle empty task list."""
        mock_result = {
            "success": True,
            "data": {
                "tasks": [],
                "total_count": 0,
                "has_more": False,
            }
        }

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await list_tasks(user_id="user-1")

            assert result["success"] is True
            assert len(result["data"]["tasks"]) == 0

    @pytest.mark.asyncio
    async def test_list_tasks_with_tool_context(self):
        """Should pass session/user context for audit."""
        session_id = uuid4()
        set_tool_context(session_id=session_id, user_id="user-1")

        mock_result = {"success": True, "data": {"tasks": [], "total_count": 0}}

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            await list_tasks(user_id="user-1")

            call_args = mock_invoke.call_args
            assert call_args.kwargs["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_list_tasks_validates_status(self):
        """Should validate status parameter."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            await list_tasks(user_id="user-1", status="invalid_status")

    @pytest.mark.asyncio
    async def test_list_tasks_validates_limit_range(self):
        """Should validate limit is within range."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            await list_tasks(user_id="user-1", limit=200)  # Max is 100
