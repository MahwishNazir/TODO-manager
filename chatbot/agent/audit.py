"""
Audit logging module (T036, T109).

Provides audit trail for tool invocations as required by FR-022 and FR-062.
Supports both in-memory storage (development) and PostgreSQL (production).
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from chatbot.agent.config import get_settings
from chatbot.agent.models import ToolInvocation, InvocationStatus


# Configure audit logger
audit_logger = logging.getLogger("chatbot.audit")
audit_logger.setLevel(logging.INFO)


# In-memory audit store for development (fallback when no database)
_audit_store: List[ToolInvocation] = []


def _get_db_session():
    """
    Get database session if available.

    Returns:
        Database session generator or None if database not configured
    """
    try:
        from chatbot.agent.database import get_engine, get_session

        engine = get_engine()
        if engine is not None:
            return get_session()
    except Exception:
        pass
    return None


def _store_to_database(invocation: ToolInvocation) -> bool:
    """
    Store invocation to PostgreSQL database.

    Args:
        invocation: ToolInvocation record

    Returns:
        True if stored, False if database not available
    """
    try:
        from chatbot.agent.database import get_engine
        from chatbot.agent.models.audit_db import ToolInvocationDB
        from sqlmodel import Session

        engine = get_engine()
        if engine is None:
            return False

        # Convert to database model
        db_record = ToolInvocationDB.from_params(
            session_id=invocation.session_id,
            user_id=invocation.user_id,
            tool_name=invocation.tool_name,
            params=invocation.params,
        )
        db_record.id = invocation.id
        db_record.status = invocation.status.value
        db_record.started_at = invocation.started_at

        if invocation.completed_at:
            db_record.completed_at = invocation.completed_at
            db_record.duration_ms = invocation.get_duration_ms()

        if invocation.result:
            db_record.result = invocation.result

        if invocation.status == InvocationStatus.ERROR and invocation.result:
            db_record.error_message = invocation.result.get("error", "Unknown error")

        with Session(engine) as session:
            session.add(db_record)
            session.commit()

        return True

    except Exception as e:
        audit_logger.warning(f"Failed to store audit to database: {e}")
        return False


def _query_from_database(
    user_id: Optional[str] = None,
    session_id: Optional[UUID] = None,
    tool_name: Optional[str] = None,
    limit: int = 100,
) -> Optional[List[ToolInvocation]]:
    """
    Query invocations from PostgreSQL database.

    Args:
        user_id: Filter by user ID
        session_id: Filter by session ID
        tool_name: Filter by tool name
        limit: Maximum entries to return

    Returns:
        List of ToolInvocation records or None if database not available
    """
    try:
        from chatbot.agent.database import get_engine
        from chatbot.agent.models.audit_db import ToolInvocationDB
        from sqlmodel import Session, select

        engine = get_engine()
        if engine is None:
            return None

        with Session(engine) as session:
            query = select(ToolInvocationDB)

            if user_id:
                query = query.where(ToolInvocationDB.user_id == user_id)
            if session_id:
                query = query.where(ToolInvocationDB.session_id == session_id)
            if tool_name:
                query = query.where(ToolInvocationDB.tool_name == tool_name)

            query = query.order_by(ToolInvocationDB.started_at.desc()).limit(limit)
            db_records = session.exec(query).all()

            # Convert to ToolInvocation models
            results = []
            for record in db_records:
                inv = ToolInvocation(
                    session_id=record.session_id,
                    tool_name=record.tool_name,
                    params=record.params,
                    user_id=record.user_id,
                )
                inv.id = record.id
                inv.started_at = record.started_at
                inv.completed_at = record.completed_at
                inv.result = record.result
                inv.status = InvocationStatus(record.status)
                results.append(inv)

            return results

    except Exception as e:
        audit_logger.warning(f"Failed to query audit from database: {e}")
        return None


def log_tool_invocation(
    session_id: Optional[UUID],
    user_id: str,
    tool_name: str,
    params: Dict[str, Any],
    result: Optional[Dict[str, Any]] = None,
    status: InvocationStatus = InvocationStatus.PENDING,
    error: Optional[str] = None,
) -> ToolInvocation:
    """
    Log a tool invocation for audit purposes.

    Args:
        session_id: Session ID for context
        user_id: User who triggered the invocation
        tool_name: Name of the MCP tool
        params: Parameters passed to the tool
        result: Tool result (if completed)
        status: Invocation status
        error: Error message (if failed)

    Returns:
        Created ToolInvocation record
    """
    settings = get_settings()

    if not settings.audit_enabled:
        # Still create record but don't persist
        return ToolInvocation(
            session_id=session_id or UUID(int=0),
            tool_name=tool_name,
            params=params,
            user_id=user_id,
        )

    # Create invocation record
    invocation = ToolInvocation(
        session_id=session_id or UUID(int=0),
        tool_name=tool_name,
        params=params,
        user_id=user_id,
    )

    # Update status if completed
    if status == InvocationStatus.SUCCESS and result:
        invocation.complete_success(result)
    elif status == InvocationStatus.ERROR:
        invocation.complete_error({"error": error or "Unknown error"})
    elif status == InvocationStatus.TIMEOUT:
        invocation.complete_timeout()

    # Store to database if available, otherwise use in-memory
    stored_to_db = _store_to_database(invocation)

    if not stored_to_db:
        # Fall back to in-memory store for development
        _audit_store.append(invocation)

    # Log to file/console
    _log_to_logger(invocation)

    return invocation


def _log_to_logger(invocation: ToolInvocation) -> None:
    """Log invocation to the audit logger."""
    log_data = {
        "invocation_id": str(invocation.id),
        "session_id": str(invocation.session_id),
        "user_id": invocation.user_id,
        "tool_name": invocation.tool_name,
        "status": invocation.status.value,
        "started_at": invocation.started_at.isoformat(),
        "completed_at": invocation.completed_at.isoformat() if invocation.completed_at else None,
        "duration_ms": invocation.get_duration_ms(),
    }

    # Redact sensitive params
    redacted_params = _redact_sensitive(invocation.params)
    log_data["params"] = redacted_params

    audit_logger.info(
        f"Tool invocation: {invocation.tool_name}",
        extra={"audit_data": log_data}
    )


def _redact_sensitive(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive fields from params."""
    sensitive_fields = {"password", "token", "secret", "api_key", "auth"}
    redacted = {}

    for key, value in data.items():
        if any(s in key.lower() for s in sensitive_fields):
            redacted[key] = "[REDACTED]"
        elif isinstance(value, dict):
            redacted[key] = _redact_sensitive(value)
        else:
            redacted[key] = value

    return redacted


