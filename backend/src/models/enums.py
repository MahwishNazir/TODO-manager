"""
Enum definitions for Phase III data models.

This module defines Python Enums for priority, task status,
message role, and operation types used across the data models.
"""

from enum import Enum


class Priority(str, Enum):
    """Task priority levels.

    Stored as VARCHAR in PostgreSQL with CHECK constraint.
    Default value is MEDIUM.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Task completion status.

    Replaces the boolean is_completed field for more flexibility.
    Default value is INCOMPLETE.
    """
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class MessageRole(str, Enum):
    """Message sender type in conversations.

    Identifies the source of each message in the chat history.
    """
    USER = "user"          # Human input
    ASSISTANT = "assistant"  # AI response
    SYSTEM = "system"      # System-generated message


class OperationType(str, Enum):
    """Types of operations that may require user confirmation.

    Used in pending_operations table for delete confirmations.
    """
    DELETE = "delete"           # Single task deletion
    BULK_DELETE = "bulk_delete"  # Multiple task deletion
    BULK_COMPLETE = "bulk_complete"  # Multiple task completion
