"""
Unit tests for MCP client wrapper (T025).

Tests MCP client functionality with mocked HTTP responses.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import httpx

from chatbot.agent.mcp_client import (
    MCPClient,
    MCPClientError,
    MCPConnectionError,
    MCPTimeoutError,
    invoke_mcp_tool,
)


class TestMCPClient:
    """Tests for MCPClient class."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock httpx client."""
        client = AsyncMock(spec=httpx.AsyncClient)
        return client

    @pytest.mark.asyncio
    async def test_call_tool_success(self, mock_httpx_client):
        """Successful tool call should return data."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {"task_id": "task-123"},
        }
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        with patch("chatbot.agent.mcp_client.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_httpx_client
            MockClient.return_value.__aexit__.return_value = None

            async with MCPClient() as client:
                client._client = mock_httpx_client
                result = await client.call_tool(
                    tool_name="add_task",
                    params={"title": "Test"},
                )

            assert result["success"] is True
            assert result["data"]["task_id"] == "task-123"

    @pytest.mark.asyncio
    async def test_call_tool_mcp_error(self, mock_httpx_client):
        """MCP errors should raise MCPClientError."""
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "error": {
                "code": "TASK_NOT_FOUND",
                "message": "Task not found",
                "details": {"task_id": "xyz"},
            },
        }
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        with patch("chatbot.agent.mcp_client.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_httpx_client
            MockClient.return_value.__aexit__.return_value = None

            async with MCPClient() as client:
                client._client = mock_httpx_client
                with pytest.raises(MCPClientError) as exc_info:
                    await client.call_tool(
                        tool_name="delete_task",
                        params={"task_id": "xyz"},
                    )

            assert exc_info.value.code == "TASK_NOT_FOUND"
            assert "Task not found" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_call_tool_connection_error(self, mock_httpx_client):
        """Connection errors should raise MCPConnectionError."""
        mock_httpx_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        with patch("chatbot.agent.mcp_client.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_httpx_client
            MockClient.return_value.__aexit__.return_value = None

            async with MCPClient() as client:
                client._client = mock_httpx_client
                with pytest.raises(MCPConnectionError):
                    await client.call_tool(
                        tool_name="list_tasks",
                        params={},
                    )

    @pytest.mark.asyncio
    async def test_call_tool_timeout(self, mock_httpx_client):
        """Timeout should raise MCPTimeoutError."""
        mock_httpx_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with patch("chatbot.agent.mcp_client.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_httpx_client
            MockClient.return_value.__aexit__.return_value = None

            async with MCPClient(timeout_seconds=30) as client:
                client._client = mock_httpx_client
                with pytest.raises(MCPTimeoutError) as exc_info:
                    await client.call_tool(
                        tool_name="list_tasks",
                        params={},
                    )

            assert exc_info.value.code == "TIMEOUT"
            assert "30" in str(exc_info.value.details)

    @pytest.mark.asyncio
    async def test_call_tool_without_context_manager(self):
        """Calling without context manager should raise error."""
        client = MCPClient()

        with pytest.raises(RuntimeError, match="context manager"):
            await client.call_tool(
                tool_name="add_task",
                params={},
            )

    @pytest.mark.asyncio
    async def test_call_tool_with_audit_context(self, mock_httpx_client):
        """Tool calls with session/user ID should create invocation record."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {"task_id": "task-123"},
        }
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        session_id = uuid4()
        user_id = "user-123"

        with patch("chatbot.agent.mcp_client.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_httpx_client
            MockClient.return_value.__aexit__.return_value = None

            async with MCPClient() as client:
                client._client = mock_httpx_client
                result = await client.call_tool(
                    tool_name="add_task",
                    params={"title": "Test"},
                    session_id=session_id,
                    user_id=user_id,
                )

            assert result["success"] is True


class TestMCPClientError:
    """Tests for MCPClientError exception."""

    def test_error_attributes(self):
        """Error should have code, message, and details."""
        error = MCPClientError(
            code="INVALID_INPUT",
            message="Title is required",
            details={"field": "title"},
        )

        assert error.code == "INVALID_INPUT"
        assert error.message == "Title is required"
        assert error.details == {"field": "title"}

    def test_to_error_record(self):
        """to_error_record should create ErrorRecord."""
        error = MCPClientError(
            code="TASK_NOT_FOUND",
            message="Task not found",
        )

        record = error.to_error_record()

        assert record.code == "TASK_NOT_FOUND"
        assert record.message == "Task not found"


class TestMCPConnectionError:
    """Tests for MCPConnectionError."""

    def test_default_message(self):
        """Should have default message."""
        error = MCPConnectionError()

        assert error.code == "CONNECTION_ERROR"
        assert "connect" in error.message.lower()

    def test_custom_message(self):
        """Should accept custom message."""
        error = MCPConnectionError("Server unreachable")

        assert error.message == "Server unreachable"


class TestMCPTimeoutError:
    """Tests for MCPTimeoutError."""

    def test_timeout_details(self):
        """Should include tool name and timeout in details."""
        error = MCPTimeoutError(tool_name="list_tasks", timeout_seconds=30)

        assert error.code == "TIMEOUT"
        assert "list_tasks" in error.message
        assert "30" in error.message
        assert error.details["tool_name"] == "list_tasks"
        assert error.details["timeout_seconds"] == 30


class TestInvokeMCPTool:
    """Tests for invoke_mcp_tool convenience function."""

    @pytest.mark.asyncio
    async def test_invoke_creates_client(self):
        """invoke_mcp_tool should create and use client."""
        with patch("chatbot.agent.mcp_client.MCPClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.call_tool = AsyncMock(return_value={
                "success": True,
                "data": {"task_id": "task-123"},
            })
            MockClient.return_value.__aenter__.return_value = mock_instance
            MockClient.return_value.__aexit__.return_value = None

            result = await invoke_mcp_tool(
                tool_name="add_task",
                params={"title": "Test"},
            )

            assert result["success"] is True
            mock_instance.call_tool.assert_called_once()