def get_audit_log(
    user_id: Optional[str] = None,
    session_id: Optional[UUID] = None,
    tool_name: Optional[str] = None,
    limit: int = 100,
) -> List[ToolInvocation]:
    """
    Retrieve audit log entries.

    Queries from PostgreSQL if available, otherwise uses in-memory store.

    Args:
        user_id: Filter by user ID
        session_id: Filter by session ID
        tool_name: Filter by tool name
        limit: Maximum entries to return

    Returns:
        List of matching ToolInvocation records
    """
    # Try database first
    db_results = _query_from_database(
        user_id=user_id,
        session_id=session_id,
        tool_name=tool_name,
        limit=limit,
    )

    if db_results is not None:
        return db_results

    # Fall back to in-memory store
    results = _audit_store.copy()

    if user_id:
        results = [r for r in results if r.user_id == user_id]

    if session_id:
        results = [r for r in results if r.session_id == session_id]

    if tool_name:
        results = [r for r in results if r.tool_name == tool_name]

    # Sort by started_at descending (most recent first)
    results.sort(key=lambda x: x.started_at, reverse=True)

    return results[:limit]


def clear_audit_log() -> int:
    """
    Clear the audit log (for testing).

    Returns:
        Number of entries cleared
    """
    count = len(_audit_store)
    _audit_store.clear()
    return count


def get_invocation_stats(
    user_id: Optional[str] = None,
    session_id: Optional[UUID] = None,
) -> Dict[str, Any]:
    """
    Get statistics for tool invocations.

    Args:
        user_id: Filter by user ID
        session_id: Filter by session ID

    Returns:
        Statistics dict
    """
    entries = get_audit_log(user_id=user_id, session_id=session_id, limit=10000)

    if not entries:
        return {
            "total_invocations": 0,
            "success_count": 0,
            "error_count": 0,
            "timeout_count": 0,
            "avg_duration_ms": 0,
            "tools_used": {},
        }

    # Calculate stats
    success_count = sum(1 for e in entries if e.status == InvocationStatus.SUCCESS)
    error_count = sum(1 for e in entries if e.status == InvocationStatus.ERROR)
    timeout_count = sum(1 for e in entries if e.status == InvocationStatus.TIMEOUT)

    # Calculate average duration
    durations = [e.get_duration_ms() for e in entries if e.get_duration_ms()]
    avg_duration = sum(durations) / len(durations) if durations else 0

    # Count tool usage
    tool_counts: Dict[str, int] = {}
    for entry in entries:
        tool_counts[entry.tool_name] = tool_counts.get(entry.tool_name, 0) + 1

    return {
        "total_invocations": len(entries),
        "success_count": success_count,
        "error_count": error_count,
        "timeout_count": timeout_count,
        "avg_duration_ms": round(avg_duration, 2),
        "tools_used": tool_counts,
    }


class AuditContext:
    """
    Context manager for auditing a tool invocation.

    Usage:
        async with AuditContext(session_id, user_id, "add_task", params) as audit:
            result = await invoke_tool(...)
            audit.complete_success(result)
    """

    def __init__(
        self,
        session_id: Optional[UUID],
        user_id: str,
        tool_name: str,
        params: Dict[str, Any],
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.tool_name = tool_name
        self.params = params
        self.invocation: Optional[ToolInvocation] = None

    def __enter__(self) -> "AuditContext":
        """Start audit record."""
        self.invocation = log_tool_invocation(
            session_id=self.session_id,
            user_id=self.user_id,
            tool_name=self.tool_name,
            params=self.params,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Handle exit and log any uncaught errors."""
        if exc_type is not None and self.invocation:
            self.invocation.complete_error({
                "error": str(exc_val),
                "exception_type": exc_type.__name__,
            })
        return False  # Don't suppress exceptions

    def complete_success(self, result: Dict[str, Any]) -> None:
        """Mark invocation as successful."""
        if self.invocation:
            self.invocation.complete_success(result)

    def complete_error(self, error: Dict[str, Any]) -> None:
        """Mark invocation as failed."""
        if self.invocation:
            self.invocation.complete_error(error)

    def complete_timeout(self) -> None:
        """Mark invocation as timed out."""
        if self.invocation:
            self.invocation.complete_timeout()
