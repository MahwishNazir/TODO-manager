"""
Message service layer for business logic.

This module provides operations for messages with user isolation
through conversation ownership verification.

Phase III: Message Storage and Retrieval
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from src.models.conversation import Conversation
from src.models.message import Message
from src.models.enums import MessageRole


class MessageService:
    """
    Service class for message operations with user isolation.

    Messages are accessed through their parent conversation,
    which enforces user isolation.
    """

    def __init__(self, session: Session):
        """Initialize service with database session."""
        self.session = session

    def _verify_conversation_ownership(
        self,
        conversation_id: UUID,
        user_id: str,
    ) -> Optional[Conversation]:
        """
        Verify that a conversation belongs to the specified user.

        Args:
            conversation_id: Conversation UUID to verify
            user_id: User identifier for isolation

        Returns:
            Conversation if owned by user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        return self.session.exec(statement).first()

    def get_messages_for_conversation(
        self,
        conversation_id: UUID,
        user_id: str,
        limit: Optional[int] = None,
    ) -> Optional[List[Message]]:
        """
        Get messages for a conversation with user isolation.

        Returns None if conversation doesn't exist or belongs to another user.
        Returns messages in chronological order (oldest first).

        Args:
            conversation_id: Conversation UUID
            user_id: User identifier for isolation
            limit: Optional max number of messages (most recent)

        Returns:
            List of messages if accessible, None otherwise
        """
        # Verify conversation ownership
        if not self._verify_conversation_ownership(conversation_id, user_id):
            return None

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        if limit:
            # Get most recent N messages, then reverse for chronological order
            statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            results = list(self.session.exec(statement).all())
            return list(reversed(results))

        return list(self.session.exec(statement).all())

    def get_message_by_id(
        self,
        message_id: UUID,
        user_id: str,
    ) -> Optional[Message]:
        """
        Get a specific message by ID with user isolation.

        Verifies message's conversation belongs to the user.

        Args:
            message_id: Message UUID to retrieve
            user_id: User identifier for isolation

        Returns:
            Message if found and accessible, None otherwise
        """
        statement = select(Message).where(Message.id == message_id)
        message = self.session.exec(statement).first()

        if not message:
            return None

        # Verify conversation ownership
        if not self._verify_conversation_ownership(message.conversation_id, user_id):
            return None

        return message

    def get_last_mentioned_task_id(
        self,
        conversation_id: UUID,
        user_id: str,
    ) -> Optional[int]:
        """
        Get the most recently mentioned task ID in a conversation.

        Used for resolving "that one" and similar pronoun references.

        Args:
            conversation_id: Conversation UUID
            user_id: User identifier for isolation

        Returns:
            Task ID if found, None otherwise
        """
        # Verify conversation ownership
        if not self._verify_conversation_ownership(conversation_id, user_id):
            return None

        statement = (
            select(Message.last_mentioned_task_id)
            .where(
                Message.conversation_id == conversation_id,
                Message.last_mentioned_task_id != None,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return self.session.exec(statement).first()

    def create_message(
        self,
        conversation_id: UUID,
        user_id: str,
        role: MessageRole,
        content: str,
        last_mentioned_task_id: Optional[int] = None,
        message_metadata: Optional[dict] = None,
    ) -> Optional[Message]:
        """
        Create a new message in a conversation with user isolation.

        Args:
            conversation_id: Target conversation UUID
            user_id: User identifier for isolation
            role: Message role
            content: Message content
            last_mentioned_task_id: Optional task reference
            message_metadata: Optional metadata

        Returns:
            Created message if accessible, None otherwise
        """
        # Verify conversation ownership
        conversation = self._verify_conversation_ownership(conversation_id, user_id)
        if not conversation:
            return None

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            last_mentioned_task_id=last_mentioned_task_id,
            message_metadata=message_metadata or {},
        )

        # Update conversation timestamp
        conversation.last_message_at = datetime.now(timezone.utc)

        self.session.add(message)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(message)

        return message
