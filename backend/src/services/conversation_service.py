"""
Conversation service layer for business logic.

This module provides CRUD operations for conversations with user isolation
enforcement. All operations are scoped to a specific user_id.

Phase III: Conversation History Storage
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from src.models.conversation import Conversation
from src.models.message import Message
from src.models.enums import MessageRole


class ConversationService:
    """
    Service class for conversation operations with user isolation.

    All methods require user_id to ensure data isolation between users.
    """

    def __init__(self, session: Session):
        """Initialize service with database session."""
        self.session = session

    def get_conversations_by_user(
        self,
        user_id: str,
        active_only: bool = False,
    ) -> List[Conversation]:
        """
        Get all conversations for a user.

        Args:
            user_id: User identifier for isolation
            active_only: If True, only return active conversations

        Returns:
            List of conversations belonging to the user
        """
        statement = select(Conversation).where(Conversation.user_id == user_id)

        if active_only:
            statement = statement.where(Conversation.is_active == True)

        statement = statement.order_by(Conversation.last_message_at.desc())
        return list(self.session.exec(statement).all())

    def get_conversation_by_id(
        self,
        conversation_id: UUID,
        user_id: str,
    ) -> Optional[Conversation]:
        """
        Get a specific conversation by ID with user isolation.

        Returns None if conversation doesn't exist or belongs to another user.
        This ensures security by obscurity.

        Args:
            conversation_id: Conversation UUID to retrieve
            user_id: User identifier for isolation

        Returns:
            Conversation if found and accessible, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        return self.session.exec(statement).first()

    def create_conversation(self, user_id: str) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: User identifier

        Returns:
            Created conversation
        """
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def add_message(
        self,
        conversation_id: UUID,
        user_id: str,
        role: MessageRole,
        content: str,
        last_mentioned_task_id: Optional[int] = None,
        message_metadata: Optional[dict] = None,
    ) -> Optional[Message]:
        """
        Add a message to a conversation with user isolation.

        Verifies the conversation belongs to the user before adding.

        Args:
            conversation_id: Target conversation UUID
            user_id: User identifier for isolation
            role: Message role (user/assistant/system)
            content: Message content
            last_mentioned_task_id: Optional task reference
            message_metadata: Optional metadata dict

        Returns:
            Created message if conversation accessible, None otherwise
        """
        # Verify conversation ownership
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None

        # Create message
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

    def deactivate_conversation(
        self,
        conversation_id: UUID,
        user_id: str,
    ) -> bool:
        """
        Deactivate a conversation with user isolation.

        Args:
            conversation_id: Conversation UUID to deactivate
            user_id: User identifier for isolation

        Returns:
            True if deactivated, False if not found or access denied
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        conversation.is_active = False
        self.session.add(conversation)
        self.session.commit()

        return True
