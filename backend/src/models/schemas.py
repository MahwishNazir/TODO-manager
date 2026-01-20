"""
Pydantic schemas for API request/response validation.

This module defines Pydantic models for validating API requests
and responses, separate from the SQLModel database models.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TaskCreate(BaseModel):
    """
    Schema for creating a new task via POST /api/{user_id}/tasks.

    Attributes:
        title: Task description (1-500 characters, will be trimmed)
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task description",
        example="Buy groceries",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """
        Validate and trim task title.

        Args:
            value: The title string to validate

        Returns:
            str: Trimmed title

        Raises:
            ValueError: If title is empty or whitespace-only after trimming
        """
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be empty or whitespace-only")
        return trimmed


class TaskUpdate(BaseModel):
    """
    Schema for updating a task via PUT /api/{user_id}/tasks/{id}.

    Attributes:
        title: New task description (1-500 characters, will be trimmed)
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="New task description",
        example="Buy organic groceries",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """
        Validate and trim task title.

        Args:
            value: The title string to validate

        Returns:
            str: Trimmed title

        Raises:
            ValueError: If title is empty or whitespace-only after trimming
        """
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be empty or whitespace-only")
        return trimmed


class TaskResponse(BaseModel):
    """
    Schema for task response in API responses.

    This is the standard representation of a task returned by the API.

    Attributes:
        id: Task unique identifier
        user_id: User identifier who owns the task
        title: Task description
        is_completed: Task completion status
        created_at: Task creation timestamp
        updated_at: Task last update timestamp
    """

    id: int = Field(..., description="Task unique identifier", example=1)
    user_id: str = Field(..., description="User identifier", example="user123")
    title: str = Field(..., description="Task description", example="Buy groceries")
    is_completed: bool = Field(
        ..., description="Task completion status", example=False
    )
    created_at: datetime = Field(
        ..., description="Task creation timestamp", example="2026-01-12T10:00:00Z"
    )
    updated_at: datetime = Field(
        ..., description="Task last update timestamp", example="2026-01-12T10:00:00Z"
    )

    model_config = ConfigDict(from_attributes=True)  # Enable compatibility with SQLModel


class TaskListResponse(BaseModel):
    """
    Schema for list of tasks response from GET /api/{user_id}/tasks.

    Attributes:
        tasks: List of tasks
        count: Number of tasks returned
    """

    tasks: List[TaskResponse] = Field(
        ..., description="List of tasks", example=[]
    )
    count: int = Field(
        ..., description="Number of tasks returned", example=0
    )


class ErrorResponse(BaseModel):
    """
    Schema for error responses.

    This is the standard error format used across all API endpoints.

    Attributes:
        error: Error type or category
        detail: Human-readable error message
        type: Machine-readable error type identifier
    """

    error: str = Field(
        ..., description="Error type or category", example="Validation error"
    )
    detail: str = Field(
        ...,
        description="Human-readable error message",
        example="Task title cannot be empty",
    )
    type: str = Field(
        ...,
        description="Machine-readable error type",
        example="validation_error",
    )
