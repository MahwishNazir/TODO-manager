"""Models package for Phase II and Phase III.

Exports SQLModel entities, Pydantic schemas, and enums for
todo tasks, conversations, and messages.
"""
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.schemas import (
    # Task schemas
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    # Conversation schemas
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    # Message schemas
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    # Context schema
    ConversationContext,
    PendingOperation,
    # Error schema
    ErrorResponse,
)
from src.models.enums import Priority, TaskStatus, MessageRole, OperationType

__all__ = [
    # SQLModel entities
    "Task",
    "Conversation",
    "Message",
    # Task schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    # Conversation schemas
    "ConversationCreate",
    "ConversationResponse",
    "ConversationListResponse",
    # Message schemas
    "MessageCreate",
    "MessageResponse",
    "MessageListResponse",
    # Context schema
    "ConversationContext",
    "PendingOperation",
    # Error schema
    "ErrorResponse",
    # Enums
    "Priority",
    "TaskStatus",
    "MessageRole",
    "OperationType",
]
