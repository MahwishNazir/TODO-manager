# Data Model: Phase I - Python Console TODO Application

**Feature**: 001-phase1-console-app
**Date**: 2026-01-10
**Purpose**: Define data entities, relationships, and validation rules

## Overview

This document defines the data model for Phase I of the TODO application. The model is intentionally simple for in-memory storage but designed to be compatible with Phase II database schema (PostgreSQL via SQLModel).

## Entity Definitions

### Task

**Purpose**: Represents a single todo item with title, completion status, and metadata.

**Attributes**:

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | int | Yes | Auto-generated | Positive integer, unique | Unique identifier for the task |
| `title` | str | Yes | N/A | Non-empty, ≤500 chars | Description of what needs to be done |
| `completed` | bool | Yes | False | N/A | Whether the task is finished |
| `created_at` | datetime | Yes | Current timestamp | N/A | When the task was created |

**Validation Rules**:

1. **Title Validation**:
   - Must not be empty or whitespace-only
   - Must not exceed 500 characters
   - Leading/trailing whitespace automatically trimmed
   - Special characters allowed (unicode support)

2. **ID Validation**:
   - Must be positive integer (>= 1)
   - Automatically assigned by TaskManager
   - Never modified after creation
   - Not reused after deletion

3. **Completed Validation**:
   - Boolean value only (True/False)
   - No tri-state (no "in progress" for Phase I)
   - Can toggle freely between True and False

4. **Created At Validation**:
   - Must be valid datetime object
   - Automatically set on creation
   - Never modified after creation
   - Stored in UTC (for Phase II compatibility)

**Invariants**:

- A task with an ID exists in storage or doesn't exist (no partial state)
- Title is always a non-empty string after validation
- created_at is immutable after task creation
- ID is immutable after task creation

**State Diagram**:

```
┌─────────┐
│         │
│ Created │ ─────┐
│         │      │
└─────────┘      │
                 ▼
         ┌───────────────┐
         │  Incomplete   │◄──────┐
         │ (completed =  │       │
         │    False)     │       │ toggle_completion()
         └───────────────┘       │
                 │               │
                 │ mark_complete()
                 │               │
                 ▼               │
         ┌───────────────┐       │
         │   Complete    │───────┘
         │ (completed =  │
         │    True)      │
         └───────────────┘
                 │
                 │ delete()
                 ▼
         ┌───────────────┐
         │    Deleted    │
         │  (removed     │
         │  from storage)│
         └───────────────┘
```

**Lifecycle**:

1. **Creation**: Task created with auto-generated ID and current timestamp
2. **Active**: Task can be updated (title), marked complete/incomplete
3. **Deletion**: Task removed from storage, ID not reused

**Serialization**:

For Phase I → Phase II migration, tasks must serialize to JSON:

```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false,
  "created_at": "2026-01-10T14:30:00Z"
}
```

**Python Class Structure** (implementation guidance):

```python
from datetime import datetime
from typing import Optional

class Task:
    """Represents a todo item.

    Attributes:
        id: Unique identifier (auto-generated)
        title: Task description
        completed: Whether task is finished
        created_at: Timestamp of creation
    """

    def __init__(
        self,
        id: int,
        title: str,
        completed: bool = False,
        created_at: Optional[datetime] = None
    ) -> None:
        """Initialize a task.

        Args:
            id: Unique task identifier
            title: Task description
            completed: Initial completion status
            created_at: Creation timestamp (defaults to now)

        Raises:
            ValidationError: If title is invalid
        """
        self.id = id
        self.title = self._validate_title(title)
        self.completed = completed
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def _validate_title(title: str) -> str:
        """Validate and normalize task title."""
        # Implementation in code

    def to_dict(self) -> dict:
        """Serialize task to dictionary for JSON export."""
        # Implementation in code

    def __repr__(self) -> str:
        """String representation for debugging."""
        # Implementation in code
```

### TaskManager

**Purpose**: Manages the collection of tasks and provides CRUD operations.

**Attributes**:

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `_tasks` | Dict[int, Task] | Yes | {} | Private | Dictionary storing tasks by ID |
| `_next_id` | int | Yes | 1 | Private, positive | Counter for generating new task IDs |

**Operations**:

| Operation | Method | Input | Output | Side Effects | Exceptions |
|-----------|--------|-------|--------|--------------|------------|
| Add | `add_task(title)` | str | Task | Increments `_next_id`, adds to `_tasks` | ValidationError |
| Get | `get_task(id)` | int | Task | None | TaskNotFoundError |
| Update | `update_task(id, title)` | int, str | Task | Modifies task in `_tasks` | TaskNotFoundError, ValidationError |
| Delete | `delete_task(id)` | int | None | Removes from `_tasks` | TaskNotFoundError |
| Mark Complete | `mark_complete(id, completed)` | int, bool | Task | Updates task.completed | TaskNotFoundError |
| List All | `get_all_tasks()` | None | List[Task] | None | None |
| Count | `count()` | None | int | None | None |

**Validation Rules**:

1. **add_task**:
   - Title must pass Task validation
   - ID automatically assigned (sequential)
   - Task immediately added to storage

2. **get_task**:
   - ID must exist in storage
   - Returns reference to actual task (not copy)

3. **update_task**:
   - ID must exist in storage
   - New title must pass validation
   - Only title can be updated via this method

4. **delete_task**:
   - ID must exist in storage
   - ID is not reused after deletion
   - Operation is irreversible

5. **mark_complete**:
   - ID must exist in storage
   - Completed value must be boolean
   - Can toggle between True and False freely

