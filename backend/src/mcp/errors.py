"""
Error taxonomy and response builders for MCP Server Tools Layer.

This module provides:
- ErrorCode enum for standardized error codes
- Response envelope builders for consistent tool responses
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Any
import uuid


class ErrorCode(str, Enum):
    """Standardized error codes for MCP tool responses.

    Client errors (4xx equivalent):
        INVALID_INPUT: Input validation failed
        TASK_NOT_FOUND: Specified task does not exist
        UNAUTHORIZED: User lacks permission for this operation
        NO_FIELDS_TO_UPDATE: Update called with no changes

    Server errors (5xx equivalent):
        SERVICE_UNAVAILABLE: Downstream service unavailable
        INTERNAL_ERROR: Unexpected server error
    """

    # Client errors
    INVALID_INPUT = "INVALID_INPUT"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    NO_FIELDS_TO_UPDATE = "NO_FIELDS_TO_UPDATE"

    # Server errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def _build_metadata() -> dict[str, str]:
    """Build metadata for response envelope."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": str(uuid.uuid4()),
    }


def build_success_response(data: dict[str, Any]) -> dict[str, Any]:
    """Build a successful response envelope.

    Args:
        data: The data payload to include in the response.

    Returns:
        A dictionary with the standard response envelope structure:
        {
            "success": True,
            "data": {...},
            "error": None,
            "metadata": {"timestamp": "...", "request_id": "..."}
        }
    """
    return {
        "success": True,
        "data": data,
        "error": None,
        "metadata": _build_metadata(),
    }


def build_error_response(
    code: ErrorCode,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an error response envelope.

    Args:
        code: The error code from ErrorCode enum.
        message: Human-readable error message.
        details: Optional additional error details.

    Returns:
        A dictionary with the standard response envelope structure:
        {
            "success": False,
            "data": None,
            "error": {"code": "...", "message": "...", "details": ...},
            "metadata": {"timestamp": "...", "request_id": "..."}
        }
    """
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code.value,
            "message": message,
            "details": details,
        },
        "metadata": _build_metadata(),
    }
