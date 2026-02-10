"""
Conversation SQLModel for database representation.

This module defines the Conversation table structure for PostgreSQL
with all required fields for AI chat session management.

Phase III: AI Chatbot Conversations
- Stores conversation metadata per user
- Tracks active/inactive state
- Links to messages via conversation_id
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation model for database table.

    This SQLModel represents the conversations table in PostgreSQL with
    all fields, constraints, and indexes for conversation management.

    Attributes (FR-007 to FR-010):
        id: UUID primary key (auto-generated)
        user_id: User identifier for conversation ownership (FK to users)
        started_at: Timestamp when conversation began
        last_message_at: Timestamp of most recent message
        is_active: Whether conversation is currently active (default: True)

    Table Configuration:
        - Primary key: id (UUID)
        - Index: idx_conversations_user_id ON (user_id)
        - Index: idx_conversations_user_active ON (user_id, is_active)
          WHERE is_active = TRUE (partial index)
        - FK: user_id REFERENCES users(id) ON DELETE CASCADE
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier (UUID)",
    )

    user_id: str = Field(
        max_length=50,
        nullable=False,
        index=True,
        description="User identifier for conversation ownership (FR-008)",
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when conversation began",
    )

    last_message_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp of most recent message (FR-009)",
    )

    is_active: bool = Field(
        default=True,
        nullable=False,
        description="Whether conversation is currently active (FR-010)",
    )

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user123",
                "started_at": "2026-01-28T10:00:00Z",
                "last_message_at": "2026-01-28T10:30:00Z",
                "is_active": True,
            }
        }
