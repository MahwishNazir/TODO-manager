"""
Integration tests for conversation lifecycle.

Tests for creating conversations, adding messages, and
verifying chronological retrieval of conversation history.

TDD: RED phase - Write tests before implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from src.models.enums import MessageRole


# Create in-memory SQLite database for integration tests
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


class TestConversationCreation:
    """Tests for conversation creation workflow."""

    def test_create_new_conversation_for_user(self, session: Session):
        """Should create a new conversation for a user."""
        from src.models.conversation import Conversation

        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()
        session.refresh(conv)

        assert conv.id is not None
        assert conv.user_id == "user123"
        assert conv.is_active is True

    def test_conversation_has_timestamps_on_creation(self, session: Session):
        """Conversation should have started_at and last_message_at set on creation."""
        from src.models.conversation import Conversation

        before = datetime.now(timezone.utc)
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()
        session.refresh(conv)
        after = datetime.now(timezone.utc)

        assert conv.started_at is not None
        assert conv.last_message_at is not None

    def test_user_can_have_multiple_conversations(self, session: Session):
        """User should be able to have multiple conversations."""
        from src.models.conversation import Conversation

        conv1 = Conversation(user_id="user123")
        conv2 = Conversation(user_id="user123")
        conv3 = Conversation(user_id="user123")

        session.add_all([conv1, conv2, conv3])
        session.commit()

        statement = select(Conversation).where(Conversation.user_id == "user123")
        results = session.exec(statement).all()

        assert len(results) == 3


class TestAddingMessages:
    """Tests for adding messages to conversations."""

    def test_add_user_message_to_conversation(self, session: Session):
        """Should add a user message to a conversation."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create conversation
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()
        session.refresh(conv)

        # Add message
        msg = Message(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Hello, what are my tasks?",
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.id is not None
        assert msg.conversation_id == conv.id

    def test_add_assistant_response_to_conversation(self, session: Session):
        """Should add an assistant response to a conversation."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create conversation
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        # Add user message
        user_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Show my tasks",
        )
        session.add(user_msg)
        session.commit()

        # Add assistant response
        assistant_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.ASSISTANT,
            content="You have 3 tasks: 1. Buy groceries 2. Call mom 3. Finish report",
        )
        session.add(assistant_msg)
        session.commit()
        session.refresh(assistant_msg)

        assert assistant_msg.id is not None
        assert assistant_msg.role == MessageRole.ASSISTANT

    def test_conversation_message_count(self, session: Session):
        """Should track correct number of messages in conversation."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create conversation
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        # Add multiple messages
        messages = [
            Message(conversation_id=conv.id, role=MessageRole.USER, content="Hi"),
            Message(conversation_id=conv.id, role=MessageRole.ASSISTANT, content="Hello!"),
            Message(conversation_id=conv.id, role=MessageRole.USER, content="Tasks?"),
            Message(conversation_id=conv.id, role=MessageRole.ASSISTANT, content="Here are your tasks..."),
        ]
        session.add_all(messages)
        session.commit()

        # Count messages
        statement = select(Message).where(Message.conversation_id == conv.id)
        results = session.exec(statement).all()

        assert len(results) == 4


class TestChronologicalRetrieval:
    """Tests for retrieving messages in chronological order."""

    def test_retrieve_messages_in_order(self, session: Session):
        """Should retrieve messages in chronological order."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create conversation
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        now = datetime.now(timezone.utc)

        # Add messages with explicit timestamps
        messages = [
            Message(
                conversation_id=conv.id,
                role=MessageRole.USER,
                content="Message 1",
                created_at=now - timedelta(minutes=10),
            ),
            Message(
                conversation_id=conv.id,
                role=MessageRole.ASSISTANT,
                content="Message 2",
                created_at=now - timedelta(minutes=9),
            ),
            Message(
                conversation_id=conv.id,
                role=MessageRole.USER,
                content="Message 3",
                created_at=now - timedelta(minutes=8),
            ),
        ]
        session.add_all(messages)
        session.commit()

        # Retrieve in order
        statement = (
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
        )
        results = session.exec(statement).all()

        assert results[0].content == "Message 1"
        assert results[1].content == "Message 2"
        assert results[2].content == "Message 3"

    def test_context_window_limit(self, session: Session):
        """Should limit context to last N messages."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create conversation
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        now = datetime.now(timezone.utc)
        max_context = 5

        # Add more messages than context window
        for i in range(10):
            msg = Message(
                conversation_id=conv.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}",
                created_at=now - timedelta(minutes=10 - i),
            )
            session.add(msg)
        session.commit()

        # Retrieve last N messages
        statement = (
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(max_context)
        )
        results = session.exec(statement).all()

        # Reverse to get chronological order
        results = list(reversed(results))

        assert len(results) == max_context
        assert results[0].content == "Message 5"  # First of last 5
        assert results[-1].content == "Message 9"  # Last message


