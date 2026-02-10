"""
Task SQLModel for database representation.

This module defines the Task table structure for PostgreSQL
with all required fields and validation rules.

Phase III Extensions:
- priority: Task priority level (low, medium, high)
- status: Task completion status (incomplete, complete)
- due_date: Optional due date for the task
- is_deleted: Soft delete flag
"""

from datetime import datetime, date
from typing import Optional
import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from .enums import Priority, TaskStatus


class EnumValue(sa.TypeDecorator):
    """Store Python str enums as their .value (lowercase) in the database."""

    impl = sa.String
    cache_ok = True

    def __init__(self, enum_class, length=20):
        self.enum_class = enum_class
        super().__init__(length)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, self.enum_class):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return self.enum_class(value)


class Task(SQLModel, table=True):
    """
    Task model for database table.

    This SQLModel represents the tasks table in PostgreSQL with
    all fields, constraints, and indexes for user isolation.

    Phase II Attributes:
        id: Auto-incrementing primary key
        user_id: User identifier for task isolation
        title: Task description (1-500 characters)
        is_completed: Completion status (default: False) - kept for backward compatibility
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified

    Phase III Attributes (FR-001 to FR-004):
        priority: Task priority level (default: medium)
        status: Task completion status (default: incomplete)
        due_date: Optional due date for the task
        is_deleted: Soft delete flag (default: False)

    Table Configuration:
        - Primary key: id (auto-increment)
        - Index: user_id (for efficient user filtering)
        - Index: idx_tasks_user_status (partial, WHERE is_deleted = FALSE)
        - Index: idx_tasks_user_due_date (partial, WHERE is_deleted = FALSE)
        - Index: idx_tasks_user_deleted (for soft delete queries)
        - Constraints: title not null, user_id not null
        - CHECK: priority IN ('low', 'medium', 'high')
        - CHECK: status IN ('incomplete', 'complete')
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
        description="Task completion status (Phase II, kept for backward compatibility)",
    )

    # Phase III: Extended fields (FR-001 to FR-004)
    priority: Priority = Field(
        default=Priority.MEDIUM,
        nullable=False,
        sa_type=EnumValue(Priority, 10),
        description="Task priority level (low, medium, high)",
    )

    status: TaskStatus = Field(
        default=TaskStatus.INCOMPLETE,
        nullable=False,
        sa_type=EnumValue(TaskStatus, 20),
        description="Task completion status (incomplete, complete)",
    )

    due_date: Optional[date] = Field(
        default=None,
        nullable=True,
        description="Optional due date for the task",
    )

    is_deleted: bool = Field(
        default=False,
        nullable=False,
        description="Soft delete flag",
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
                "priority": "medium",
                "status": "incomplete",
                "due_date": "2026-02-01",
                "is_deleted": False,
                "created_at": "2026-01-12T10:00:00Z",
                "updated_at": "2026-01-12T10:00:00Z",
            }
        }
