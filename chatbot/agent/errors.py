"""
Error handling infrastructure.

Provides error categorization, user-friendly messages, and error templates.
Implements FR-050 through FR-055 requirements.
"""

from typing import Any, Dict, Optional

from chatbot.agent.models.error import (
    ErrorCategory,
    ErrorRecord,
    ERROR_CODE_MAPPING,
    DEFAULT_SUGGESTIONS,
)


class AgentError(Exception):
    """Base exception for agent errors."""

    def __init__(
        self,
        code: str,
        message: str,
        category: Optional[ErrorCategory] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        self.code = code
        self.message = message
        self.category = category or ERROR_CODE_MAPPING.get(
            code, ErrorCategory.SYSTEM_PERMANENT
        )
        self.details = details
        self.suggestion = suggestion or DEFAULT_SUGGESTIONS.get(code)
        super().__init__(message)

    def to_error_record(self) -> ErrorRecord:
        """Convert to ErrorRecord model."""
        return ErrorRecord(
            code=self.code,
            message=self.message,
            category=self.category,
            details=self.details,
            suggestion=self.suggestion,
        )


# Error message templates for user-friendly responses
# These never expose technical details (FR-055)

ERROR_TEMPLATES = {
    # User-correctable errors (FR-052)
    "INVALID_INPUT": (
        "I couldn't understand that request. {suggestion}"
    ),
    "TASK_NOT_FOUND": (
        "I couldn't find a task matching '{reference}'. "
        "Would you like to see your current tasks?"
    ),
    "UNAUTHORIZED": (
        "Your session has expired. Please sign in again to continue."
    ),
    "NO_FIELDS_TO_UPDATE": (
        "I'm not sure what you'd like to change. "
        "Please specify the new title, description, or other field."
    ),
    "AMBIGUOUS_REFERENCE": (
        "I found {count} tasks that could match:\n{task_list}\n"
        "Which one did you mean? (Reply with the number)"
    ),

    # System-temporary errors (FR-053)
    "SERVICE_UNAVAILABLE": (
        "I'm having trouble connecting to the task service right now. "
        "Please try again in a moment."
    ),
    "TIMEOUT": (
        "That took longer than expected. Please try again."
    ),
    "RATE_LIMITED": (
        "I'm getting too many requests. Please wait a moment and try again."
    ),
    "CONNECTION_ERROR": (
        "I'm having trouble connecting right now. Please try again in a moment."
    ),

    # System-permanent errors (FR-054)
    "INTERNAL_ERROR": (
        "Something went wrong on our end. "
        "If this continues, please contact support."
    ),
    "UNKNOWN_ERROR": (
        "Something unexpected happened. Please try again later."
    ),
}


def format_error_message(
    code: str,
    **kwargs: Any
) -> str:
    """
    Format an error message from template.

    Args:
        code: Error code
        **kwargs: Template variables

    Returns:
        Formatted user-friendly error message
    """
    template = ERROR_TEMPLATES.get(code, ERROR_TEMPLATES["UNKNOWN_ERROR"])

    # Add default suggestion if not provided
    if "suggestion" not in kwargs:
        kwargs["suggestion"] = DEFAULT_SUGGESTIONS.get(code, "Please try again.")

    try:
        return template.format(**kwargs)
    except KeyError:
        # Missing template variable - return generic message
        return template.split("{")[0].strip() or ERROR_TEMPLATES["UNKNOWN_ERROR"]


def categorize_error(
    code: str,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> ErrorRecord:
    """
    Categorize an error and create an ErrorRecord.

    Args:
        code: Error code from MCP or internal
        message: Error message
        details: Additional error details

    Returns:
        ErrorRecord with appropriate category and suggestion
    """
    category = ERROR_CODE_MAPPING.get(code, ErrorCategory.SYSTEM_PERMANENT)
    suggestion = DEFAULT_SUGGESTIONS.get(code)

    return ErrorRecord(
        code=code,
        message=message or f"Error: {code}",
        category=category,
        details=details,
        suggestion=suggestion,
    )


def get_user_friendly_message(error_record: ErrorRecord) -> str:
    """
    Get a user-friendly message for an error.

    Never exposes technical details (FR-055).

    Args:
        error_record: The error record

    Returns:
        User-friendly error message
    """
    return error_record.get_user_message()


def should_offer_retry(error_record: ErrorRecord) -> bool:
    """
    Check if retry option should be offered.

    Implements FR-053.

    Args:
        error_record: The error record

    Returns:
        True if retry should be offered
    """
    return error_record.should_offer_retry()


def should_escalate(error_record: ErrorRecord) -> bool:
    """
    Check if error requires escalation.

    Implements FR-054.

    Args:
        error_record: The error record

    Returns:
        True if escalation is needed
    """
    return error_record.requires_escalation()


def format_task_not_found_error(
    reference: str,
) -> str:
    """Format a task not found error with the reference."""
    return format_error_message("TASK_NOT_FOUND", reference=reference)


def format_ambiguous_reference_error(
    tasks: list,
) -> str:
    """
    Format an ambiguous reference error with task list.

    Args:
        tasks: List of matching tasks

    Returns:
        Formatted error message with numbered task list
    """
    task_list = "\n".join(
        f"{i + 1}. {task.get('title', 'Untitled')}"
        for i, task in enumerate(tasks)
    )
    return format_error_message(
        "AMBIGUOUS_REFERENCE",
        count=len(tasks),
        task_list=task_list,
    )
