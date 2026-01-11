"""
Task model and custom exceptions for TODO application.

This module defines the core Task entity and custom exception types
used throughout the application.
"""

from datetime import datetime, UTC
from typing import Dict, Any, Optional


# Custom Exception Classes
class TodoError(Exception):
    """Base exception for TODO application errors.

    All custom exceptions in the TODO application inherit from this base class.
    This allows catching all application-specific errors with a single except block.

    Example:
        try:
            task_manager.add_task("")
        except TodoError as e:
            print(f"Application error: {e}")
    """
    pass


class TaskNotFoundError(TodoError):
    """Raised when a task with the given ID doesn't exist.

    Attributes:
        task_id: The ID of the task that was not found.

    Example:
        raise TaskNotFoundError(999)
        # Output: Task 999 not found
    """

    def __init__(self, task_id: int) -> None:
        """Initialize TaskNotFoundError with task ID.

        Args:
            task_id: The ID of the task that was not found.
        """
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id


class ValidationError(TodoError):
    """Raised when user input or task data fails validation.

    This exception is used for all validation failures, such as:
    - Empty or whitespace-only titles
    - Titles exceeding maximum length
    - Invalid task IDs (non-numeric, negative)

    Example:
        raise ValidationError("Task title cannot be empty")
    """
    pass


class InvalidTaskDataError(TodoError):
    """Raised when task data is malformed or corrupt.

    This exception is used for data integrity issues that shouldn't occur
    during normal operation, such as:
    - Task objects with missing required fields
    - Tasks with invalid data types
    - Corrupted task data during serialization

    Example:
        raise InvalidTaskDataError("Task is missing required 'id' field")
    """
    pass


# Task Model Implementation


class Task:
    """Represents a single todo item.

    A Task has a unique ID, a title (description), completion status,
    and a creation timestamp. Tasks are the core entity in the TODO application.

    Attributes:
        id: Unique integer identifier (assigned by TaskManager).
        title: Description of what needs to be done (non-empty, ≤500 chars).
        completed: Whether the task is finished (True/False).
        created_at: UTC timestamp when the task was created.

    Example:
        >>> task = Task(id=1, title="Buy groceries")
        >>> task.title
        'Buy groceries'
        >>> task.completed
        False
    """

    def __init__(
        self,
        id: int,
        title: str,
        completed: bool = False,
        created_at: Optional[datetime] = None
    ) -> None:
        """Initialize a Task.

        Args:
            id: Unique task identifier (positive integer).
            title: Task description (will be validated and trimmed).
            completed: Initial completion status (default: False).
            created_at: Creation timestamp (default: current UTC time).

        Raises:
            ValidationError: If title is empty or exceeds 500 characters.

        Example:
            >>> task = Task(id=1, title="  Buy milk  ")
            >>> task.title
            'Buy milk'  # Whitespace trimmed
        """
        self.id = id
        self.title = self._validate_title(title)
        self.completed = completed
        self.created_at = created_at if created_at is not None else datetime.now(UTC)

    @staticmethod
    def _validate_title(title: str) -> str:
        """Validate and normalize task title.

        Validation rules:
        - Title must not be empty or whitespace-only
        - Title must not exceed 500 characters
        - Leading and trailing whitespace is automatically trimmed

        Args:
            title: The title string to validate.

        Returns:
            str: The validated and trimmed title.

        Raises:
            ValidationError: If title fails validation.

        Example:
            >>> Task._validate_title("  Valid title  ")
            'Valid title'
            >>> Task._validate_title("")
            ValidationError: Task title cannot be empty
        """
        if not title or not title.strip():
            raise ValidationError("Task title cannot be empty")

        trimmed_title = title.strip()

        if len(trimmed_title) > 500:
            raise ValidationError(
                f"Task title too long (max 500 characters, got {len(trimmed_title)})"
            )

        return trimmed_title

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dictionary for JSON export.

        Returns a dictionary representation suitable for JSON serialization
        or data migration to Phase II database.

        Returns:
            dict: Dictionary with keys: id, title, completed, created_at.

        Example:
            >>> task = Task(id=1, title="Buy milk", completed=False)
            >>> task_dict = task.to_dict()
            >>> task_dict['id']
            1
            >>> task_dict['title']
            'Buy milk'
        """
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        """Return string representation for debugging.

        Returns:
            str: String like "Task(id=1, title='Buy milk', completed=False)".

        Example:
            >>> task = Task(id=1, title="Buy milk")
            >>> repr(task)
            "Task(id=1, title='Buy milk', completed=False)"
        """
        return (
            f"Task(id={self.id}, "
            f"title='{self.title}', "
            f"completed={self.completed})"
        )
