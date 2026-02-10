"""
Integration tests for conversation context reconstruction.

Tests for the ContextService that reconstructs conversation context
for stateless AI agent processing (FR-021, FR-022).

TDD: RED phase - Write tests before implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from src.models.enums import MessageRole, Priority, TaskStatus


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


@pytest.fixture(scope="function")
def sample_user_id():
    """Provide a sample user ID."""
    return "user123"


@pytest.fixture(scope="function")
def sample_conversation(session: Session, sample_user_id: str):
    """Create and return a sample conversation."""
    from src.models.conversation import Conversation

    conv = Conversation(user_id=sample_user_id)
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv


@pytest.fixture(scope="function")
def sample_tasks(session: Session, sample_user_id: str):
    """Create sample tasks for testing."""
    from src.models.task import Task

    tasks = [
        Task(
            user_id=sample_user_id,
            title="Buy groceries",
            priority=Priority.MEDIUM,
            status=TaskStatus.INCOMPLETE,
        ),
        Task(
            user_id=sample_user_id,
            title="Call mom",
            priority=Priority.HIGH,
            status=TaskStatus.INCOMPLETE,
        ),
        Task(
            user_id=sample_user_id,
            title="Finish report",
            priority=Priority.HIGH,
            status=TaskStatus.COMPLETE,
        ),
    ]
    session.add_all(tasks)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


class TestContextReconstruction:
    """Tests for reconstructing conversation context (FR-021)."""

    def test_reconstruct_context_returns_conversation_id(
        self, session: Session, sample_conversation
    ):
        """Context should include the conversation ID."""
        from src.services.context_service import ContextService

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        assert context.conversation_id == sample_conversation.id

    def test_reconstruct_context_returns_messages_in_order(
        self, session: Session, sample_conversation
    ):
        """Context should include messages in chronological order."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        now = datetime.now(timezone.utc)

        # Add messages out of order
        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Second message",
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="First message",
                created_at=now - timedelta(minutes=10),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Third message",
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        assert len(context.messages) == 3
        assert context.messages[0].content == "First message"
        assert context.messages[1].content == "Second message"
        assert context.messages[2].content == "Third message"

    def test_reconstruct_context_limits_to_max_messages(
        self, session: Session, sample_conversation
    ):
        """Context should limit to maximum 50 messages (FR-021)."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        now = datetime.now(timezone.utc)

        # Create 60 messages
        for i in range(60):
            msg = Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}",
                created_at=now - timedelta(minutes=60 - i),
            )
            session.add(msg)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id, max_messages=50)

        assert len(context.messages) == 50
        # Should be the most recent 50 messages
        assert context.messages[0].content == "Message 10"
        assert context.messages[-1].content == "Message 59"

    def test_reconstruct_context_includes_last_mentioned_task_id(
        self, session: Session, sample_conversation, sample_tasks
    ):
        """Context should include the last mentioned task ID (FR-022)."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        now = datetime.now(timezone.utc)

        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Show my tasks",
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Here are your tasks...",
                last_mentioned_task_id=sample_tasks[0].id,
                created_at=now - timedelta(minutes=4),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Complete that one",
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        assert context.last_mentioned_task_id == sample_tasks[0].id

    def test_reconstruct_context_finds_most_recent_task_mention(
        self, session: Session, sample_conversation, sample_tasks
    ):
        """Context should find the most recently mentioned task."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        now = datetime.now(timezone.utc)

        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Task 1 mentioned",
                last_mentioned_task_id=sample_tasks[0].id,
                created_at=now - timedelta(minutes=10),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Task 2 mentioned",
                last_mentioned_task_id=sample_tasks[1].id,
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Complete that one",
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        # Should be the most recent task mention
        assert context.last_mentioned_task_id == sample_tasks[1].id

    def test_reconstruct_context_with_no_task_mentions(
        self, session: Session, sample_conversation
    ):
        """Context should have None for last_mentioned_task_id if no tasks mentioned."""
        from src.models.message import Message
        from src.services.context_service import ContextService

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

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        assert context.last_mentioned_task_id is None


class TestPendingOperationRetrieval:
    """Tests for retrieving pending operations from context (FR-022)."""

    def test_reconstruct_context_includes_pending_operation(
        self, session: Session, sample_conversation, sample_tasks
    ):
        """Context should include pending operation awaiting confirmation."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        now = datetime.now(timezone.utc)

        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Delete all completed tasks",
                created_at=now - timedelta(minutes=2),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Are you sure you want to delete these tasks?",
                message_metadata={
                    "pending_operation": {
                        "operation": "bulk_delete",
                        "task_ids": [sample_tasks[2].id],
                    }
                },
                created_at=now - timedelta(minutes=1),
            ),
        ]
        session.add_all(messages)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        assert context.pending_operation is not None
        assert context.pending_operation.operation == "bulk_delete"
        assert sample_tasks[2].id in context.pending_operation.task_ids

    def test_reconstruct_context_no_pending_operation_when_none(
        self, session: Session, sample_conversation
    ):
        """Context should have None for pending_operation when no operation pending."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="Show my tasks",
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Here are your tasks...",
            ),
        ]
        session.add_all(messages)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        assert context.pending_operation is None

    def test_pending_operation_only_from_most_recent_message(
        self, session: Session, sample_conversation, sample_tasks
    ):
        """Only the most recent pending operation should be included."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        now = datetime.now(timezone.utc)

        messages = [
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="Old pending operation",
                message_metadata={
                    "pending_operation": {
                        "operation": "delete",
                        "task_ids": [sample_tasks[0].id],
                    }
                },
                created_at=now - timedelta(minutes=10),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER,
                content="No, cancel that. Delete task 2 instead",
                created_at=now - timedelta(minutes=5),
            ),
            Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.ASSISTANT,
                content="New pending operation",
                message_metadata={
                    "pending_operation": {
                        "operation": "delete",
                        "task_ids": [sample_tasks[1].id],
                    }
                },
                created_at=now,
            ),
        ]
        session.add_all(messages)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        # Should be the most recent pending operation
        assert context.pending_operation.task_ids == [sample_tasks[1].id]


