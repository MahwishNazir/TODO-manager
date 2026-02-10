"""
Pydantic schemas for API request/response validation.

This module defines Pydantic models for validating API requests
and responses, separate from the SQLModel database models.

Phase III Extensions:
- TaskCreate: Added priority, due_date fields
- TaskUpdate: Added priority, status, due_date fields
- TaskResponse: Added priority, status, due_date, is_deleted fields
"""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .enums import Priority, TaskStatus


class TaskCreate(BaseModel):
    """
    Schema for creating a new task via POST /api/{user_id}/tasks.

    Phase III Extensions:
        - priority: Optional priority level (default: medium)
        - due_date: Optional due date for the task

    Attributes:
        title: Task description (1-500 characters, will be trimmed)
        priority: Task priority level (low, medium, high)
        due_date: Optional due date for the task
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task description",
        example="Buy groceries",
    )

    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority level",
        example="medium",
    )

    due_date: Optional[date] = Field(
        default=None,
        description="Optional due date for the task",
        example="2026-02-01",
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

    Phase III Extensions:
        - priority: Optional priority level update
        - status: Optional status update (incomplete, complete)
        - due_date: Optional due date update (can be set to None)

    Attributes:
        title: New task description (1-500 characters, will be trimmed)
        priority: Task priority level (low, medium, high)
        status: Task completion status (incomplete, complete)
        due_date: Optional due date for the task
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="New task description",
        example="Buy organic groceries",
    )

    priority: Optional[Priority] = Field(
        default=None,
        description="Task priority level",
        example="high",
    )

    status: Optional[TaskStatus] = Field(
        default=None,
        description="Task completion status",
        example="complete",
    )

    due_date: Optional[date] = Field(
        default=None,
        description="Due date for the task (can be None to clear)",
        example="2026-02-01",
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

    Phase III Extensions:
        - priority: Task priority level
        - status: Task completion status
        - due_date: Optional due date
        - is_deleted: Soft delete flag

    Attributes:
        id: Task unique identifier
        user_id: User identifier who owns the task
        title: Task description
        is_completed: Task completion status (Phase II, kept for backward compatibility)
        priority: Task priority level (low, medium, high)
        status: Task completion status (incomplete, complete)
        due_date: Optional due date for the task
        is_deleted: Soft delete flag
        created_at: Task creation timestamp
        updated_at: Task last update timestamp
    """

    id: int = Field(..., description="Task unique identifier", example=1)
    user_id: str = Field(..., description="User identifier", example="user123")
    title: str = Field(..., description="Task description", example="Buy groceries")
    is_completed: bool = Field(
        ..., description="Task completion status (Phase II)", example=False
    )
    priority: Priority = Field(
        ..., description="Task priority level", example="medium"
    )
    status: TaskStatus = Field(
        ..., description="Task completion status", example="incomplete"
    )
    due_date: Optional[date] = Field(
        None, description="Due date for the task", example="2026-02-01"
    )
    is_deleted: bool = Field(
        ..., description="Soft delete flag", example=False
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


# =============================================================================
# Phase III: Conversation Schemas (FR-007 to FR-010)
# =============================================================================

from uuid import UUID
from typing import Any

from .enums import MessageRole


class ConversationCreate(BaseModel):
    """
    Schema for creating a new conversation.

    No fields required - user_id from auth, timestamps auto-generated.
    Conversation is created automatically when first message is sent.
    """

    pass


class ConversationResponse(BaseModel):
    """
    Schema for conversation response in API responses.

    Attributes:
        id: Conversation unique identifier (UUID)
        user_id: User identifier who owns the conversation
        started_at: Timestamp when conversation began
        last_message_at: Timestamp of most recent message
        is_active: Whether conversation is currently active
    """

    id: UUID = Field(..., description="Conversation unique identifier")
    user_id: str = Field(..., description="User identifier")
    started_at: datetime = Field(..., description="Conversation start time")
    last_message_at: datetime = Field(..., description="Last message timestamp")
    is_active: bool = Field(..., description="Whether conversation is active")

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """
    Schema for list of conversations response.

    Attributes:
        conversations: List of conversations
        count: Number of conversations returned
    """

    conversations: List[ConversationResponse] = Field(
        ..., description="List of conversations"
    )
    count: int = Field(..., description="Number of conversations returned")


# =============================================================================
# Phase III: Message Schemas (FR-011 to FR-015)
# =============================================================================


class MessageCreate(BaseModel):
    """
    Schema for creating a new message.

    Attributes:
        role: Message sender type (user, assistant, system)
        content: Message text content
        last_mentioned_task_id: Optional task reference for context
        metadata: Optional JSONB metadata
    """

    role: MessageRole = Field(
        ..., description="Message sender type", example="user"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Message text content",
        example="Show me my tasks for today",
    )
    last_mentioned_task_id: Optional[int] = Field(
        default=None,
        description="Optional task reference for context",
    )
    message_metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional JSONB data (tool calls, task refs, etc.)",
    )


class MessageResponse(BaseModel):
    """
    Schema for message response in API responses.

    Attributes:
        id: Message unique identifier (UUID)
        conversation_id: Parent conversation ID
        role: Message sender type
        content: Message text content
        created_at: Message timestamp
        last_mentioned_task_id: Optional task reference
        metadata: JSONB metadata
    """

    id: UUID = Field(..., description="Message unique identifier")
    conversation_id: UUID = Field(..., description="Parent conversation ID")
    role: MessageRole = Field(..., description="Message sender type")
    content: str = Field(..., description="Message text content")
    created_at: datetime = Field(..., description="Message timestamp")
    last_mentioned_task_id: Optional[int] = Field(
        None, description="Task reference for context"
    )
    message_metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="JSONB data (tool calls, task refs, etc.)"
    )

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """
    Schema for list of messages response.

    Attributes:
        messages: List of messages in chronological order
        count: Number of messages returned
    """

    messages: List[MessageResponse] = Field(
        ..., description="List of messages in chronological order"
    )
    count: int = Field(..., description="Number of messages returned")


# =============================================================================
# Phase III: Context Reconstruction Schema (FR-021, FR-022)
# =============================================================================


class PendingOperation(BaseModel):
    """
    Schema for pending operation awaiting confirmation.

    Attributes:
        operation: Operation type (delete, bulk_delete, bulk_complete)
        task_ids: List of task IDs to operate on
    """

    operation: str = Field(..., description="Operation type")
    task_ids: List[int] = Field(..., description="Task IDs to operate on")


class ConversationContext(BaseModel):
    """
    Schema for reconstructed conversation context (FR-021, FR-022).

    This is the context object passed to the AI agent for stateless processing.

    Attributes:
        conversation_id: Current conversation ID
        messages: Recent messages in chronological order
        last_mentioned_task_id: Most recently mentioned task for 'that one' resolution
        pending_operation: Operation awaiting user confirmation (if any)
    """

    conversation_id: UUID = Field(..., description="Current conversation ID")
    messages: List[MessageResponse] = Field(
        ..., description="Recent messages in chronological order"
    )
    last_mentioned_task_id: Optional[int] = Field(
        None, description="Most recently mentioned task ID"
    )
    pending_operation: Optional[PendingOperation] = Field(
        None, description="Operation awaiting confirmation"
    )
