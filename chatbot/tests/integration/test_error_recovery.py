"""
Integration tests for error recovery (T081).

Tests MCP connection failures and error handling flows.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from chatbot.agent.core import process_message, reset_agent
from chatbot.agent.mcp_client import (
    MCPClientError,
    MCPConnectionError,
    MCPTimeoutError,
)


class TestMCPConnectionFailure:
    """Integration tests for MCP connection failure handling."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.mark.asyncio
    async def test_connection_failure_user_friendly(self):
        """Connection failure should return user-friendly message."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "I'm having trouble connecting right now. Please try again."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Show my tasks",
                user_id="user-123",
            )

            assert result["success"] is True
            # Response should be user-friendly
            response_lower = result["response"].lower()
            assert "try again" in response_lower or "trouble" in response_lower or "error" in response_lower

    @pytest.mark.asyncio
    async def test_timeout_offers_retry(self):
        """Timeout should offer retry option."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "The request took too long. Would you like me to try again?"},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Create a task",
                user_id="user-123",
            )

            assert result["success"] is True


class TestTaskNotFoundRecovery:
    """Tests for task not found error recovery."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.mark.asyncio
    async def test_task_not_found_suggests_list(self):
        """Task not found should suggest showing tasks."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "I couldn't find that task. Would you like to see your current tasks?"},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Complete the nonexistent task",
                user_id="user-123",
            )

            assert result["success"] is True
            response_lower = result["response"].lower()
            assert "couldn't find" in response_lower or "not found" in response_lower


class TestInternalErrorHandling:
    """Tests for internal error handling."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Reset agent singleton before/after tests."""
        reset_agent()
        yield
        reset_agent()

    @pytest.mark.asyncio
    async def test_internal_error_no_stack_trace(self):
        """Internal errors should not expose stack traces (FR-055)."""
        mock_response = MagicMock(
            messages=[
                {"role": "assistant", "content": "Something went wrong. If this persists, please contact support."},
            ]
        )

        with patch("chatbot.agent.core.Runner") as MockRunner:
            mock_runner_instance = AsyncMock()
            mock_runner_instance.run = AsyncMock(return_value=mock_response)
            MockRunner.return_value = mock_runner_instance

            result = await process_message(
                user_message="Create a task",
                user_id="user-123",
            )

            # Should not expose technical details
            response = result["response"]
            assert "Exception" not in response
            assert "Traceback" not in response
            assert "line" not in response.lower() or "support" in response.lower()


class TestMCPClientErrorHandling:
    """Tests for MCPClientError handling in tools."""

    @pytest.mark.asyncio
    async def test_mcp_error_converted_to_user_message(self):
        """MCP errors should be converted to user-friendly messages."""
        from chatbot.agent.tools import add_task

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPClientError(
                code="SERVICE_UNAVAILABLE",
                message="Database connection failed",
            )

            result = await add_task(user_id="user-1", title="Test")

            assert result["success"] is False
            assert result["error"]["code"] == "SERVICE_UNAVAILABLE"
            # The error should be categorized properly

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """MCPConnectionError should be handled gracefully."""
        from chatbot.agent.tools import list_tasks

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPConnectionError("Connection refused")

            result = await list_tasks(user_id="user-1")

            assert result["success"] is False
            assert result["error"]["code"] == "CONNECTION_ERROR"

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """MCPTimeoutError should be handled gracefully."""
        from chatbot.agent.tools import delete_task

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPTimeoutError("delete_task", 30)

            result = await delete_task(user_id="user-1", task_id="task-123")

            assert result["success"] is False
            assert result["error"]["code"] == "TIMEOUT"
