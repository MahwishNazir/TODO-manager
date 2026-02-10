"""
Unit tests for error categorization and handling (T026).

Tests error handling infrastructure: categorization, user messages, templates.
"""

import pytest

from chatbot.agent.errors import (
    AgentError,
    ERROR_TEMPLATES,
    format_error_message,
    categorize_error,
    get_user_friendly_message,
    should_offer_retry,
    should_escalate,
    format_task_not_found_error,
    format_ambiguous_reference_error,
)
from chatbot.agent.models import ErrorCategory, ErrorRecord


class TestAgentError:
    """Tests for AgentError exception class."""

    def test_create_with_defaults(self):
        """AgentError should set defaults from code mapping."""
        error = AgentError(
            code="TASK_NOT_FOUND",
            message="Task not found",
        )

        assert error.code == "TASK_NOT_FOUND"
        assert error.message == "Task not found"
        assert error.category == ErrorCategory.USER_CORRECTABLE
        assert error.suggestion is not None

    def test_create_with_explicit_category(self):
        """AgentError should use explicit category."""
        error = AgentError(
            code="CUSTOM_ERROR",
            message="Custom error",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert error.category == ErrorCategory.SYSTEM_TEMPORARY

    def test_create_with_details(self):
        """AgentError should store details."""
        error = AgentError(
            code="INVALID_INPUT",
            message="Invalid input",
            details={"field": "title", "reason": "too short"},
        )

        assert error.details == {"field": "title", "reason": "too short"}

    def test_create_with_custom_suggestion(self):
        """AgentError should use custom suggestion."""
        error = AgentError(
            code="TASK_NOT_FOUND",
            message="Task not found",
            suggestion="Try using the task title instead.",
        )

        assert error.suggestion == "Try using the task title instead."

    def test_to_error_record(self):
        """to_error_record should create ErrorRecord."""
        error = AgentError(
            code="TIMEOUT",
            message="Request timed out",
            details={"duration_ms": 30500},
        )

        record = error.to_error_record()

        assert isinstance(record, ErrorRecord)
        assert record.code == "TIMEOUT"
        assert record.message == "Request timed out"
        assert record.details == {"duration_ms": 30500}

    def test_unknown_code_defaults_to_permanent(self):
        """Unknown error codes should default to SYSTEM_PERMANENT."""
        error = AgentError(
            code="UNKNOWN_CODE",
            message="Something happened",
        )

        assert error.category == ErrorCategory.SYSTEM_PERMANENT


class TestErrorTemplates:
    """Tests for error message templates."""

    def test_invalid_input_template(self):
        """INVALID_INPUT template should include suggestion."""
        message = format_error_message(
            "INVALID_INPUT",
            suggestion="Please provide a task title.",
        )

        assert "couldn't understand" in message.lower()
        assert "Please provide a task title" in message

    def test_task_not_found_template(self):
        """TASK_NOT_FOUND template should include reference."""
        message = format_error_message(
            "TASK_NOT_FOUND",
            reference="buy groceries",
        )

        assert "buy groceries" in message
        assert "couldn't find" in message.lower()

    def test_unauthorized_template(self):
        """UNAUTHORIZED template should mention sign in."""
        message = format_error_message("UNAUTHORIZED")

        assert "sign in" in message.lower()

    def test_service_unavailable_template(self):
        """SERVICE_UNAVAILABLE template should suggest retry."""
        message = format_error_message("SERVICE_UNAVAILABLE")

        assert "try again" in message.lower()

    def test_timeout_template(self):
        """TIMEOUT template should suggest retry."""
        message = format_error_message("TIMEOUT")

        assert "try again" in message.lower()

    def test_internal_error_template(self):
        """INTERNAL_ERROR template should mention support."""
        message = format_error_message("INTERNAL_ERROR")

        assert "support" in message.lower() or "went wrong" in message.lower()

    def test_ambiguous_reference_template(self):
        """AMBIGUOUS_REFERENCE template should include task list."""
        message = format_error_message(
            "AMBIGUOUS_REFERENCE",
            count=3,
            task_list="1. Buy groceries\n2. Buy gifts\n3. Buy supplies",
        )

        assert "3 tasks" in message
        assert "Buy groceries" in message
        assert "Buy gifts" in message

    def test_unknown_code_fallback(self):
        """Unknown codes should use UNKNOWN_ERROR template."""
        message = format_error_message("COMPLETELY_UNKNOWN_CODE")

        # Should not raise, should return something
        assert len(message) > 0

    def test_missing_template_variable(self):
        """Missing variables should not crash."""
        # TASK_NOT_FOUND needs 'reference' but we don't provide it
        message = format_error_message("TASK_NOT_FOUND")

        # Should return partial message or fallback
        assert len(message) > 0


class TestCategorizeError:
    """Tests for categorize_error function."""

    def test_categorize_user_correctable(self):
        """User-correctable codes should be categorized correctly."""
        record = categorize_error(
            code="TASK_NOT_FOUND",
            message="Task not found",
        )

        assert record.category == ErrorCategory.USER_CORRECTABLE
        assert record.suggestion is not None

    def test_categorize_system_temporary(self):
        """Temporary codes should be categorized correctly."""
        record = categorize_error(
            code="TIMEOUT",
            message="Request timed out",
        )

        assert record.category == ErrorCategory.SYSTEM_TEMPORARY

    def test_categorize_system_permanent(self):
        """Permanent codes should be categorized correctly."""
        record = categorize_error(
            code="INTERNAL_ERROR",
            message="Internal error",
        )

        assert record.category == ErrorCategory.SYSTEM_PERMANENT

    def test_categorize_with_details(self):
        """Details should be included in record."""
        record = categorize_error(
            code="INVALID_INPUT",
            message="Invalid",
            details={"field": "title"},
        )

        assert record.details == {"field": "title"}

    def test_categorize_unknown_code(self):
        """Unknown codes should default to permanent."""
        record = categorize_error(
            code="UNKNOWN",
            message="Unknown error",
        )

        assert record.category == ErrorCategory.SYSTEM_PERMANENT


class TestGetUserFriendlyMessage:
    """Tests for get_user_friendly_message function."""

    def test_user_correctable_message(self):
        """User-correctable should return suggestion."""
        record = ErrorRecord(
            code="TASK_NOT_FOUND",
            message="Task XYZ not found",
            category=ErrorCategory.USER_CORRECTABLE,
            suggestion="Check the task title and try again.",
        )

        message = get_user_friendly_message(record)

        assert "Check the task title" in message

    def test_system_temporary_message(self):
        """Temporary errors should suggest retry."""
        record = ErrorRecord(
            code="TIMEOUT",
            message="Internal timeout",
            category=ErrorCategory.SYSTEM_TEMPORARY,
            suggestion="Please try again.",
        )

        message = get_user_friendly_message(record)

        assert "try again" in message.lower()

    def test_system_permanent_message(self):
        """Permanent errors should mention support."""
        record = ErrorRecord(
            code="INTERNAL_ERROR",
            message="Database failure at line 42",  # Technical detail
            category=ErrorCategory.SYSTEM_PERMANENT,
        )

        message = get_user_friendly_message(record)

        # Should NOT expose technical details (FR-055)
        assert "line 42" not in message
        assert "Database" not in message
        assert "support" in message.lower() or "went wrong" in message.lower()


class TestShouldOfferRetry:
    """Tests for should_offer_retry function."""

    def test_temporary_errors_offer_retry(self):
        """SYSTEM_TEMPORARY errors should offer retry."""
        record = ErrorRecord(
            code="TIMEOUT",
            message="Timed out",
            category=ErrorCategory.SYSTEM_TEMPORARY,
        )

        assert should_offer_retry(record) is True

    def test_user_correctable_no_retry(self):
        """USER_CORRECTABLE errors should not offer retry."""
        record = ErrorRecord(
            code="TASK_NOT_FOUND",
            message="Not found",
            category=ErrorCategory.USER_CORRECTABLE,
        )

        assert should_offer_retry(record) is False

    def test_permanent_no_retry(self):
        """SYSTEM_PERMANENT errors should not offer retry."""
        record = ErrorRecord(
            code="INTERNAL_ERROR",
            message="Failed",
            category=ErrorCategory.SYSTEM_PERMANENT,
        )

        assert should_offer_retry(record) is False


class TestShouldEscalate:
    """Tests for should_escalate function."""

    def test_permanent_requires_escalation(self):
        """SYSTEM_PERMANENT should require escalation."""
        record = ErrorRecord(
            code="INTERNAL_ERROR",
            message="Failed",
            category=ErrorCategory.SYSTEM_PERMANENT,
        )

        assert should_escalate(record) is True

    def test_temporary_no_escalation(self):
        """SYSTEM_TEMPORARY should not require escalation."""
        record = ErrorRecord(
            code="TIMEOUT",
            message="Timed out",
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


class TestFormatTaskNotFoundError:
    """Tests for format_task_not_found_error helper."""

    def test_formats_reference(self):
        """Should format error with task reference."""
        message = format_task_not_found_error("buy groceries")

        assert "buy groceries" in message
        assert "couldn't find" in message.lower()


class TestFormatAmbiguousReferenceError:
    """Tests for format_ambiguous_reference_error helper."""

    def test_formats_task_list(self):
        """Should format error with numbered task list."""
        tasks = [
            {"title": "Buy groceries"},
            {"title": "Buy gifts"},
            {"title": "Buy supplies"},
        ]

        message = format_ambiguous_reference_error(tasks)

        assert "3 tasks" in message
        assert "1. Buy groceries" in message
        assert "2. Buy gifts" in message
        assert "3. Buy supplies" in message

    def test_handles_missing_title(self):
        """Should handle tasks with missing titles."""
        tasks = [
            {"title": "Task with title"},
            {},  # Missing title
        ]

        message = format_ambiguous_reference_error(tasks)

        assert "2 tasks" in message
        assert "Task with title" in message
        assert "Untitled" in message
