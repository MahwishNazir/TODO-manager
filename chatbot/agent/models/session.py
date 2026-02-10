"""
AgentSession model.

Represents an active conversation session between user and agent.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from chatbot.agent.models.confirmation import ConfirmationState
    from chatbot.agent.models.context import ConversationContext


class SessionStatus(str, Enum):
    """Status of an agent session."""

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class AgentSession(BaseModel):
    """
    Represents an active conversation session between user and agent.

    Contains user context, conversation history, and session metadata.
    Sessions expire after 30 minutes of inactivity.
    """

    session_id: UUID = Field(
        default_factory=uuid4,
        description="Unique session identifier"
    )
    user_id: str = Field(
        ...,
        min_length=1,
        description="Authenticated user's ID"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Session creation timestamp (UTC)"
    )
    last_active: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last activity timestamp (UTC)"
    )
    status: SessionStatus = Field(
        default=SessionStatus.ACTIVE,
        description="Current session status"
    )

    # These will be set after import to avoid circular imports
    context: "ConversationContext | None" = Field(
        default=None,
        description="Current conversation state"
    )
    confirmation: "ConfirmationState | None" = Field(
        default=None,
        description="Pending confirmation state"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-123",
                "created_at": "2026-01-31T12:00:00Z",
                "last_active": "2026-01-31T12:05:00Z",
                "status": "ACTIVE",
            }
        }
    }

    def touch(self) -> None:
        """Update last_active timestamp to current time."""
        self.last_active = datetime.now(timezone.utc)

    def is_expired(self, ttl_seconds: int = 1800) -> bool:
        """
        Check if session has expired.

        Args:
            ttl_seconds: Session time-to-live in seconds (default: 30 minutes)

        Returns:
            True if session has expired
        """
        if self.status == SessionStatus.EXPIRED:
            return True

        elapsed = (datetime.now(timezone.utc) - self.last_active).total_seconds()
        return elapsed > ttl_seconds

    def expire(self) -> None:
        """Mark session as expired."""
        self.status = SessionStatus.EXPIRED
