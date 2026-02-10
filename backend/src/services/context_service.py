"""
Context reconstruction service for AI agent.

This service reconstructs conversation context from the database
for stateless AI agent processing (FR-021, FR-022).

Phase III: Context Reconstruction
- Retrieves conversation messages in chronological order
- Limits context to configurable max messages (default 50)
- Resolves last_mentioned_task_id for "that one" references
- Retrieves pending operations awaiting confirmation
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from src.models.conversation import Conversation
from src.models.message import Message
from src.models.schemas import (
    ConversationContext,
    MessageResponse,
    PendingOperation,
)


class ContextService:
    """
    Service for reconstructing conversation context.

    This service retrieves all necessary context for the AI agent
    to process a user request statelessly.

    Attributes:
        session: Database session for queries

    Example:
        service = ContextService(session)
        context = service.reconstruct_context(conversation_id)
        # context contains messages, last_mentioned_task_id, pending_operation
    """

    # Default maximum messages to include in context (FR-021)
    DEFAULT_MAX_MESSAGES = 50

    def __init__(self, session: Session):
        """
        Initialize the context service.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def reconstruct_context(
        self,
        conversation_id: UUID,
        max_messages: Optional[int] = None,
    ) -> ConversationContext:
        """
        Reconstruct conversation context for AI agent processing.

        Retrieves the most recent messages from the conversation,
        finds the last mentioned task ID for reference resolution,
        and checks for any pending operations awaiting confirmation.

        Args:
            conversation_id: UUID of the conversation to reconstruct
            max_messages: Maximum number of messages to include
                         (default: 50 per FR-021)

        Returns:
            ConversationContext: Reconstructed context with:
                - conversation_id
                - messages (chronological order)
                - last_mentioned_task_id
                - pending_operation (if any)

        Raises:
            ValueError: If conversation not found
        """
        if max_messages is None:
            max_messages = self.DEFAULT_MAX_MESSAGES

        # Verify conversation exists
        conversation = self._get_conversation(conversation_id)
        if conversation is None:
            raise ValueError(f"Conversation not found: {conversation_id}")

        # Get messages in chronological order (most recent N)
        messages = self._get_recent_messages(conversation_id, max_messages)

        # Find last mentioned task ID
        last_mentioned_task_id = self._get_last_mentioned_task_id(conversation_id)

        # Find pending operation (if any)
        pending_operation = self._get_pending_operation(conversation_id)

        return ConversationContext(
            conversation_id=conversation_id,
            messages=messages,
            last_mentioned_task_id=last_mentioned_task_id,
            pending_operation=pending_operation,
        )

    def _get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Conversation or None if not found
        """
        statement = select(Conversation).where(Conversation.id == conversation_id)
        return self.session.exec(statement).first()

    def _get_recent_messages(
        self,
        conversation_id: UUID,
        max_messages: int,
    ) -> list[MessageResponse]:
        """
        Retrieve the most recent messages from a conversation.

        Messages are returned in chronological order (oldest first).

        Args:
            conversation_id: UUID of the conversation
            max_messages: Maximum number of messages to retrieve

        Returns:
            List of MessageResponse objects in chronological order
        """
        # First, get the most recent N messages (descending order)
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_messages)
        )
        results = self.session.exec(statement).all()

        # Reverse to get chronological order (oldest first)
        messages = list(reversed(results))

        # Convert to MessageResponse schemas
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                last_mentioned_task_id=msg.last_mentioned_task_id,
                message_metadata=msg.message_metadata or {},
            )
            for msg in messages
        ]

    def _get_last_mentioned_task_id(
        self,
        conversation_id: UUID,
    ) -> Optional[int]:
        """
        Find the most recently mentioned task ID in a conversation.

        Used for resolving "that one" and similar pronoun references.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Task ID of most recently mentioned task, or None
        """
        statement = (
            select(Message.last_mentioned_task_id)
            .where(
                Message.conversation_id == conversation_id,
                Message.last_mentioned_task_id != None,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = self.session.exec(statement).first()
        return result

    def _get_pending_operation(
        self,
        conversation_id: UUID,
    ) -> Optional[PendingOperation]:
        """
        Find the most recent pending operation awaiting confirmation.

        Checks message metadata for pending_operation field.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            PendingOperation if one is pending, otherwise None
        """
        # Get messages in reverse chronological order
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
        )
        messages = self.session.exec(statement).all()

        # Find the most recent message with a pending operation
        for msg in messages:
            if msg.message_metadata and "pending_operation" in msg.message_metadata:
                pending_data = msg.message_metadata["pending_operation"]
                return PendingOperation(
                    operation=pending_data.get("operation", ""),
                    task_ids=pending_data.get("task_ids", []),
                )

        return None
