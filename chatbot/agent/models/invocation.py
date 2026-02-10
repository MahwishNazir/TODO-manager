"""
ToolInvocation model.

Audit record for each MCP tool call.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field


class InvocationStatus(str, Enum):
    """Status of a tool invocation."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class ToolInvocation(BaseModel):
    """
    Audit record for each MCP tool call.

    Captures all information needed for debugging and compliance:
    - What tool was called with what parameters
    - When it started and completed
    - What the result was
    - How long it took

    Retained for 90 days for audit purposes.
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Unique invocation identifier"
    )
    session_id: UUID = Field(
        ...,
        description="Parent session ID"
    )
    correlation_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Request correlation ID for tracing"
    )
    tool_name: str = Field(
        ...,
        description="Name of the MCP tool (e.g., 'add_task', 'list_tasks')"
    )
    params: Dict[str, Any] = Field(
        ...,
        description="Input parameters passed to the tool"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Tool response (success data or error details)"
    )
    status: InvocationStatus = Field(
        default=InvocationStatus.PENDING,
        description="Current invocation status"
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When invocation started (UTC)"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="When invocation completed (UTC)"
    )
    user_id: str = Field(
        ...,
        description="User who initiated the invocation"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "session_id": "660e8400-e29b-41d4-a716-446655440001",
                "correlation_id": "req-abc123",
                "tool_name": "add_task",
                "params": {"user_id": "user-123", "title": "Buy groceries"},
                "result": {"success": True, "data": {"task": {}}},
                "status": "SUCCESS",
                "started_at": "2026-01-31T12:00:00Z",
                "completed_at": "2026-01-31T12:00:01Z",
                "user_id": "user-123",
            }
        }
    }

    @computed_field
    @property
    def duration_ms(self) -> Optional[int]:
        """Calculate execution duration in milliseconds."""
        if self.completed_at is None:
            return None
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() * 1000)

    def complete_success(self, result: Dict[str, Any]) -> None:
        """Mark invocation as successfully completed."""
        self.status = InvocationStatus.SUCCESS
        self.result = result
        self.completed_at = datetime.now(timezone.utc)

    def complete_error(self, error: Dict[str, Any]) -> None:
        """Mark invocation as completed with error."""
        self.status = InvocationStatus.ERROR
        self.result = error
        self.completed_at = datetime.now(timezone.utc)

    def complete_timeout(self) -> None:
        """Mark invocation as timed out."""
        self.status = InvocationStatus.TIMEOUT
        self.result = {"error": {"code": "TIMEOUT", "message": "Tool invocation timed out"}}
        self.completed_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        """Mark invocation as cancelled."""
        self.status = InvocationStatus.CANCELLED
        self.result = {"error": {"code": "CANCELLED", "message": "Invocation cancelled by user"}}
        self.completed_at = datetime.now(timezone.utc)

    def is_complete(self) -> bool:
        """Check if invocation has completed."""
        return self.status != InvocationStatus.PENDING

    def is_success(self) -> bool:
        """Check if invocation completed successfully."""
        return self.status == InvocationStatus.SUCCESS
