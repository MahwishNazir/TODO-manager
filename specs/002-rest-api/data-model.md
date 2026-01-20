# Data Model: REST API with Persistent Storage

**Feature**: Phase II Step 1 - REST API
**Date**: 2026-01-12
**Branch**: 002-rest-api

## Overview

This document defines the data model for the TODO application REST API using SQLModel (combining SQLAlchemy and Pydantic). The model supports user isolation, task persistence, and prepares for future authentication integration in Step 2.

## Entities

### Task

The core entity representing a todo item with user ownership and completion tracking.

**Table Name**: `tasks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| `user_id` | String(50) | NOT NULL, INDEXED | User identifier (trusted from URL in Step 1) |
| `title` | String(500) | NOT NULL, CHECK(length >= 1) | Task description |
| `is_completed` | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | DateTime | NOT NULL, DEFAULT NOW() | Creation timestamp (UTC) |
| `updated_at` | DateTime | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | Last modification timestamp (UTC) |

**Indexes**:
- `PRIMARY KEY (id)`: Fast lookup by task ID
- `INDEX idx_user_id (user_id)`: Fast filtering by user
- `INDEX idx_user_completed (user_id, is_completed)`: Optimized for filtered queries (e.g., "show incomplete tasks for user123")

**Constraints**:
- `CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 500)`: Enforce title length
- `CHECK (LENGTH(user_id) >= 1 AND LENGTH(user_id) <= 50)`: Enforce user_id length

**SQLModel Implementation**:

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task model for storing todo items with user isolation.

    Attributes:
        id: Unique task identifier (auto-incremented)
        user_id: User identifier (not authenticated in Step 1)
        title: Task description (1-500 characters)
        is_completed: Completion status (default: False)
        created_at: Creation timestamp (UTC, auto-set)
        updated_at: Last update timestamp (UTC, auto-updated)
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=50, index=True, nullable=False)
    title: str = Field(min_length=1, max_length=500, nullable=False)
    is_completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False
    )
```

## API Schemas (Pydantic Models)

Separate from the database model, these schemas define the API request/response structure.

### TaskCreate

Request body for creating a new task.

```python
from pydantic import BaseModel, Field, field_validator

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task description",
        examples=["Buy groceries"]
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()
```

**Example JSON**:
```json
{
  "title": "Buy groceries"
}
```

---

### TaskUpdate

Request body for updating an existing task.

```python
class TaskUpdate(BaseModel):
    """Schema for updating a task's title."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Updated task description",
        examples=["Buy organic groceries"]
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()
```

**Example JSON**:
```json
{
  "title": "Buy organic groceries"
}
```

---

### TaskResponse

Response body for a single task (used by GET, POST, PUT, PATCH).

```python
from datetime import datetime

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int = Field(description="Task ID", examples=[1])
    user_id: str = Field(description="User identifier", examples=["user123"])
    title: str = Field(description="Task description", examples=["Buy groceries"])
    is_completed: bool = Field(description="Completion status", examples=[False])
    created_at: datetime = Field(description="Creation timestamp (UTC)")
    updated_at: datetime = Field(description="Last update timestamp (UTC)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": "user123",
                    "title": "Buy groceries",
                    "is_completed": False,
                    "created_at": "2026-01-12T10:30:00Z",
                    "updated_at": "2026-01-12T10:30:00Z"
                }
            ]
        }
    }
```

**Example JSON**:
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "is_completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

---

### TaskListResponse

Response body for listing multiple tasks (used by GET /tasks).

```python
from typing import List

class TaskListResponse(BaseModel):
    """Schema for task list response."""
    tasks: List[TaskResponse] = Field(description="List of tasks")
    count: int = Field(description="Total number of tasks", examples=[3])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tasks": [
                        {
                            "id": 1,
                            "user_id": "user123",
                            "title": "Buy groceries",
                            "is_completed": False,
                            "created_at": "2026-01-12T10:30:00Z",
                            "updated_at": "2026-01-12T10:30:00Z"
                        }
                    ],
                    "count": 1
                }
            ]
        }
    }
```

**Example JSON**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user123",
      "title": "Buy groceries",
      "is_completed": false,
      "created_at": "2026-01-12T10:30:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    }
  ],
  "count": 1
}
```

**Note**: For Step 1, returning a simple array `List[TaskResponse]` is acceptable. The wrapped format with `count` prepares for pagination in future steps.

---

### ErrorResponse

Standard error response format.

```python
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(description="Error message", examples=["Task not found"])
    error_type: str = Field(
        default="unknown_error",
        description="Error category",
        examples=["not_found", "validation_error", "database_error"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Task not found",
                    "error_type": "not_found"
                }
            ]
        }
    }
```

**Example JSON (404)**:
```json
{
  "detail": "Task not found",
  "error_type": "not_found"
}
```

**Example JSON (422)**:
```json
{
  "detail": "title cannot be empty",
  "error_type": "validation_error"
}
```

## State Transitions

### Task Lifecycle

```
┌─────────────┐
│   CREATE    │ ──> is_completed = False
│             │     created_at = NOW()
│             │     updated_at = NOW()
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  INCOMPLETE │ ◄──┐
│ (is_completed│    │
│   = False)  │    │ PATCH /complete (toggle)
└──────┬──────┘    │
       │           │
       │ PATCH /complete (toggle)
       │           │
       ▼           │
