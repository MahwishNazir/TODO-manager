"""
Pydantic schemas for MCP tool inputs.

Defines input schemas for all 5 MCP tools that the agent can invoke.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AddTaskInput(BaseModel):
    """Input schema for add_task MCP tool."""

    user_id: str = Field(
        ...,
        description="Unique identifier of the task owner"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task title (1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (0-5000 characters)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user-123",
                "title": "Buy groceries",
                "description": "Get milk, eggs, and bread",
            }
        }
    }


class ListTasksInput(BaseModel):
    """Input schema for list_tasks MCP tool."""

    user_id: str = Field(
        ...,
        description="Unique identifier of the task owner"
    )
    status: Optional[Literal["pending", "completed", "all"]] = Field(
        default="all",
        description="Filter by status"
    )
    limit: Optional[int] = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum tasks to return (1-100)"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Number of tasks to skip"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user-123",
                "status": "pending",
                "limit": 10,
                "offset": 0,
            }
        }
    }


class UpdateTaskInput(BaseModel):
    """Input schema for update_task MCP tool."""

    user_id: str = Field(
        ...,
        description="Unique identifier of the task owner"
    )
    task_id: str = Field(
        ...,
        description="Unique identifier of the task to update"
    )
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="New task title (1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="New task description (empty string clears)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user-123",
                "task_id": "task-456",
                "title": "Buy groceries and snacks",
            }
        }
    }


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task MCP tool."""

    user_id: str = Field(
        ...,
        description="Unique identifier of the task owner"
    )
    task_id: str = Field(
        ...,
        description="Unique identifier of the task to complete"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user-123",
                "task_id": "task-456",
            }
        }
    }


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task MCP tool."""

    user_id: str = Field(
        ...,
        description="Unique identifier of the task owner"
    )
    task_id: str = Field(
        ...,
        description="Unique identifier of the task to delete"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user-123",
                "task_id": "task-456",
            }
        }
    }
