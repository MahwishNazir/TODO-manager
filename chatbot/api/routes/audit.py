"""
Audit query endpoint (T111).

Provides API for querying tool invocation audit logs for debugging.
"""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from chatbot.api.dependencies import CurrentUser, get_current_user
from chatbot.api.schemas import APIResponse
from chatbot.agent.audit import get_audit_log, get_invocation_stats


router = APIRouter()


@router.get("/audit/invocations", response_model=APIResponse)
async def list_invocations(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session_id: Optional[UUID] = Query(default=None, description="Filter by session ID"),
    tool_name: Optional[str] = Query(default=None, description="Filter by tool name"),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum entries to return"),
) -> APIResponse:
    """
    List tool invocations for the current user.

    Returns audit log entries filtered by the current user's ID.
    Optionally filter by session_id or tool_name.

    Args:
        session_id: Filter by session ID
        tool_name: Filter by tool name
        limit: Maximum entries to return (1-500)

    Returns:
        List of invocation records
    """
    invocations = get_audit_log(
        user_id=current_user.user_id,
        session_id=session_id,
        tool_name=tool_name,
        limit=limit,
    )

    # Convert to serializable format
    entries = [
        {
            "id": str(inv.id),
            "session_id": str(inv.session_id),
            "tool_name": inv.tool_name,
            "status": inv.status.value,
            "started_at": inv.started_at.isoformat(),
            "completed_at": inv.completed_at.isoformat() if inv.completed_at else None,
            "duration_ms": inv.get_duration_ms(),
            "params": _sanitize_params(inv.params),
        }
        for inv in invocations
    ]

    return APIResponse(
        success=True,
        data={
            "invocations": entries,
            "count": len(entries),
        },
    )


@router.get("/audit/stats", response_model=APIResponse)
async def get_stats(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session_id: Optional[UUID] = Query(default=None, description="Filter by session ID"),
) -> APIResponse:
    """
    Get invocation statistics for the current user.

    Returns aggregate statistics including success/error counts,
    average duration, and tool usage breakdown.

    Args:
        session_id: Filter by session ID

    Returns:
        Statistics summary
    """
    stats = get_invocation_stats(
        user_id=current_user.user_id,
        session_id=session_id,
    )

    return APIResponse(
        success=True,
        data={"stats": stats},
    )


@router.get("/audit/invocations/{invocation_id}", response_model=APIResponse)
async def get_invocation(
    invocation_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> APIResponse:
    """
    Get details of a specific invocation.

    Args:
        invocation_id: Invocation UUID

    Returns:
        Invocation details including result if available
    """
    # Get all invocations for user and find the specific one
    invocations = get_audit_log(user_id=current_user.user_id, limit=10000)

    for inv in invocations:
        if inv.id == invocation_id:
            return APIResponse(
                success=True,
                data={
                    "invocation": {
                        "id": str(inv.id),
                        "session_id": str(inv.session_id),
                        "tool_name": inv.tool_name,
                        "status": inv.status.value,
                        "started_at": inv.started_at.isoformat(),
                        "completed_at": inv.completed_at.isoformat() if inv.completed_at else None,
                        "duration_ms": inv.get_duration_ms(),
                        "params": _sanitize_params(inv.params),
                        "result": inv.result,
                    },
                },
            )

    return APIResponse(
        success=False,
        error={
            "code": "NOT_FOUND",
            "message": "Invocation not found or access denied",
        },
    )


def _sanitize_params(params: dict) -> dict:
    """Sanitize sensitive fields from params for API response."""
    sensitive_fields = {"password", "token", "secret", "api_key", "auth"}
    sanitized = {}

    for key, value in params.items():
        if any(s in key.lower() for s in sensitive_fields):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_params(value)
        else:
            sanitized[key] = value

    return sanitized
