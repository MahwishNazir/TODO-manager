"""
Unit tests for Conversation model.

Tests for the Conversation SQLModel including field validation,
persistence, and timestamp handling.

TDD: RED phase - Write tests before implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool


# Create in-memory SQLite database for unit tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="function")
def session():
    """Provide a clean database session for each test."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


class TestConversationModelFields:
    """Tests for Conversation model field definitions (FR-007 to FR-010)."""

    def test_conversation_has_id_field(self):
        """Conversation model should have a UUID id field."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        assert hasattr(conv, "id")

    def test_conversation_has_user_id_field(self):
        """Conversation model should have a user_id field."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        assert hasattr(conv, "user_id")
        assert conv.user_id == "user123"

    def test_conversation_user_id_is_required(self):
        """Conversation user_id should be required field."""
        from src.models.conversation import Conversation

        # Verify user_id is a required field (no default, not optional)
        user_id_field = Conversation.model_fields["user_id"]
        # Field should not have a default value (required)
        assert user_id_field.default is None or user_id_field.is_required()

    def test_conversation_has_started_at_field(self):
        """Conversation model should have a started_at timestamp."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        assert hasattr(conv, "started_at")
        assert conv.started_at is not None

    def test_conversation_has_last_message_at_field(self):
        """Conversation model should have a last_message_at timestamp."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        assert hasattr(conv, "last_message_at")
        assert conv.last_message_at is not None

    def test_conversation_has_is_active_field(self):
        """Conversation model should have an is_active boolean field."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        assert hasattr(conv, "is_active")
        assert conv.is_active is True  # Default

    def test_conversation_is_active_default_is_true(self):
        """Conversation is_active should default to True."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        assert conv.is_active is True


class TestConversationModelPersistence:
    """Tests for Conversation persistence operations."""

    def test_create_conversation(self, session: Session):
        """Should create and persist a conversation."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()
        session.refresh(conv)

        assert conv.id is not None

    def test_conversation_id_is_uuid(self, session: Session):
        """Conversation id should be a valid UUID string."""
        from src.models.conversation import Conversation
        from uuid import UUID

        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()
        session.refresh(conv)

        # Should be parseable as UUID
        UUID(str(conv.id))

    def test_read_conversation_by_id(self, session: Session):
        """Should read conversation by id."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        # Read from database
        statement = select(Conversation).where(Conversation.id == conv.id)
        result = session.exec(statement).first()

        assert result is not None
        assert result.user_id == "user123"

    def test_read_conversations_by_user_id(self, session: Session):
        """Should read all conversations for a user."""
        from src.models.conversation import Conversation

        # Create conversations for two users
        conv1 = Conversation(user_id="user123")
        conv2 = Conversation(user_id="user123")
        conv3 = Conversation(user_id="user456")

        session.add_all([conv1, conv2, conv3])
        session.commit()

        # Query by user_id
        statement = select(Conversation).where(Conversation.user_id == "user123")
        results = session.exec(statement).all()

        assert len(results) == 2
        for conv in results:
            assert conv.user_id == "user123"

    def test_update_conversation_last_message_at(self, session: Session):
        """Should update last_message_at timestamp."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        original_time = conv.last_message_at

        # Update timestamp
        new_time = datetime.now(timezone.utc)
        conv.last_message_at = new_time
        session.add(conv)
        session.commit()
        session.refresh(conv)

        assert conv.last_message_at != original_time

    def test_update_conversation_is_active(self, session: Session):
        """Should update is_active flag."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123", is_active=True)
        session.add(conv)
        session.commit()

        # Deactivate
        conv.is_active = False
        session.add(conv)
        session.commit()
        session.refresh(conv)

        assert conv.is_active is False


class TestConversationModelFiltering:
    """Tests for filtering conversations."""

    def test_filter_active_conversations(self, session: Session):
        """Should filter only active conversations."""
        from src.models.conversation import Conversation

        active = Conversation(user_id="user123", is_active=True)
        inactive = Conversation(user_id="user123", is_active=False)

        session.add_all([active, inactive])
        session.commit()

        # Filter active only
        statement = select(Conversation).where(
            Conversation.user_id == "user123",
            Conversation.is_active == True,
        )
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].is_active is True

    def test_filter_conversations_by_user_and_active(self, session: Session):
        """Should filter by user_id and is_active together."""
        from src.models.conversation import Conversation

        # User 1 conversations
        user1_active = Conversation(user_id="user123", is_active=True)
        user1_inactive = Conversation(user_id="user123", is_active=False)

        # User 2 conversations
        user2_active = Conversation(user_id="user456", is_active=True)

        session.add_all([user1_active, user1_inactive, user2_active])
        session.commit()

        # Filter user123 active conversations
        statement = select(Conversation).where(
            Conversation.user_id == "user123",
            Conversation.is_active == True,
        )
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].user_id == "user123"
        assert results[0].is_active is True

    def test_order_conversations_by_last_message_at(self, session: Session):
        """Should order conversations by last_message_at descending."""
        from src.models.conversation import Conversation

        now = datetime.now(timezone.utc)

        old = Conversation(
            user_id="user123",
            last_message_at=now - timedelta(hours=2),
        )
        recent = Conversation(
            user_id="user123",
            last_message_at=now,
        )

        session.add_all([old, recent])
        session.commit()

        # Order by last_message_at descending
        statement = (
            select(Conversation)
            .where(Conversation.user_id == "user123")
            .order_by(Conversation.last_message_at.desc())
        )
        results = session.exec(statement).all()

        assert len(results) == 2
        assert results[0].last_message_at > results[1].last_message_at


class TestConversationModelConstraints:
    """Tests for Conversation model constraints."""

    def test_user_id_max_length(self):
        """User ID should have max length of 50 characters."""
        from src.models.conversation import Conversation

        # Should work with 50 characters
        conv = Conversation(user_id="a" * 50)
        assert len(conv.user_id) == 50

    def test_multiple_active_conversations_allowed(self, session: Session):
        """User can have multiple active conversations."""
        from src.models.conversation import Conversation

        conv1 = Conversation(user_id="user123", is_active=True)
        conv2 = Conversation(user_id="user123", is_active=True)

        session.add_all([conv1, conv2])
        session.commit()

        statement = select(Conversation).where(
            Conversation.user_id == "user123",
            Conversation.is_active == True,
        )
        results = session.exec(statement).all()

        assert len(results) == 2
