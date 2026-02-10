"""
ConfirmationState model.

Tracks pending confirmation requests for destructive operations.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class ConfirmationStatus(str, Enum):
    """Status of the confirmation state machine."""

    IDLE = "IDLE"
    AWAITING_DELETE = "AWAITING_DELETE"
    AWAITING_BULK = "AWAITING_BULK"
    AWAITING_MULTI_UPDATE = "AWAITING_MULTI_UPDATE"
    AWAITING_PLAN_APPROVAL = "AWAITING_PLAN_APPROVAL"


class ConfirmationState(BaseModel):
    """
    Tracks pending confirmation requests for destructive operations.

    Implements a finite state machine for confirmation flows:
    - IDLE: No pending confirmation
    - AWAITING_DELETE: Waiting for delete confirmation
    - AWAITING_BULK: Waiting for bulk operation confirmation
    - AWAITING_MULTI_UPDATE: Waiting for multi-field update confirmation
    - AWAITING_PLAN_APPROVAL: Waiting for multi-step plan approval

    Transitions:
    - IDLE -> AWAITING_* on destructive action
    - AWAITING_* -> IDLE on confirm/decline/timeout/new intent
    """

    state: ConfirmationStatus = Field(
        default=ConfirmationStatus.IDLE,
        description="Current confirmation state"
    )
    pending_action: Optional[str] = Field(
        default=None,
        description="Action awaiting confirmation (e.g., 'delete', 'bulk_update')"
    )
    affected_ids: List[str] = Field(
        default_factory=list,
        description="Task IDs affected by pending action"
    )
    requested_at: Optional[datetime] = Field(
        default=None,
        description="When confirmation was requested (UTC)"
    )
    action_description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the pending action"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "state": "AWAITING_DELETE",
                "pending_action": "delete",
                "affected_ids": ["task-123"],
                "requested_at": "2026-01-31T12:00:00Z",
                "action_description": "Delete task 'Buy groceries'",
            }
        }
    }

    @model_validator(mode="after")
    def validate_state_consistency(self) -> "ConfirmationState":
        """Ensure state and fields are consistent."""
        if self.state == ConfirmationStatus.IDLE:
            # IDLE state should have no pending data
            if self.pending_action is not None:
                self.pending_action = None
            if self.affected_ids:
                self.affected_ids = []
            if self.requested_at is not None:
                self.requested_at = None
            if self.action_description is not None:
                self.action_description = None
        else:
            # Non-IDLE states must have pending_action
            if self.pending_action is None:
                raise ValueError(
                    f"State {self.state} requires pending_action to be set"
                )
        return self

    def is_idle(self) -> bool:
        """Check if no confirmation is pending."""
        return self.state == ConfirmationStatus.IDLE

    def is_awaiting_confirmation(self) -> bool:
        """Check if waiting for user confirmation."""
        return self.state != ConfirmationStatus.IDLE

    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """
        Check if pending confirmation has expired.

        Args:
            timeout_seconds: Timeout in seconds (default: 5 minutes)

        Returns:
            True if confirmation has expired
        """
        if self.state == ConfirmationStatus.IDLE or self.requested_at is None:
            return False

        elapsed = (datetime.now(timezone.utc) - self.requested_at).total_seconds()
        return elapsed > timeout_seconds

    def set_awaiting_delete(
        self,
        task_ids: List[str],
        description: str
    ) -> None:
        """Set state to awaiting delete confirmation."""
        self.state = ConfirmationStatus.AWAITING_DELETE
        self.pending_action = "delete"
        self.affected_ids = task_ids
        self.requested_at = datetime.now(timezone.utc)
        self.action_description = description

    def set_awaiting_bulk(
        self,
        action: str,
        task_ids: List[str],
        description: str
    ) -> None:
        """Set state to awaiting bulk operation confirmation."""
        self.state = ConfirmationStatus.AWAITING_BULK
        self.pending_action = action
        self.affected_ids = task_ids
        self.requested_at = datetime.now(timezone.utc)
        self.action_description = description

    def set_awaiting_plan_approval(
        self,
        plan_id: str,
        description: str
    ) -> None:
        """Set state to awaiting plan approval."""
        self.state = ConfirmationStatus.AWAITING_PLAN_APPROVAL
        self.pending_action = "plan_approval"
        self.affected_ids = [plan_id]
        self.requested_at = datetime.now(timezone.utc)
        self.action_description = description

    def reset(self) -> None:
        """Reset to IDLE state."""
        self.state = ConfirmationStatus.IDLE
        self.pending_action = None
        self.affected_ids = []
        self.requested_at = None
        self.action_description = None