class TestConversationDeactivation:
    """Tests for deactivating conversations."""

    def test_deactivate_conversation(self, session: Session):
        """Should deactivate a conversation."""
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

    def test_get_only_active_conversations(self, session: Session):
        """Should retrieve only active conversations for user."""
        from src.models.conversation import Conversation

        active1 = Conversation(user_id="user123", is_active=True)
        active2 = Conversation(user_id="user123", is_active=True)
        inactive = Conversation(user_id="user123", is_active=False)

        session.add_all([active1, active2, inactive])
        session.commit()

        # Get only active
        statement = select(Conversation).where(
            Conversation.user_id == "user123",
            Conversation.is_active == True,
        )
        results = session.exec(statement).all()

        assert len(results) == 2
        for conv in results:
            assert conv.is_active is True


class TestConversationWithTaskReferences:
    """Tests for conversations with task references in messages."""

    def test_message_tracks_last_mentioned_task(self, session: Session):
        """Should track last mentioned task in assistant messages."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create conversation
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        # Add messages with task reference
        user_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Complete task 1",
        )
        assistant_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.ASSISTANT,
            content="Done! I've marked 'Buy groceries' as complete.",
            last_mentioned_task_id=1,
        )

        session.add_all([user_msg, assistant_msg])
        session.commit()

        # Verify task reference
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conv.id,
                Message.last_mentioned_task_id != None,
            )
        )
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].last_mentioned_task_id == 1

    def test_get_last_mentioned_task_from_conversation(self, session: Session):
        """Should find the last mentioned task in a conversation."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        now = datetime.now(timezone.utc)

        # Create conversation
        conv = Conversation(user_id="user123")
        session.add(conv)
        session.commit()

        # Add messages mentioning different tasks
        messages = [
            Message(
                conversation_id=conv.id,
                role=MessageRole.ASSISTANT,
                content="Task 1 created",
                last_mentioned_task_id=1,
                created_at=now - timedelta(minutes=10),
            ),
            Message(
                conversation_id=conv.id,
                role=MessageRole.ASSISTANT,
                content="Task 2 created",
                last_mentioned_task_id=2,
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=conv.id,
                role=MessageRole.ASSISTANT,
                content="Task 3 completed",
                last_mentioned_task_id=3,
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        # Get the most recent message with task reference
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conv.id,
                Message.last_mentioned_task_id != None,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = session.exec(statement).first()

        assert result is not None
        assert result.last_mentioned_task_id == 3


class TestUserIsolation:
    """Tests for user isolation in conversations."""

    def test_conversations_isolated_by_user(self, session: Session):
        """Conversations should be isolated by user_id."""
        from src.models.conversation import Conversation

        conv1 = Conversation(user_id="user123")
        conv2 = Conversation(user_id="user456")

        session.add_all([conv1, conv2])
        session.commit()

        # Query for user123
        statement = select(Conversation).where(Conversation.user_id == "user123")
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].user_id == "user123"

    def test_messages_accessible_only_via_conversation(self, session: Session):
        """Messages should only be accessible through their conversation."""
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create conversations for different users
        conv1 = Conversation(user_id="user123")
        conv2 = Conversation(user_id="user456")
        session.add_all([conv1, conv2])
        session.commit()

        # Add messages to each
        msg1 = Message(
            conversation_id=conv1.id,
            role=MessageRole.USER,
            content="User 1 message",
        )
        msg2 = Message(
            conversation_id=conv2.id,
            role=MessageRole.USER,
            content="User 2 message",
        )
        session.add_all([msg1, msg2])
        session.commit()

        # Query messages for conv1 only
        statement = select(Message).where(Message.conversation_id == conv1.id)
        results = session.exec(statement).all()

        assert len(results) == 1
        assert results[0].content == "User 1 message"
