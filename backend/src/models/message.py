"""
Message SQLModel for database representation.

This module defines the Message table structure for PostgreSQL
with all required fields for AI chat message storage.

Phase III: AI Chatbot Messages
- Stores individual messages in conversations
- Tracks message role (user/assistant/system)
- Links to tasks via last_mentioned_task_id
- Supports flexible metadata via JSONB
"""

from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON

from .enums import MessageRole


class Message(SQLModel, table=True):
    """
    Message model for database table.

    This SQLModel represents the messages table in PostgreSQL with
    all fields, constraints, and indexes for message storage.

    Attributes (FR-011 to FR-015):
        id: UUID primary key (auto-generated)
        conversation_id: UUID FK to conversations table (FR-012)
        role: Message sender type - user/assistant/system (FR-013)
        content: Message text content
        created_at: Timestamp for ordering (FR-015)
        last_mentioned_task_id: Optional FK to tasks for context (FR-014)
        metadata: JSONB field for flexible extension data

    Table Configuration:
        - Primary key: id (UUID)
        - Index: idx_messages_conversation ON (conversation_id)
        - Index: idx_messages_conversation_time ON (conversation_id, created_at)
        - FK: conversation_id REFERENCES conversations(id) ON DELETE CASCADE
        - FK: last_mentioned_task_id REFERENCES tasks(id) ON DELETE SET NULL
        - CHECK: role IN ('user', 'assistant', 'system')
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier (UUID)",
    )

    conversation_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="conversations.id",
        description="Parent conversation (FR-012)",
    )

    role: MessageRole = Field(
        nullable=False,
        description="Message sender type: user, assistant, or system (FR-013)",
    )

    content: str = Field(
        nullable=False,
        description="Message text content",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Message timestamp for ordering (FR-015)",
    )

    last_mentioned_task_id: Optional[int] = Field(
        default=None,
        nullable=True,
        foreign_key="tasks.id",
        description="Task referenced for context resolution (FR-014)",
    )

    # Note: Cannot use "metadata" as it's reserved by SQLAlchemy
    message_metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=True, default={}),
        description="JSONB field for flexible data (tool calls, displayed tasks, etc.)",
    )

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Show me my tasks for today",
                "created_at": "2026-01-28T10:00:00Z",
                "last_mentioned_task_id": None,
                "message_metadata": {},
            }
        }
