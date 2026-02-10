"""
Unit tests for Message-Task foreign key relationship.

Tests for the last_mentioned_task_id field in Message model
that links messages to tasks for context resolution.

TDD: RED phase - Write tests before implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from src.models.enums import MessageRole, Priority, TaskStatus


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
def sample_task(session: Session):
    """Create and return a sample task for testing."""
    from src.models.task import Task

    task = Task(
        user_id="user123",
        title="Sample task for message linking",
        is_completed=False,
        priority=Priority.MEDIUM,
        status=TaskStatus.INCOMPLETE,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(scope="function")
def sample_conversation(session: Session):
    """Create and return a sample conversation for testing."""
    from src.models.conversation import Conversation

    conv = Conversation(user_id="user123")
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv


class TestMessageTaskForeignKey:
    """Tests for Message.last_mentioned_task_id FK relationship."""

    def test_message_can_reference_task(self, session: Session, sample_task, sample_conversation):
        """Message should be able to reference a task via last_mentioned_task_id."""
        from src.models.message import Message

        msg = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.ASSISTANT,
            content=f"Completed task: {sample_task.title}",
            last_mentioned_task_id=sample_task.id,
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.last_mentioned_task_id == sample_task.id

    def test_message_task_reference_is_optional(self, session: Session, sample_conversation):
        """Message should not require a task reference."""
        from src.models.message import Message

        msg = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content="Hello, what are my tasks?",
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.last_mentioned_task_id is None

    def test_multiple_messages_can_reference_same_task(
        self, session: Session, sample_task, sample_conversation
    ):
        """Multiple messages should be able to reference the same task."""
        from src.models.message import Message

        msg1 = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Here is task 1",
            last_mentioned_task_id=sample_task.id,
        )
        msg2 = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Task 1 updated",
            last_mentioned_task_id=sample_task.id,
        )

        session.add_all([msg1, msg2])
        session.commit()

        # Query messages referencing this task
        statement = select(Message).where(Message.last_mentioned_task_id == sample_task.id)
        results = session.exec(statement).all()

        assert len(results) == 2

    def test_query_messages_by_task_reference(
        self, session: Session, sample_conversation
    ):
        """Should be able to query all messages that reference a specific task."""
        from src.models.task import Task
        from src.models.message import Message

        # Create multiple tasks
        task1 = Task(user_id="user123", title="Task 1")
        task2 = Task(user_id="user123", title="Task 2")
        session.add_all([task1, task2])
        session.commit()

        # Create messages referencing different tasks
        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="About task 1",
                last_mentioned_task_id=task1.id,
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="More about task 1",
                last_mentioned_task_id=task1.id,
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="About task 2",
                last_mentioned_task_id=task2.id,
            ),
        ]
        session.add_all(messages)
        session.commit()

        # Query messages for task1
        statement = select(Message).where(Message.last_mentioned_task_id == task1.id)
        results = session.exec(statement).all()

        assert len(results) == 2
        for msg in results:
            assert msg.last_mentioned_task_id == task1.id


class TestLastMentionedTaskResolution:
    """Tests for finding the last mentioned task in a conversation."""

    def test_get_last_mentioned_task_id_from_conversation(
        self, session: Session, sample_conversation
    ):
        """Should find the most recently mentioned task in a conversation."""
        from src.models.task import Task
        from src.models.message import Message

        # Create tasks
        task1 = Task(user_id="user123", title="Task 1")
        task2 = Task(user_id="user123", title="Task 2")
        task3 = Task(user_id="user123", title="Task 3")
        session.add_all([task1, task2, task3])
        session.commit()

        now = datetime.now(timezone.utc)

        # Create messages mentioning tasks in order
        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Created task 1",
                last_mentioned_task_id=task1.id,
                created_at=now - timedelta(minutes=10),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Created task 2",
                last_mentioned_task_id=task2.id,
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Created task 3",
                last_mentioned_task_id=task3.id,
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        # Query for most recent task reference
        statement = (
            select(Message.last_mentioned_task_id)
            .where(
                Message.conversation_id == sample_conversation.id,
                Message.last_mentioned_task_id != None,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = session.exec(statement).first()

        assert result == task3.id

    def test_last_mentioned_task_excludes_none_values(
        self, session: Session, sample_conversation
    ):
        """Query for last mentioned task should skip messages without task reference."""
        from src.models.task import Task
        from src.models.message import Message

        task1 = Task(user_id="user123", title="Task 1")
        session.add(task1)
        session.commit()

        now = datetime.now(timezone.utc)

        # Mix of messages with and without task references
        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Mentioned task 1",
                last_mentioned_task_id=task1.id,
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Thanks!",
                last_mentioned_task_id=None,  # No task reference
                created_at=now - timedelta(minutes=4),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="You're welcome!",
                last_mentioned_task_id=None,  # No task reference
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        # Query for most recent task reference (should be task1)
        statement = (
            select(Message.last_mentioned_task_id)
            .where(
                Message.conversation_id == sample_conversation.id,
                Message.last_mentioned_task_id != None,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = session.exec(statement).first()

        assert result == task1.id

    def test_no_task_mentioned_returns_none(self, session: Session, sample_conversation):
        """Should return None when no tasks have been mentioned in conversation."""
        from src.models.message import Message

        # Messages without task references
        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Hello",
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Hi there!",
            ),
        ]
        session.add_all(messages)
        session.commit()

        # Query for most recent task reference
        statement = (
            select(Message.last_mentioned_task_id)
            .where(
                Message.conversation_id == sample_conversation.id,
                Message.last_mentioned_task_id != None,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = session.exec(statement).first()

        assert result is None


class TestMessageMetadataForTaskContext:
    """Tests for Message.message_metadata storing task-related context."""

    def test_message_metadata_stores_task_list(
        self, session: Session, sample_conversation
    ):
        """Message metadata should store list of displayed tasks."""
        from src.models.message import Message

        msg = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Here are your tasks: 1. Buy groceries 2. Call mom",
            message_metadata={
                "displayed_tasks": [1, 2],
                "action": "list_tasks",
            },
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.message_metadata["displayed_tasks"] == [1, 2]
        assert msg.message_metadata["action"] == "list_tasks"

    def test_message_metadata_stores_action_type(
        self, session: Session, sample_conversation
    ):
        """Message metadata should store the action type performed."""
        from src.models.message import Message

        msg = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Task completed!",
            last_mentioned_task_id=1,
            message_metadata={
                "action": "complete_task",
                "task_id": 1,
                "previous_status": "incomplete",
            },
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        assert msg.message_metadata["action"] == "complete_task"
        assert msg.message_metadata["task_id"] == 1

    def test_message_metadata_stores_pending_operation(
        self, session: Session, sample_conversation
    ):
        """Message metadata should store pending operation for confirmation."""
        from src.models.message import Message

        msg = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Are you sure you want to delete these 3 tasks?",
            message_metadata={
                "pending_operation": {
                    "type": "bulk_delete",
                    "task_ids": [1, 2, 3],
                    "awaiting_confirmation": True,
                }
            },
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)

        pending = msg.message_metadata["pending_operation"]
        assert pending["type"] == "bulk_delete"
        assert pending["task_ids"] == [1, 2, 3]
        assert pending["awaiting_confirmation"] is True

    def test_retrieve_last_pending_operation(
        self, session: Session, sample_conversation
    ):
        """Should be able to find the last pending operation in conversation."""
        from src.models.message import Message

        now = datetime.now(timezone.utc)

        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Some message",
                message_metadata={},
                created_at=now - timedelta(minutes=10),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Delete these?",
                message_metadata={
                    "pending_operation": {
                        "type": "bulk_delete",
                        "task_ids": [1, 2],
                    }
                },
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Yes",
                message_metadata={},
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        # Query for messages with pending operations
        # Note: SQLite JSON support is limited, this is a simplified test
        statement = (
            select(Message)
            .where(Message.conversation_id == sample_conversation.id)
            .order_by(Message.created_at.desc())
        )
        results = session.exec(statement).all()

        # Find last message with pending operation
        pending_op = None
        for msg in results:
            if msg.message_metadata and "pending_operation" in msg.message_metadata:
                pending_op = msg.message_metadata["pending_operation"]
                break

        assert pending_op is not None
        assert pending_op["type"] == "bulk_delete"
        assert pending_op["task_ids"] == [1, 2]