6. **get_all_tasks**:
   - Returns list of all tasks (copy of values)
   - Order is not guaranteed (dict iteration)
   - Empty list if no tasks

**Invariants**:

- `_next_id` always > maximum ID in `_tasks`
- All tasks in `_tasks` have unique IDs
- `_tasks` keys match their task.id values
- No null/None tasks in storage

**Concurrency** (Phase I):

- Single-threaded only
- No locking required
- Sequential operations guaranteed

**Performance Guarantees**:

- add_task: O(1) time complexity
- get_task: O(1) time complexity
- update_task: O(1) time complexity
- delete_task: O(1) time complexity
- mark_complete: O(1) time complexity
- get_all_tasks: O(n) time complexity where n = number of tasks
- count: O(1) time complexity

**Python Class Structure** (implementation guidance):

```python
from typing import Dict, List

class TaskManager:
    """Manages collection of tasks with CRUD operations.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects
        _next_id: Counter for generating new task IDs
    """

    def __init__(self) -> None:
        """Initialize an empty task manager."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str) -> Task:
        """Create and add a new task."""
        # Implementation in code

    def get_task(self, task_id: int) -> Task:
        """Retrieve a task by ID."""
        # Implementation in code

    def update_task(self, task_id: int, title: str) -> Task:
        """Update task title."""
        # Implementation in code

    def delete_task(self, task_id: int) -> None:
        """Remove a task from storage."""
        # Implementation in code

    def mark_complete(self, task_id: int, completed: bool) -> Task:
        """Mark task as complete or incomplete."""
        # Implementation in code

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks."""
        # Implementation in code

    def count(self) -> int:
        """Return number of tasks."""
        # Implementation in code
```

## Entity Relationships

```
┌────────────────┐
│  TaskManager   │
│                │
│ - _tasks: Dict │ ───────┐
│ - _next_id: int│        │ contains
└────────────────┘        │ 0..*
                          │
                          ▼
                   ┌──────────┐
                   │   Task   │
                   │          │
                   │ - id     │
                   │ - title  │
                   │ - status │
                   │ - created│
                   └──────────┘
```

**Relationship Details**:

- **TaskManager contains Task (0..*)**:
  - One TaskManager manages zero or more Tasks
  - Tasks are stored in `_tasks` dictionary
  - Tasks cannot exist without TaskManager (composition)
  - Deleting TaskManager deletes all Tasks (in-memory only)

- **No Task-to-Task relationships** in Phase I:
  - No dependencies between tasks
  - No parent-child hierarchies
  - No task grouping/categorization
  - (Deferred to future phases)

## Data Validation Strategy

### Input Validation (User Input)

**Validate at boundaries**:
- CLI input validation (menu choices, task IDs)
- Task title validation (empty, length, trimming)

**Validation Methods**:
```python
def validate_task_id(input_str: str) -> int:
    """Convert and validate task ID from user input."""
    try:
        task_id = int(input_str)
        if task_id < 1:
            raise ValidationError("Task ID must be positive")
        return task_id
    except ValueError:
        raise ValidationError("Task ID must be a number")

def validate_title(title: str) -> str:
    """Validate and normalize task title."""
    if not title or not title.strip():
        raise ValidationError("Task title cannot be empty")
    if len(title) > 500:
        raise ValidationError("Task title too long (max 500 characters)")
    return title.strip()
```

### Internal Data Integrity

**Trust internal operations**:
- No validation on TaskManager internal operations
- Type hints ensure type safety at development time
- mypy catches type errors before runtime

**Assertions for debugging** (optional):
```python
def add_task(self, title: str) -> Task:
    task = Task(id=self._next_id, title=title)
    assert task.id not in self._tasks, "ID collision detected"
    self._tasks[task.id] = task
    self._next_id += 1
    return task
```

## Error Handling

### Exception Hierarchy

```
Exception
└── TodoError (base)
    ├── TaskNotFoundError
    ├── InvalidTaskDataError
    └── ValidationError
```

**Exception Definitions**:

```python
class TodoError(Exception):
    """Base exception for TODO application errors."""
    pass

class TaskNotFoundError(TodoError):
    """Raised when a task with given ID doesn't exist."""

    def __init__(self, task_id: int):
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id

class InvalidTaskDataError(TodoError):
    """Raised when task data is malformed."""
    pass

class ValidationError(TodoError):
    """Raised when user input fails validation."""
    pass
```

**Usage**:

```python
try:
    task = task_manager.get_task(999)
except TaskNotFoundError as e:
    print(f"Error: {e}")  # "Error: Task 999 not found"
```

## Phase II Migration Considerations

### Database Schema Mapping

Phase I data model maps directly to Phase II SQLModel schema:

```python
# Phase II (preview - not implemented in Phase I)
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str = Field(max_length=500)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Data Export Format

Phase I export (JSON):
```json
{
  "version": "1.0",
  "exported_at": "2026-01-10T12:00:00Z",
  "tasks": [...]
}
```

Phase II import will:
1. Validate JSON schema
2. Create database records
3. Preserve IDs (if available)
4. Handle ID conflicts (regenerate if needed)

## Summary

**Entities**: 2 (Task, TaskManager)
**Relationships**: 1 (composition)
**Validation Points**: 2 (user input, task creation)
**Performance**: All operations O(1) except list_all O(n)
**Migration**: Direct mapping to Phase II database schema

**Next**: See [contracts/](./contracts/) for detailed interface definitions.
