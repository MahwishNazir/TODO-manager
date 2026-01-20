"""
Task SQLModel for database representation.

This module defines the Task table structure for PostgreSQL
with all required fields and validation rules.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model for database table.

    This SQLModel represents the tasks table in PostgreSQL with
    all fields, constraints, and indexes for user isolation.

    Attributes:
        id: Auto-incrementing primary key
        user_id: User identifier for task isolation (not verified in Step 1)
        title: Task description (1-500 characters)
        is_completed: Completion status (default: False)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified

    Table Configuration:
        - Primary key: id (auto-increment)
        - Index: user_id (for efficient user filtering)
        - Constraints: title not null, user_id not null
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing task ID",
    )

    user_id: str = Field(
        max_length=50,
        index=True,
        nullable=False,
        description="User identifier for task isolation",
    )

    title: str = Field(
        min_length=1,
        max_length=500,
        nullable=False,
        description="Task description",
    )

    is_completed: bool = Field(
        default=False,
        nullable=False,
        description="Task completion status",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task last update timestamp",
    )

    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries",
                "is_completed": False,
                "created_at": "2026-01-12T10:00:00Z",
                "updated_at": "2026-01-12T10:00:00Z",
            }
        }
