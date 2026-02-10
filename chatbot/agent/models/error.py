"""
ErrorRecord model.

Structured error information from tool failures.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """
    Error category for determining response type.

    - USER_CORRECTABLE: User can fix the issue (invalid input, not found)
    - SYSTEM_TEMPORARY: Transient issue, retry may succeed (timeout, rate limit)
    - SYSTEM_PERMANENT: Requires escalation (auth failure, service down)
    """

    USER_CORRECTABLE = "USER_CORRECTABLE"
    SYSTEM_TEMPORARY = "SYSTEM_TEMPORARY"
    SYSTEM_PERMANENT = "SYSTEM_PERMANENT"


# Mapping of MCP error codes to categories
ERROR_CODE_MAPPING: Dict[str, ErrorCategory] = {
    "INVALID_INPUT": ErrorCategory.USER_CORRECTABLE,
    "TASK_NOT_FOUND": ErrorCategory.USER_CORRECTABLE,
    "UNAUTHORIZED": ErrorCategory.USER_CORRECTABLE,
    "NO_FIELDS_TO_UPDATE": ErrorCategory.USER_CORRECTABLE,
    "SERVICE_UNAVAILABLE": ErrorCategory.SYSTEM_TEMPORARY,
    "TIMEOUT": ErrorCategory.SYSTEM_TEMPORARY,
    "RATE_LIMITED": ErrorCategory.SYSTEM_TEMPORARY,
    "INTERNAL_ERROR": ErrorCategory.SYSTEM_PERMANENT,
    "CONNECTION_ERROR": ErrorCategory.SYSTEM_TEMPORARY,
}

# Default suggestions per error code
DEFAULT_SUGGESTIONS: Dict[str, str] = {
    "INVALID_INPUT": "Please check your input and try again.",
    "TASK_NOT_FOUND": "The task could not be found. Would you like to see your current tasks?",
    "UNAUTHORIZED": "Your session has expired. Please sign in again to continue.",
    "NO_FIELDS_TO_UPDATE": "Please specify what you'd like to change.",
    "SERVICE_UNAVAILABLE": "The service is temporarily unavailable. Please try again in a moment.",
    "TIMEOUT": "The request took too long. Please try again.",
    "RATE_LIMITED": "Too many requests. Please wait a moment before trying again.",
    "INTERNAL_ERROR": "Something went wrong. If this persists, please contact support.",
    "CONNECTION_ERROR": "I'm having trouble connecting. Please try again.",
}


class ErrorRecord(BaseModel):
    """
    Structured error information from tool failures.

    Provides categorized error information with user-friendly messages
    and suggested remediation actions.
    """

    code: str = Field(
        ...,
        description="Error code from MCP taxonomy"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    category: ErrorCategory = Field(
        ...,
        description="Error category for response type"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context"
    )
    suggestion: Optional[str] = Field(
        default=None,
        description="Suggested corrective action"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "TASK_NOT_FOUND",
                "message": "Task with the specified ID was not found",
                "category": "USER_CORRECTABLE",
                "details": {"task_id": "nonexistent-id"},
                "suggestion": "The task could not be found. Would you like to see your current tasks?",
            }
        }
    }

    @classmethod
    def from_mcp_error(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> "ErrorRecord":
        """
        Create an ErrorRecord from an MCP error response.

        Args:
            code: MCP error code
            message: Error message from MCP
            details: Additional error details

        Returns:
            ErrorRecord with appropriate category and suggestion
        """
        category = ERROR_CODE_MAPPING.get(code, ErrorCategory.SYSTEM_PERMANENT)
        suggestion = DEFAULT_SUGGESTIONS.get(code)

        return cls(
            code=code,
            message=message,
            category=category,
            details=details,
            suggestion=suggestion,
        )

    def get_user_message(self) -> str:
        """
        Get a user-friendly error message.

        Returns message suitable for display to users,
        never exposing technical details (FR-055).
        """
        if self.category == ErrorCategory.USER_CORRECTABLE:
            return self.suggestion or self.message
        elif self.category == ErrorCategory.SYSTEM_TEMPORARY:
            return self.suggestion or "Something went wrong. Please try again."
        else:
            return "Something went wrong. If this persists, please contact support."

    def should_offer_retry(self) -> bool:
        """Check if retry should be offered (FR-053)."""
        return self.category == ErrorCategory.SYSTEM_TEMPORARY

    def requires_escalation(self) -> bool:
        """Check if error requires escalation (FR-054)."""
        return self.category == ErrorCategory.SYSTEM_PERMANENT
