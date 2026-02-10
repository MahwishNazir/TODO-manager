"""
ConversationContext model.

Maintains conversation state for context-aware responses.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of a message in the conversation."""

    USER = "user"
    ASSISTANT = "assistant"


class ToolCall(BaseModel):
    """Record of a tool call made during message processing."""

    tool_name: str = Field(..., description="Name of the MCP tool called")
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters passed to the tool"
    )
    status: str = Field(..., description="Result status: success or error")
    duration_ms: Optional[int] = Field(
        default=None,
        description="Execution duration in milliseconds"
    )


class Message(BaseModel):
    """A single message in the conversation history."""

    role: MessageRole = Field(..., description="Who sent this message")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the message was sent (UTC)"
    )
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="Tools called during processing (assistant only)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "user",
                "content": "Create a task to buy groceries",
                "timestamp": "2026-01-31T12:00:00Z",
                "tool_calls": None,
            }
        }
    }


class TaskReference(BaseModel):
    """Reference to a task mentioned in conversation."""

    task_id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title for display")
    mentioned_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the task was mentioned"
    )


class ConversationContext(BaseModel):
    """
    Maintains conversation state for context-aware responses.

    Stores recent message history and task references for
    resolving pronouns like "that one" or "it".
    """

    messages: List[Message] = Field(
        default_factory=list,
        description="Recent message history (last 20)"
    )
    last_mentioned_task_id: Optional[str] = Field(
        default=None,
        description="ID of the last referenced task"
    )
    last_mentioned_task_ref: Optional[str] = Field(
        default=None,
        description="Text reference to the last task"
    )
    disambiguation_candidates: List[TaskReference] = Field(
        default_factory=list,
        description="Tasks for ambiguous reference resolution"
    )

    # Configuration
    max_messages: int = Field(
        default=20,
        description="Maximum messages to retain"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Create a task to buy groceries",
                        "timestamp": "2026-01-31T12:00:00Z",
                    }
                ],
                "last_mentioned_task_id": "task-123",
                "last_mentioned_task_ref": "buy groceries",
                "disambiguation_candidates": [],
            }
        }
    }

    def add_message(self, role: MessageRole, content: str, tool_calls: Optional[List[ToolCall]] = None) -> Message:
        """
        Add a message to the conversation history.

        Automatically trims old messages if exceeding max_messages.

        Args:
            role: Who sent the message
            content: Message content
            tool_calls: Optional list of tool calls (for assistant messages)

        Returns:
            The created message
        """
        message = Message(role=role, content=content, tool_calls=tool_calls)
        self.messages.append(message)

        # Trim old messages if needed
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

        return message

    def add_user_message(self, content: str) -> Message:
        """Add a user message to the conversation."""
        return self.add_message(MessageRole.USER, content)

    def add_assistant_message(self, content: str, tool_calls: Optional[List[ToolCall]] = None) -> Message:
        """Add an assistant message to the conversation."""
        return self.add_message(MessageRole.ASSISTANT, content, tool_calls)

    def set_last_mentioned_task(self, task_id: str, task_ref: str) -> None:
        """Update the last mentioned task reference."""
        self.last_mentioned_task_id = task_id
        self.last_mentioned_task_ref = task_ref

    def clear_last_mentioned_task(self) -> None:
        """Clear the last mentioned task reference."""
        self.last_mentioned_task_id = None
        self.last_mentioned_task_ref = None

    def set_disambiguation_candidates(self, candidates: List[TaskReference]) -> None:
        """Set candidates for disambiguation."""
        self.disambiguation_candidates = candidates

    def clear_disambiguation(self) -> None:
        """Clear disambiguation candidates."""
        self.disambiguation_candidates = []

    def get_message_history_for_prompt(self) -> List[Dict[str, str]]:
        """
        Get message history formatted for the agent prompt.

        Returns:
            List of messages in OpenAI format
        """
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
        ]
