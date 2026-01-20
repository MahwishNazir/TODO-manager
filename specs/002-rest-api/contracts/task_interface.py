"""
Task API Interface Specification

This file defines the contract for task operations.
It serves as the single source of truth for API behavior.
"""

from typing import Protocol, List
from datetime import datetime


class TaskCreateInput(Protocol):
    """Input schema for creating a task."""
    title: str  # 1-500 characters, non-empty


class TaskUpdateInput(Protocol):
    """Input schema for updating a task."""
    title: str  # 1-500 characters, non-empty


class TaskOutput(Protocol):
    """Output schema for a single task."""
    id: int
    user_id: str
    title: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class TaskService(Protocol):
    """
    Task service contract.

    All implementations must support user isolation:
    - Users can only access their own tasks
    - Cross-user access returns 404 (not 403, don't reveal existence)
    """

    def create_task(self, user_id: str, input: TaskCreateInput) -> TaskOutput:
        """
        Create a new task for a user.

        Args:
            user_id: User identifier (1-50 chars, alphanumeric + hyphens/underscores)
            input: Task creation data

        Returns:
            Created task with generated ID and timestamps

        Raises:
            ValidationError (422): Invalid input (empty title, title > 500 chars, invalid user_id)
            DatabaseError (500): Database operation failed
        """
        ...

    def get_all_tasks(self, user_id: str) -> List[TaskOutput]:
        """
        Get all tasks for a user.

        Args:
            user_id: User identifier

        Returns:
            List of tasks (empty list if no tasks)

        Raises:
            ValidationError (422): Invalid user_id format
            DatabaseError (500): Database operation failed
        """
        ...

    def get_task_by_id(self, user_id: str, task_id: int) -> TaskOutput:
        """
        Get a specific task by ID for a user.

        Args:
            user_id: User identifier
            task_id: Task ID

        Returns:
            Task with matching ID

        Raises:
            NotFoundError (404): Task not found or belongs to different user
            ValidationError (422): Invalid user_id or task_id format
            DatabaseError (500): Database operation failed
        """
        ...

    def update_task(self, user_id: str, task_id: int, input: TaskUpdateInput) -> TaskOutput:
        """
        Update a task's title.

        Args:
            user_id: User identifier
            task_id: Task ID
            input: Update data

        Returns:
            Updated task with new title and updated_at timestamp

        Raises:
            NotFoundError (404): Task not found or belongs to different user
            ValidationError (422): Invalid input or user_id
            DatabaseError (500): Database operation failed
        """
        ...

    def toggle_completion(self, user_id: str, task_id: int) -> TaskOutput:
        """
        Toggle task completion status.

        Args:
            user_id: User identifier
            task_id: Task ID

        Returns:
            Task with toggled is_completed status and updated_at timestamp

        Raises:
            NotFoundError (404): Task not found or belongs to different user
            ValidationError (422): Invalid user_id or task_id
            DatabaseError (500): Database operation failed
        """
        ...

    def delete_task(self, user_id: str, task_id: int) -> None:
        """
        Delete a task permanently.

        Args:
            user_id: User identifier
            task_id: Task ID

        Returns:
            None (204 No Content on success)

        Raises:
            NotFoundError (404): Task not found or belongs to different user
            ValidationError (422): Invalid user_id or task_id
            DatabaseError (500): Database operation failed
        """
        ...


# HTTP Status Code Contract
class HTTPStatusCodes:
    """Expected HTTP status codes for each operation."""

    # Success codes
    OK = 200  # GET (single task), PUT (update), PATCH (complete)
    CREATED = 201  # POST (create)
    NO_CONTENT = 204  # DELETE

    # Client error codes
    NOT_FOUND = 404  # Task not found or belongs to different user
    UNPROCESSABLE_ENTITY = 422  # Validation error

    # Server error codes
    INTERNAL_SERVER_ERROR = 500  # Database error or unexpected exception


# API Endpoint Paths
class APIEndpoints:
    """API endpoint paths."""

    LIST_TASKS = "/api/{user_id}/tasks"  # GET
    CREATE_TASK = "/api/{user_id}/tasks"  # POST
    GET_TASK = "/api/{user_id}/tasks/{id}"  # GET
    UPDATE_TASK = "/api/{user_id}/tasks/{id}"  # PUT
    DELETE_TASK = "/api/{user_id}/tasks/{id}"  # DELETE
    TOGGLE_COMPLETE = "/api/{user_id}/tasks/{id}/complete"  # PATCH


# Validation Rules
class ValidationRules:
    """Validation constraints for task data."""

    # User ID constraints
    USER_ID_MIN_LENGTH = 1
    USER_ID_MAX_LENGTH = 50
    USER_ID_PATTERN = r'^[a-zA-Z0-9_-]+$'

    # Title constraints
    TITLE_MIN_LENGTH = 1
    TITLE_MAX_LENGTH = 500

    # Error messages
    ERROR_TITLE_EMPTY = "title cannot be empty"
    ERROR_TITLE_TOO_LONG = "title exceeds maximum length of 500 characters"
    ERROR_USER_ID_INVALID = "user_id must contain only alphanumeric characters, hyphens, and underscores"
    ERROR_USER_ID_LENGTH = "user_id must be 1-50 characters"
    ERROR_TASK_NOT_FOUND = "Task not found"
    ERROR_DATABASE = "Database error occurred"
