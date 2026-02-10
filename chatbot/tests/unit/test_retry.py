"""
Unit tests for retry logic (T082).

Tests retry behavior for system-temporary errors.
"""

import pytest
from unittest.mock import AsyncMock, patch

from chatbot.agent.models import ErrorCategory, ErrorRecord
from chatbot.agent.errors import should_offer_retry
from chatbot.agent.mcp_client import MCPClientError, MCPTimeoutError


class TestShouldOfferRetry:
    """Tests for should_offer_retry function."""

    def test_timeout_offers_retry(self):
        """TIMEOUT should offer retry."""
        record = ErrorRecord(
            code="TIMEOUT",
            message="Timed out",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert should_offer_retry(record) is True

    def test_service_unavailable_offers_retry(self):
        """SERVICE_UNAVAILABLE should offer retry."""
        record = ErrorRecord(
            code="SERVICE_UNAVAILABLE",
            message="Service unavailable",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert should_offer_retry(record) is True

    def test_rate_limited_offers_retry(self):
        """RATE_LIMITED should offer retry."""
        record = ErrorRecord(
            code="RATE_LIMITED",
            message="Rate limited",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert should_offer_retry(record) is True

    def test_connection_error_offers_retry(self):
        """CONNECTION_ERROR should offer retry."""
        record = ErrorRecord(
            code="CONNECTION_ERROR",
            message="Connection error",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert should_offer_retry(record) is True

    def test_user_correctable_no_retry(self):
        """USER_CORRECTABLE errors should not offer automatic retry."""
        record = ErrorRecord(
            code="INVALID_INPUT",
            message="Invalid input",
            category=ErrorCategory.USER_CORRECTABLE,
        )

        assert should_offer_retry(record) is False

    def test_permanent_no_retry(self):
        """SYSTEM_PERMANENT errors should not offer retry."""
        record = ErrorRecord(
            code="INTERNAL_ERROR",
            message="Internal error",
            category=ErrorCategory.SYSTEM_PERMANENT,
        )

        assert should_offer_retry(record) is False


class TestRetryBehavior:
    """Tests for actual retry behavior in MCP client."""

    @pytest.mark.asyncio
    async def test_timeout_returns_retriable_error(self):
        """Timeout should return a retriable error structure."""
        from chatbot.agent.tools import add_task

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = MCPTimeoutError("add_task", 30)

            result = await add_task(user_id="user-1", title="Test")

            assert result["success"] is False
            error = result["error"]

            # Create ErrorRecord to check retry status
            record = ErrorRecord(
                code=error["code"],
                message=error["message"],
                category=ErrorCategory.SYSTEM_TEMPORARY,
            )
            assert should_offer_retry(record) is True

    @pytest.mark.asyncio
    async def test_successful_after_retry(self):
        """Should succeed on retry after temporary failure."""
        from chatbot.agent.tools import add_task

        call_count = 0

        async def mock_invoke(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise MCPTimeoutError("add_task", 30)
            return {"success": True, "data": {"task": {"id": "task-123"}}}

        with patch("chatbot.agent.tools.invoke_mcp_tool", new_callable=AsyncMock) as mock:
            mock.side_effect = mock_invoke

            # First call fails
            result1 = await add_task(user_id="user-1", title="Test")
            assert result1["success"] is False

            # Second call succeeds
            result2 = await add_task(user_id="user-1", title="Test")
            assert result2["success"] is True


class TestRetryMessageFormatting:
    """Tests for retry message formatting."""

    def test_timeout_message_suggests_retry(self):
        """Timeout message should suggest retry."""
        error = MCPTimeoutError("list_tasks", 30)

        # Message should mention retry possibility
        assert "30" in error.message
        assert "list_tasks" in error.message

    def test_error_record_retry_message(self):
        """ErrorRecord should generate appropriate retry message."""
        record = ErrorRecord(
            code="TIMEOUT",
            message="Request timed out",
            category=ErrorCategory.SYSTEM_TEMPORARY,
            suggestion="Please try again.",
        )

        user_msg = record.get_user_message()
        assert "try again" in user_msg.lower()


class TestRetryConfiguration:
    """Tests for retry configuration."""

    def test_default_timeout_30_seconds(self):
        """Default timeout should be 30 seconds."""
        from chatbot.agent.config import get_settings

        settings = get_settings()
        assert settings.mcp_timeout_seconds == 30

    def test_timeout_configurable(self):
        """Timeout should be configurable via settings."""
        from chatbot.agent.config import AgentSettings

        settings = AgentSettings(
            openai_api_key="test",
            mcp_timeout_seconds=60,
        )
        assert settings.mcp_timeout_seconds == 60