class TestContextReconstructionEdgeCases:
    """Edge case tests for context reconstruction."""

    def test_reconstruct_context_empty_conversation(
        self, session: Session, sample_conversation
    ):
        """Should handle conversation with no messages."""
        from src.services.context_service import ContextService

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id)

        assert context.conversation_id == sample_conversation.id
        assert len(context.messages) == 0
        assert context.last_mentioned_task_id is None
        assert context.pending_operation is None

    def test_reconstruct_context_nonexistent_conversation(self, session: Session):
        """Should raise error for nonexistent conversation."""
        from src.services.context_service import ContextService

        service = ContextService(session)
        fake_id = uuid4()

        with pytest.raises(ValueError, match="Conversation not found"):
            service.reconstruct_context(fake_id)

    def test_reconstruct_context_custom_max_messages(
        self, session: Session, sample_conversation
    ):
        """Should respect custom max_messages parameter."""
        from src.models.message import Message
        from src.services.context_service import ContextService

        now = datetime.now(timezone.utc)

        # Create 10 messages
        for i in range(10):
            msg = Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}",
                created_at=now - timedelta(minutes=10 - i),
            )
            session.add(msg)
        session.commit()

        service = ContextService(session)
        context = service.reconstruct_context(sample_conversation.id, max_messages=5)

        assert len(context.messages) == 5
        # Should be the most recent 5
        assert context.messages[0].content == "Message 5"
        assert context.messages[-1].content == "Message 9"


class TestContextServicePerformance:
    """Performance tests for context reconstruction (SC-002: <50ms)."""

    def test_context_reconstruction_with_many_messages(
        self, session: Session, sample_conversation
    ):
        """Context reconstruction should handle many messages efficiently."""
        from src.models.message import Message
        from src.services.context_service import ContextService
        import time

        now = datetime.now(timezone.utc)

        # Create 100 messages
        messages = []
        for i in range(100):
            msg = Message(
                conversation_id=sample_conversation.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}",
                created_at=now - timedelta(minutes=100 - i),
                last_mentioned_task_id=i % 10 if i % 5 == 0 else None,
            )
            messages.append(msg)
        session.add_all(messages)
        session.commit()

        service = ContextService(session)

        # Measure reconstruction time
        start = time.time()
        context = service.reconstruct_context(sample_conversation.id, max_messages=50)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert len(context.messages) == 50
        # Note: Actual performance testing should be done with proper benchmarking
        # This is a basic sanity check
        assert elapsed < 1000  # Should complete within 1 second in test environment
