"""
Pydantic schemas for MCP Server tool inputs and outputs.

This module defines:
- Input schemas for each MCP tool (with validation)
- Output schemas for task responses
- Response envelope schema
"""

from typing import Literal
from pydantic import BaseModel, Field, model_validator


# =============================================================================
# Common Validation Patterns
# =============================================================================

USER_ID_PATTERN = r"^[a-zA-Z0-9_-]+$"
USER_ID_MIN_LENGTH = 1
USER_ID_MAX_LENGTH = 50

TITLE_MIN_LENGTH = 1
TITLE_MAX_LENGTH = 500

DESCRIPTION_MAX_LENGTH = 5000


# =============================================================================
# Output Schemas
# =============================================================================


class TaskOutput(BaseModel):
    """Output representation of a task in MCP tool responses."""

    id: str
    user_id: str
    title: str
    description: str | None = None
    status: Literal["pending", "completed"]
    created_at: str  # ISO 8601
    updated_at: str  # ISO 8601
    completed_at: str | None = None  # ISO 8601, present when status="completed"


class ErrorDetail(BaseModel):
    """Error details in response envelope."""

    code: str
    message: str
    details: dict | None = None


class ResponseMetadata(BaseModel):
    """Metadata in response envelope."""

    timestamp: str  # ISO 8601
    request_id: str  # UUID


class ResponseEnvelope(BaseModel):
    """Standard response envelope for all MCP tools."""

    success: bool
    data: dict | None = None
    error: ErrorDetail | None = None
    metadata: ResponseMetadata


# =============================================================================
# Input Schemas
# =============================================================================


class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""

    user_id: str = Field(
        ...,
        min_length=USER_ID_MIN_LENGTH,
        max_length=USER_ID_MAX_LENGTH,
        pattern=USER_ID_PATTERN,
        description="Unique identifier of the task owner",
    )
    title: str = Field(
        ...,
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        description="Task title",
    )
    description: str | None = Field(
        None,
        max_length=DESCRIPTION_MAX_LENGTH,
        description="Optional task description",
    )


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""

    user_id: str = Field(
        ...,
        min_length=USER_ID_MIN_LENGTH,
        max_length=USER_ID_MAX_LENGTH,
        pattern=USER_ID_PATTERN,
        description="Unique identifier of the task owner",
    )
    status: Literal["pending", "completed", "all"] = Field(
        "all",
        description="Filter by task status",
    )
    limit: int = Field(
        50,
        ge=1,
        le=100,
        description="Maximum tasks to return",
    )
    offset: int = Field(
        0,
        ge=0,
        description="Number of tasks to skip",
    )


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""

    user_id: str = Field(
        ...,
        min_length=USER_ID_MIN_LENGTH,
        max_length=USER_ID_MAX_LENGTH,
        pattern=USER_ID_PATTERN,
        description="Unique identifier of the task owner",
    )
    task_id: str = Field(
        ...,
        description="Unique identifier of the task to update",
    )
    title: str | None = Field(
        None,
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        description="New task title",
    )
    description: str | None = Field(
        None,
        max_length=DESCRIPTION_MAX_LENGTH,
        description="New task description (empty string clears)",
    )

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UpdateTaskInput":
        """Validate that at least one field is provided for update."""
        if self.title is None and self.description is None:
            raise ValueError(
                "At least one of 'title' or 'description' must be provided"
            )
        return self


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""

    user_id: str = Field(
        ...,
        min_length=USER_ID_MIN_LENGTH,
        max_length=USER_ID_MAX_LENGTH,
        pattern=USER_ID_PATTERN,
        description="Unique identifier of the task owner",
    )
    task_id: str = Field(
        ...,
        description="Unique identifier of the task to complete",
    )


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""

    user_id: str = Field(
        ...,
        min_length=USER_ID_MIN_LENGTH,
        max_length=USER_ID_MAX_LENGTH,
        pattern=USER_ID_PATTERN,
        description="Unique identifier of the task owner",
    )
    task_id: str = Field(
        ...,
        description="Unique identifier of the task to delete",
    )
