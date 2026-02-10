"""
Unit tests for Message model.

Tests for the Message SQLModel including field validation,
role constraints, and relationship to conversations.

TDD: RED phase - Write tests before implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from src.models.enums import MessageRole


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


@pytest.fixture(scope="function")
def conversation_id():
    """Provide a sample conversation UUID."""
    return uuid4()  # Return UUID object, not string


class TestMessageModelFields:
    """Tests for Message model field definitions (FR-011 to FR-015)."""

    def test_message_has_id_field(self, conversation_id):
        """Message model should have a UUID id field."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello",
        )
        assert hasattr(msg, "id")

    def test_message_has_conversation_id_field(self, conversation_id):
        """Message model should have a conversation_id foreign key."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello",
        )
        assert hasattr(msg, "conversation_id")
        assert msg.conversation_id == conversation_id

    def test_message_has_role_field(self, conversation_id):
        """Message model should have a role field."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Hello",
        )
        assert hasattr(msg, "role")
        assert msg.role == MessageRole.ASSISTANT

    def test_message_has_content_field(self, conversation_id):
        """Message model should have a content field."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Test content",
        )
        assert hasattr(msg, "content")
        assert msg.content == "Test content"

    def test_message_has_created_at_field(self, conversation_id):
        """Message model should have a created_at timestamp."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello",
        )
        assert hasattr(msg, "created_at")
        assert msg.created_at is not None

    def test_message_has_last_mentioned_task_id_field(self, conversation_id):
        """Message model should have a last_mentioned_task_id field."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Task completed",
            last_mentioned_task_id=42,
        )
        assert hasattr(msg, "last_mentioned_task_id")
        assert msg.last_mentioned_task_id == 42

    def test_message_last_mentioned_task_id_is_optional(self, conversation_id):
        """Message last_mentioned_task_id should be optional."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello",
        )
        assert msg.last_mentioned_task_id is None

    def test_message_has_metadata_field(self, conversation_id):
        """Message model should have a metadata JSONB field."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Hello",
            message_metadata={"action": "list_tasks", "count": 5},
        )
        assert hasattr(msg, "message_metadata")
        assert msg.message_metadata == {"action": "list_tasks", "count": 5}

    def test_message_metadata_default_is_empty_dict(self, conversation_id):
        """Message metadata should default to empty dict."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello",
        )
        assert msg.message_metadata == {}


class TestMessageModelRoles:
    """Tests for Message role validation (FR-013)."""

    def test_message_user_role(self, conversation_id):
        """Message should accept USER role."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="User message",
        )
        assert msg.role == MessageRole.USER
        assert msg.role == "user"

    def test_message_assistant_role(self, conversation_id):
        """Message should accept ASSISTANT role."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Assistant message",
        )
        assert msg.role == MessageRole.ASSISTANT
        assert msg.role == "assistant"

    def test_message_system_role(self, conversation_id):
        """Message should accept SYSTEM role."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.SYSTEM,
            content="System message",
        )
        assert msg.role == MessageRole.SYSTEM
        assert msg.role == "system"


class TestMessageModelPersistence:
    """Tests for Message persistence operations."""

    def test_create_message(self, session: Session, conversation_id):
        """Should create and persist a message."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello world",
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.id is not None

    def test_message_id_is_uuid(self, session: Session, conversation_id):
        """Message id should be a valid UUID string."""
        from src.models.message import Message
        from uuid import UUID

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello",
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        # Should be parseable as UUID
        UUID(str(msg.id))

    def test_read_message_by_id(self, session: Session, conversation_id):
        """Should read message by id."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Test message",
        )
        session.add(msg)
        session.commit()

        statement = select(Message).where(Message.id == msg.id)
        result = session.exec(statement).first()

        assert result is not None
        assert result.content == "Test message"

    def test_read_messages_by_conversation_id(self, session: Session, conversation_id):
        """Should read all messages for a conversation."""
        from src.models.message import Message

        other_conv_id = uuid4()  # Use UUID object, not string

        msg1 = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Message 1",
        )
        msg2 = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Message 2",
        )
        msg3 = Message(
            conversation_id=other_conv_id,
            role=MessageRole.USER,
            content="Other conversation",
        )

        session.add_all([msg1, msg2, msg3])
        session.commit()

        statement = select(Message).where(Message.conversation_id == conversation_id)
        results = session.exec(statement).all()

        assert len(results) == 2
        for msg in results:
            assert msg.conversation_id == conversation_id

    def test_create_message_with_task_reference(self, session: Session, conversation_id):
        """Should create message with task reference."""
        from src.models.message import Message

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Marked task as complete",
            last_mentioned_task_id=42,
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.last_mentioned_task_id == 42

    def test_create_message_with_metadata(self, session: Session, conversation_id):
        """Should create message with metadata."""
        from src.models.message import Message

        metadata = {"action": "create_task", "task_id": 10}
        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Created task",
            message_metadata=metadata,
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.message_metadata == metadata


class TestMessageModelOrdering:
    """Tests for message ordering (chronological retrieval)."""

    def test_messages_order_by_created_at(self, session: Session, conversation_id):
        """Should order messages by created_at ascending."""
        from src.models.message import Message

        now = datetime.now(timezone.utc)

        msg1 = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="First",
            created_at=now - timedelta(minutes=10),
        )
        msg2 = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Second",
            created_at=now - timedelta(minutes=5),
        )
        msg3 = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Third",
            created_at=now,
        )

        session.add_all([msg2, msg3, msg1])  # Add out of order
        session.commit()

        # Query with ordering
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        results = session.exec(statement).all()

        assert len(results) == 3
        assert results[0].content == "First"
        assert results[1].content == "Second"
        assert results[2].content == "Third"

    def test_messages_chronological_retrieval(self, session: Session, conversation_id):
        """Should retrieve messages in chronological order for context."""
        from src.models.message import Message

        now = datetime.now(timezone.utc)

        # Simulate a conversation
        messages = [
            Message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Show my tasks",
                created_at=now - timedelta(minutes=4),
            ),
            Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="You have 3 tasks",
                created_at=now - timedelta(minutes=3),
            ),
            Message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Complete the first one",
                created_at=now - timedelta(minutes=2),
            ),
            Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Done!",
                created_at=now - timedelta(minutes=1),
                last_mentioned_task_id=1,
            ),
        ]

        session.add_all(messages)
        session.commit()

        # Retrieve in chronological order
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        results = session.exec(statement).all()

        assert len(results) == 4
        # Verify alternating roles
        assert results[0].role == MessageRole.USER
        assert results[1].role == MessageRole.ASSISTANT
        assert results[2].role == MessageRole.USER
        assert results[3].role == MessageRole.ASSISTANT
        # Verify last message has task reference
        assert results[3].last_mentioned_task_id == 1


class TestMessageModelContent:
    """Tests for message content handling."""

    def test_message_content_can_be_long(self, session: Session, conversation_id):
        """Message content should support long text."""
        from src.models.message import Message

        long_content = "x" * 10000  # 10KB of content
        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=long_content,
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert len(msg.content) == 10000

    def test_message_content_preserves_formatting(self, session: Session, conversation_id):
        """Message content should preserve newlines and formatting."""
        from src.models.message import Message

        formatted_content = """Here are your tasks:
1. Buy groceries
2. Call mom
3. Finish report

Would you like to complete any of these?"""

        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=formatted_content,
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.content == formatted_content
        assert "\n" in msg.content
