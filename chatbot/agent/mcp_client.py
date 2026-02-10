"""
MCP Client wrapper.

Provides async interface to invoke MCP tools with error handling and timeout support.
"""

import asyncio
from typing import Any, Dict, Optional
from uuid import UUID

import httpx

from chatbot.agent.config import get_settings
from chatbot.agent.models.error import ErrorRecord
from chatbot.agent.models.invocation import InvocationStatus, ToolInvocation


class MCPClientError(Exception):
    """Base exception for MCP client errors."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def to_error_record(self) -> ErrorRecord:
        """Convert to ErrorRecord."""
        return ErrorRecord.from_mcp_error(
            code=self.code,
            message=self.message,
            details=self.details,
        )


class MCPConnectionError(MCPClientError):
    """Raised when unable to connect to MCP server."""

    def __init__(self, message: str = "Unable to connect to MCP server"):
        super().__init__(
            code="CONNECTION_ERROR",
            message=message,
            details=None,
        )


class MCPTimeoutError(MCPClientError):
    """Raised when MCP tool invocation times out."""

    def __init__(self, tool_name: str, timeout_seconds: int):
        super().__init__(
            code="TIMEOUT",
            message=f"Tool '{tool_name}' timed out after {timeout_seconds} seconds",
            details={"tool_name": tool_name, "timeout_seconds": timeout_seconds},
        )


class MCPClient:
    """
    Client for invoking MCP tools.

    Handles connection management, timeouts, and error translation.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ):
        settings = get_settings()
        self.base_url = base_url or settings.mcp_server_url
        self.timeout_seconds = timeout_seconds or settings.mcp_timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout_seconds),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def call_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        session_id: Optional[UUID] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Invoke an MCP tool.

        Args:
            tool_name: Name of the MCP tool to invoke
            params: Parameters to pass to the tool
            session_id: Session ID for audit logging
            user_id: User ID for audit logging

        Returns:
            Tool response data

        Raises:
            MCPConnectionError: If unable to connect
            MCPTimeoutError: If tool invocation times out
            MCPClientError: For other MCP errors
        """
        if self._client is None:
            raise RuntimeError("MCPClient must be used as async context manager")

        # Create invocation record for audit
        invocation = None
        if session_id and user_id:
            invocation = ToolInvocation(
                session_id=session_id,
                tool_name=tool_name,
                params=params,
                user_id=user_id,
            )

        try:
            # Call the MCP tool endpoint
            response = await self._client.post(
                f"/tools/{tool_name}",
                json=params,
            )

            # Parse response
            data = response.json()

            # Check for MCP-level errors
            if not data.get("success", False):
                error = data.get("error", {})
                error_code = error.get("code", "INTERNAL_ERROR")
                error_message = error.get("message", "Unknown error")
                error_details = error.get("details")

                if invocation:
                    invocation.complete_error({"error": error})

                raise MCPClientError(
                    code=error_code,
                    message=error_message,
                    details=error_details,
                )

            if invocation:
                invocation.complete_success(data)

            return data

        except httpx.ConnectError as e:
            if invocation:
                invocation.complete_error({
                    "error": {"code": "CONNECTION_ERROR", "message": str(e)}
                })
            raise MCPConnectionError() from e

        except httpx.TimeoutException as e:
            if invocation:
                invocation.complete_timeout()
            raise MCPTimeoutError(tool_name, self.timeout_seconds) from e

        except httpx.HTTPStatusError as e:
            if invocation:
                invocation.complete_error({
                    "error": {"code": "HTTP_ERROR", "message": str(e)}
                })
            raise MCPClientError(
                code="HTTP_ERROR",
                message=f"HTTP error: {e.response.status_code}",
                details={"status_code": e.response.status_code},
            ) from e


async def invoke_mcp_tool(
    tool_name: str,
    params: Dict[str, Any],
    session_id: Optional[UUID] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to invoke an MCP tool.

    Creates a client, invokes the tool, and returns the result.

    Args:
        tool_name: Name of the MCP tool
        params: Tool parameters
        session_id: Session ID for audit
        user_id: User ID for audit

    Returns:
        Tool response data
    """
    async with MCPClient() as client:
        return await client.call_tool(
            tool_name=tool_name,
            params=params,
            session_id=session_id,
            user_id=user_id,
        )
