"""
Unit tests for error category mapping (T080).

Tests error categorization and user-friendly message generation.
"""

import pytest

from chatbot.agent.models import ErrorCategory, ErrorRecord
from chatbot.agent.errors import (
    AgentError,
    categorize_error,
    get_user_friendly_message,
    should_offer_retry,
    should_escalate,
)


class TestErrorCategoryMapping:
    """Tests for error category mapping."""

    USER_CORRECTABLE_CODES = [
        "INVALID_INPUT",
        "TASK_NOT_FOUND",
        "UNAUTHORIZED",
        "NO_FIELDS_TO_UPDATE",
    ]

    SYSTEM_TEMPORARY_CODES = [
        "SERVICE_UNAVAILABLE",
        "TIMEOUT",
        "RATE_LIMITED",
        "CONNECTION_ERROR",
    ]

    SYSTEM_PERMANENT_CODES = [
        "INTERNAL_ERROR",
    ]

    @pytest.mark.parametrize("code", USER_CORRECTABLE_CODES)
    def test_user_correctable_mapping(self, code):
        """User-correctable codes should map correctly."""
        record = categorize_error(code=code, message="Test message")

        assert record.category == ErrorCategory.USER_CORRECTABLE

    @pytest.mark.parametrize("code", SYSTEM_TEMPORARY_CODES)
    def test_system_temporary_mapping(self, code):
        """System-temporary codes should map correctly."""
        record = categorize_error(code=code, message="Test message")

        assert record.category == ErrorCategory.SYSTEM_TEMPORARY

    @pytest.mark.parametrize("code", SYSTEM_PERMANENT_CODES)
    def test_system_permanent_mapping(self, code):
        """System-permanent codes should map correctly."""
        record = categorize_error(code=code, message="Test message")

        assert record.category == ErrorCategory.SYSTEM_PERMANENT

    def test_unknown_code_defaults_to_permanent(self):
        """Unknown codes should default to SYSTEM_PERMANENT."""
        record = categorize_error(code="UNKNOWN_CODE", message="Unknown error")

        assert record.category == ErrorCategory.SYSTEM_PERMANENT


class TestUserFriendlyMessages:
    """Tests for user-friendly message generation."""

    def test_user_correctable_shows_suggestion(self):
        """User-correctable errors should show helpful suggestion."""
        record = ErrorRecord(
            code="TASK_NOT_FOUND",
            message="Task abc123 not found in database",
            category=ErrorCategory.USER_CORRECTABLE,
            suggestion="The task could not be found. Would you like to see your current tasks?",
        )

        message = get_user_friendly_message(record)

        assert "task" in message.lower()
        assert "found" in message.lower() or "see" in message.lower()

    def test_system_temporary_suggests_retry(self):
        """System-temporary errors should suggest retry."""
        record = ErrorRecord(
            code="TIMEOUT",
            message="Request timed out after 30000ms",
            category=ErrorCategory.SYSTEM_TEMPORARY,
            suggestion="Please try again.",
        )

        message = get_user_friendly_message(record)

        assert "try again" in message.lower()

    def test_system_permanent_no_technical_details(self):
        """System-permanent errors should not expose technical details (FR-055)."""
        record = ErrorRecord(
            code="INTERNAL_ERROR",
            message="NullPointerException at TaskService.java:142",
            category=ErrorCategory.SYSTEM_PERMANENT,
        )

        message = get_user_friendly_message(record)

        # Should NOT contain technical details
        assert "NullPointer" not in message
        assert "java" not in message.lower()
        assert "142" not in message
        # Should have user-friendly message
        assert "went wrong" in message.lower() or "support" in message.lower()


class TestRetryLogic:
    """Tests for retry recommendation logic."""

    def test_temporary_errors_offer_retry(self):
        """SYSTEM_TEMPORARY should offer retry (FR-053)."""
        for code in ["TIMEOUT", "SERVICE_UNAVAILABLE", "RATE_LIMITED", "CONNECTION_ERROR"]:
            record = ErrorRecord(
                code=code,
                message="Error",
                category=ErrorCategory.SYSTEM_TEMPORARY,
            )

            assert should_offer_retry(record) is True

    def test_user_correctable_no_retry(self):
        """USER_CORRECTABLE should not offer automatic retry."""
        record = ErrorRecord(
            code="TASK_NOT_FOUND",
            message="Not found",
            category=ErrorCategory.USER_CORRECTABLE,
        )

        assert should_offer_retry(record) is False

    def test_permanent_no_retry(self):
        """SYSTEM_PERMANENT should not offer retry."""
        record = ErrorRecord(
            code="INTERNAL_ERROR",
            message="Internal error",
            category=ErrorCategory.SYSTEM_PERMANENT,
        )

        assert should_offer_retry(record) is False


class TestEscalation:
    """Tests for escalation recommendation."""

    def test_permanent_requires_escalation(self):
        """SYSTEM_PERMANENT should require escalation (FR-054)."""
        record = ErrorRecord(
            code="INTERNAL_ERROR",
            message="Error",
            category=ErrorCategory.SYSTEM_PERMANENT,
        )

        assert should_escalate(record) is True

    def test_temporary_no_escalation(self):
        """SYSTEM_TEMPORARY should not require immediate escalation."""
        record = ErrorRecord(
            code="TIMEOUT",
            message="Timeout",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert should_escalate(record) is False

    def test_user_correctable_no_escalation(self):
        """USER_CORRECTABLE should not require escalation."""
        record = ErrorRecord(
            code="TASK_NOT_FOUND",
            message="Not found",
            category=ErrorCategory.USER_CORRECTABLE,
        )

        assert should_escalate(record) is False


class TestAgentError:
    """Tests for AgentError exception class."""

    def test_agent_error_with_category(self):
        """AgentError should use provided category."""
        error = AgentError(
            code="CUSTOM_ERROR",
            message="Custom error",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert error.category == ErrorCategory.SYSTEM_TEMPORARY

    def test_agent_error_auto_category(self):
        """AgentError should auto-categorize known codes."""
        error = AgentError(
            code="TASK_NOT_FOUND",
            message="Task not found",
        )

        assert error.category == ErrorCategory.USER_CORRECTABLE

    def test_agent_error_to_record(self):
        """AgentError should convert to ErrorRecord."""
        error = AgentError(
            code="TIMEOUT",
            message="Request timed out",
            details={"duration_ms": 30500},
        )

        record = error.to_error_record()

        assert isinstance(record, ErrorRecord)
        assert record.code == "TIMEOUT"
        assert record.details == {"duration_ms": 30500}