┌─────────────┐    │
│  COMPLETED  │────┘
│ (is_completed
│   = True)   │
└──────┬──────┘
       │
       │ PUT /tasks/{id} (update title)
       │ updated_at = NOW()
       │
       ▼
┌─────────────┐
│   UPDATED   │
│ (title      │
│  modified)  │
└──────┬──────┘
       │
       │ DELETE /tasks/{id}
       │
       ▼
┌─────────────┐
│   DELETED   │ (Hard delete, removed from DB)
└─────────────┘
```

### Operations

1. **Create Task**:
   - Input: `title` (string, 1-500 chars)
   - Output: New task with `is_completed=False`, auto-generated `id`, current timestamps
   - Side effects: INSERT into database

2. **Read Task(s)**:
   - Input: `user_id` (path parameter)
   - Output: List of tasks for user or single task by ID
   - Side effects: None (read-only)
   - User isolation: Filter by `user_id`

3. **Update Task**:
   - Input: `task_id`, new `title`
   - Output: Updated task with new `title` and `updated_at` timestamp
   - Side effects: UPDATE database, set `updated_at = NOW()`
   - User isolation: Verify `task.user_id == user_id` before update

4. **Complete/Incomplete Task**:
   - Input: `task_id`
   - Output: Task with toggled `is_completed` status
   - Side effects: UPDATE database, toggle `is_completed`, set `updated_at = NOW()`
   - User isolation: Verify `task.user_id == user_id` before update

5. **Delete Task**:
   - Input: `task_id`
   - Output: None (204 No Content)
   - Side effects: DELETE from database (hard delete, not soft delete)
   - User isolation: Verify `task.user_id == user_id` before delete

## Validation Rules

### User ID Validation

**Pattern**: `^[a-zA-Z0-9_-]+$` (alphanumeric, hyphens, underscores)
**Length**: 1-50 characters

**Implementation**:
```python
import re
from fastapi import HTTPException, status

USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

def validate_user_id(user_id: str) -> str:
    """
    Validate user_id format.

    Args:
        user_id: User identifier from URL path

    Returns:
        Validated user_id

    Raises:
        HTTPException: 422 if validation fails
    """
    if not user_id or len(user_id) > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must be 1-50 characters"
        )
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must contain only alphanumeric characters, hyphens, and underscores"
        )
    return user_id
```

### Title Validation

**Length**: 1-500 characters (after trimming whitespace)
**Content**: Cannot be empty or whitespace-only

**Implementation**: Handled by Pydantic `@field_validator` in `TaskCreate` and `TaskUpdate` schemas (see above).

## Database Schema (SQL DDL)

Generated by Alembic migration (for reference):

```sql
-- Alembic migration: 001_initial_schema

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL CHECK (LENGTH(title) >= 1),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_user_id ON tasks(user_id);
CREATE INDEX idx_user_completed ON tasks(user_id, is_completed);

-- Function to auto-update updated_at (PostgreSQL-specific)
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call update function
CREATE TRIGGER trigger_update_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
```

**Note**: The trigger ensures `updated_at` is automatically updated on every UPDATE operation.

## Data Migration

### Phase I → Phase II Migration

If Phase I implemented JSON export (optional):

1. **Export from Phase I**:
```python
# backend/src/cli/export.py
import json
from backend.src.services.task_manager import TaskManager

manager = TaskManager()
tasks_data = [task.to_dict() for task in manager.tasks]

with open("phase1_tasks.json", "w") as f:
    json.dump(tasks_data, f, indent=2)
```

2. **Import to Phase II**:
```python
# backend/scripts/import_phase1.py
import json
from sqlmodel import Session
from backend.src.database import engine
from backend.src.models.task import Task

with open("phase1_tasks.json") as f:
    tasks_data = json.load(f)

with Session(engine) as session:
    for data in tasks_data:
        task = Task(
            title=data["title"],
            user_id="default_user",  # Assign to default user
            is_completed=data["is_completed"]
        )
        session.add(task)
    session.commit()
```

**Note**: Most users will start fresh in Phase II (no migration needed).

## Future Extensions (Out of Scope for Step 1)

The data model is designed to support future enhancements:

### Step 2 (Authentication):
- Add `users` table with `id`, `email`, `password_hash`, etc.
- Add foreign key: `tasks.user_id` → `users.id`
- user_id becomes authenticated user ID from JWT

### Intermediate Tier:
- Add `priority` column (ENUM: low, medium, high)
- Add `due_date` column (TIMESTAMP NULL)
- Add `tags` table for categorization (many-to-many relationship)

### Advanced Tier:
- Add `recurrence_rule` column (JSONB for recurring task patterns)
- Add `parent_task_id` for subtasks (self-referencing foreign key)
- Add `notifications` table for reminders

---

**Data Model Status**: ✅ Complete
**Next**: Generate API contracts (OpenAPI schema)
