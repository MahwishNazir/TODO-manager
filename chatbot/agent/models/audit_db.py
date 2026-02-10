"""
SQLModel database model for tool invocations audit (T109, T110).

Provides persistent storage for audit logs in PostgreSQL.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text


class ToolInvocationDB(SQLModel, table=True):
    """
    Database model for tool invocation audit records.

    Stores audit trail for all MCP tool invocations per FR-022 and FR-062.
    """

    __tablename__ = "tool_invocations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(index=True)
    user_id: str = Field(index=True, max_length=255)
    tool_name: str = Field(index=True, max_length=100)

    # JSON serialized params (use Text for potentially large payloads)
    params_json: str = Field(default="{}", sa_column=Column(Text))

    # Result and error info
    result_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    error_message: Optional[str] = Field(default=None, max_length=1000)

    # Status tracking
    status: str = Field(default="PENDING", max_length=20)  # PENDING, SUCCESS, ERROR, TIMEOUT

    # Timestamps
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)

    # Duration in milliseconds (computed on completion)
    duration_ms: Optional[int] = Field(default=None)

    @property
    def params(self) -> Dict[str, Any]:
        """Get params as dict."""
        return json.loads(self.params_json) if self.params_json else {}

    @params.setter
    def params(self, value: Dict[str, Any]) -> None:
        """Set params from dict."""
        self.params_json = json.dumps(value)

    @property
    def result(self) -> Optional[Dict[str, Any]]:
        """Get result as dict."""
        return json.loads(self.result_json) if self.result_json else None

    @result.setter
    def result(self, value: Optional[Dict[str, Any]]) -> None:
        """Set result from dict."""
        self.result_json = json.dumps(value) if value else None

    def complete_success(self, result: Dict[str, Any]) -> None:
        """Mark invocation as successful."""
        self.status = "SUCCESS"
        self.result = result
        self.completed_at = datetime.now(timezone.utc)
        self._compute_duration()

    def complete_error(self, error: str) -> None:
        """Mark invocation as failed."""
        self.status = "ERROR"
        self.error_message = error[:1000] if len(error) > 1000 else error
        self.completed_at = datetime.now(timezone.utc)
        self._compute_duration()

    def complete_timeout(self) -> None:
        """Mark invocation as timed out."""
        self.status = "TIMEOUT"
        self.error_message = "Tool invocation timed out"
        self.completed_at = datetime.now(timezone.utc)
        self._compute_duration()

    def _compute_duration(self) -> None:
        """Compute duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)

    @classmethod
    def from_params(
        cls,
        session_id: UUID,
        user_id: str,
        tool_name: str,
        params: Dict[str, Any],
    ) -> "ToolInvocationDB":
        """Create a new invocation record from params."""
        record = cls(
            session_id=session_id,
            user_id=user_id,
            tool_name=tool_name,
        )
        record.params = params
        return record
