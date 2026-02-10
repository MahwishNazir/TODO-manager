"""
Integration tests for service-level user data isolation.

Tests for ensuring complete data isolation between users
at the service layer with user_id scoping (FR-006, SC-003, SC-004).

TDD: Tests for Phase 6 User Story 4 - User Data Isolation
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
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
def user1_id():
    """First user ID for isolation tests."""
    return "user_alice_123"


@pytest.fixture(scope="function")
def user2_id():
    """Second user ID for isolation tests."""
    return "user_bob_456"


class TestTaskServiceIsolation:
    """Tests for TaskService isolation by user_id (T037)."""

    def test_user_can_only_see_own_tasks(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should only see their own tasks."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create tasks for both users
        user1_task = Task(user_id=user1_id, title="Alice task")
        user2_task = Task(user_id=user2_id, title="Bob task")
        session.add_all([user1_task, user2_task])
        session.commit()

        # Query using service with user1 ID
        service = TaskService(session)
        user1_tasks = service.get_tasks_by_user(user1_id)

        assert len(user1_tasks) == 1
        assert user1_tasks[0].title == "Alice task"
        assert user1_tasks[0].user_id == user1_id

    def test_user_cannot_access_other_users_task_by_id(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should not be able to access another users task by ID."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create task for user2
        user2_task = Task(user_id=user2_id, title="Bob private task")
        session.add(user2_task)
        session.commit()
        session.refresh(user2_task)

        # User1 tries to access user2 task
        service = TaskService(session)
        result = service.get_task_by_id(user2_task.id, user1_id)

        # Should return None (security by obscurity)
        assert result is None

    def test_user_can_access_own_task_by_id(
        self, session: Session, user1_id: str
    ):
        """User should be able to access their own task by ID."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create task for user1
        task = Task(user_id=user1_id, title="Alice task")
        session.add(task)
        session.commit()
        session.refresh(task)

        # User1 accesses own task
        service = TaskService(session)
        result = service.get_task_by_id(task.id, user1_id)

        assert result is not None
        assert result.title == "Alice task"

    def test_user_cannot_update_other_users_task(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should not be able to update another users task."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create task for user2
        user2_task = Task(user_id=user2_id, title="Bob task")
        session.add(user2_task)
        session.commit()
        session.refresh(user2_task)

        # User1 tries to update user2 task
        service = TaskService(session)
        result = service.update_task(
            task_id=user2_task.id,
            user_id=user1_id,
            title="Hacked by Alice",
        )

        # Should return None (task not found for this user)
        assert result is None

        # Verify original task unchanged
        session.refresh(user2_task)
        assert user2_task.title == "Bob task"

    def test_user_cannot_delete_other_users_task(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should not be able to delete another users task."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create task for user2
        user2_task = Task(user_id=user2_id, title="Bob task")
        session.add(user2_task)
        session.commit()
        session.refresh(user2_task)
        task_id = user2_task.id

        # User1 tries to delete user2 task
        service = TaskService(session)
        result = service.delete_task(task_id, user1_id)

        # Should return False (task not found for this user)
        assert result is False

        # Verify task still exists
        statement = select(Task).where(Task.id == task_id)
        existing = session.exec(statement).first()
        assert existing is not None
        assert existing.is_deleted is False


class TestConversationServiceIsolation:
    """Tests for ConversationService isolation by user_id (T038)."""

    def test_user_can_only_see_own_conversations(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should only see their own conversations."""
        from src.models.conversation import Conversation
        from src.services.conversation_service import ConversationService

        # Create conversations for both users
        user1_conv = Conversation(user_id=user1_id)
        user2_conv = Conversation(user_id=user2_id)
        session.add_all([user1_conv, user2_conv])
        session.commit()

        # Query using service with user1 ID
        service = ConversationService(session)
        user1_convs = service.get_conversations_by_user(user1_id)

        assert len(user1_convs) == 1
        assert user1_convs[0].user_id == user1_id

    def test_user_cannot_access_other_users_conversation(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should not be able to access another users conversation."""
        from src.models.conversation import Conversation
        from src.services.conversation_service import ConversationService

        # Create conversation for user2
        user2_conv = Conversation(user_id=user2_id)
        session.add(user2_conv)
        session.commit()
        session.refresh(user2_conv)

        # User1 tries to access user2 conversation
        service = ConversationService(session)
        result = service.get_conversation_by_id(user2_conv.id, user1_id)

        # Should return None
        assert result is None

    def test_user_can_access_own_conversation(
        self, session: Session, user1_id: str
    ):
        """User should be able to access their own conversation."""
        from src.models.conversation import Conversation
        from src.services.conversation_service import ConversationService

        # Create conversation for user1
        conv = Conversation(user_id=user1_id)
        session.add(conv)
        session.commit()
        session.refresh(conv)

        # User1 accesses own conversation
        service = ConversationService(session)
        result = service.get_conversation_by_id(conv.id, user1_id)

        assert result is not None
        assert result.user_id == user1_id

    def test_user_cannot_add_message_to_other_users_conversation(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should not be able to add messages to another users conversation."""
        from src.models.conversation import Conversation
        from src.services.conversation_service import ConversationService

        # Create conversation for user2
        user2_conv = Conversation(user_id=user2_id)
        session.add(user2_conv)
        session.commit()
        session.refresh(user2_conv)

        # User1 tries to add message to user2 conversation
        service = ConversationService(session)
        result = service.add_message(
            conversation_id=user2_conv.id,
            user_id=user1_id,
            role=MessageRole.USER,
            content="Trying to inject message",
        )

        # Should return None
        assert result is None


class TestCrossUserAccessSecurity:
    """Tests for security by obscurity - cross-user access (T039)."""

    def test_guessing_task_id_returns_not_found(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """Guessing a task ID should return not found not forbidden."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create task for user2
        user2_task = Task(user_id=user2_id, title="Secret task")
        session.add(user2_task)
        session.commit()
        session.refresh(user2_task)

        # User1 tries various IDs
        service = TaskService(session)

        # Existing ID belonging to another user
        result = service.get_task_by_id(user2_task.id, user1_id)
        assert result is None

        # Non-existent ID
        result = service.get_task_by_id(99999, user1_id)
        assert result is None

    def test_guessing_conversation_id_returns_not_found(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """Guessing a conversation ID should return not found."""
        from src.models.conversation import Conversation
        from src.services.conversation_service import ConversationService

        # Create conversation for user2
        user2_conv = Conversation(user_id=user2_id)
        session.add(user2_conv)
        session.commit()
        session.refresh(user2_conv)

        # User1 tries to access
        service = ConversationService(session)
        result = service.get_conversation_by_id(user2_conv.id, user1_id)

        assert result is None

    def test_no_user_count_leakage(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """Task count should not reveal existence of other users tasks."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create different number of tasks for each user
        for i in range(5):
            session.add(Task(user_id=user1_id, title=f"Alice task {i}"))
        for i in range(10):
            session.add(Task(user_id=user2_id, title=f"Bob task {i}"))
        session.commit()

        service = TaskService(session)

        # Each user should only see their own count
        user1_tasks = service.get_tasks_by_user(user1_id)
        user2_tasks = service.get_tasks_by_user(user2_id)

        assert len(user1_tasks) == 5
        assert len(user2_tasks) == 10

    def test_filtered_results_only_show_own_data(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """Filtered queries should only return users own data."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create high priority tasks for both users
        session.add(Task(user_id=user1_id, title="Alice urgent", priority=Priority.HIGH))
        session.add(Task(user_id=user2_id, title="Bob urgent", priority=Priority.HIGH))
        session.commit()

        service = TaskService(session)
        high_priority = service.get_tasks_by_user(user1_id, priority=Priority.HIGH)

        assert len(high_priority) == 1
        assert high_priority[0].user_id == user1_id
        assert high_priority[0].title == "Alice urgent"


class TestMessageServiceIsolation:
    """Tests for MessageService isolation via conversation ownership."""

    def test_messages_only_accessible_through_owned_conversation(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """Messages should only be accessible through users own conversation."""
        from src.models.conversation import Conversation
        from src.models.message import Message
        from src.services.message_service import MessageService

        # Create conversations for each user
        user1_conv = Conversation(user_id=user1_id)
        user2_conv = Conversation(user_id=user2_id)
        session.add_all([user1_conv, user2_conv])
        session.commit()
        session.refresh(user1_conv)
        session.refresh(user2_conv)

        # Add messages to each
        user1_msg = Message(
            conversation_id=user1_conv.id,
            role=MessageRole.USER,
            content="Alice message",
        )
        user2_msg = Message(
            conversation_id=user2_conv.id,
            role=MessageRole.USER,
            content="Bob message",
        )
        session.add_all([user1_msg, user2_msg])
        session.commit()

        # User1 should only see messages from their conversation
        service = MessageService(session)
        user1_messages = service.get_messages_for_conversation(user1_conv.id, user1_id)

        assert len(user1_messages) == 1
        assert user1_messages[0].content == "Alice message"

    def test_user_cannot_read_messages_from_other_conversation(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """User should not be able to read messages from another users conversation."""
        from src.models.conversation import Conversation
        from src.models.message import Message
        from src.services.message_service import MessageService

        # Create conversation for user2 with messages
        user2_conv = Conversation(user_id=user2_id)
        session.add(user2_conv)
        session.commit()
        session.refresh(user2_conv)

        user2_msg = Message(
            conversation_id=user2_conv.id,
            role=MessageRole.USER,
            content="Bob private message",
        )
        session.add(user2_msg)
        session.commit()

        # User1 tries to read user2 messages
        service = MessageService(session)
        result = service.get_messages_for_conversation(user2_conv.id, user1_id)

        # Should return None (conversation not found for user)
        assert result is None


class TestContextReconstructionIsolation:
    """Tests for context reconstruction respecting user isolation."""

    def test_context_only_includes_own_conversation_data(
        self, session: Session, user1_id: str, user2_id: str
    ):
        """Context reconstruction should only include users own data."""
        from src.models.conversation import Conversation
        from src.models.message import Message
        from src.services.context_service import ContextService

        # Create conversations for each user
        user1_conv = Conversation(user_id=user1_id)
        user2_conv = Conversation(user_id=user2_id)
        session.add_all([user1_conv, user2_conv])
        session.commit()
        session.refresh(user1_conv)
        session.refresh(user2_conv)

        # Add messages
        session.add(Message(
            conversation_id=user1_conv.id,
            role=MessageRole.USER,
            content="Alice message",
        ))
        session.add(Message(
            conversation_id=user2_conv.id,
            role=MessageRole.USER,
            content="Bob message",
        ))
        session.commit()

        # Reconstruct context for user1 conversation
        service = ContextService(session)
        context = service.reconstruct_context(user1_conv.id)

        assert len(context.messages) == 1
        assert context.messages[0].content == "Alice message"


class TestSoftDeleteIsolation:
    """Tests for soft delete with user isolation."""

    def test_soft_deleted_tasks_not_visible(
        self, session: Session, user1_id: str
    ):
        """Soft-deleted tasks should not be visible by default."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        # Create tasks
        task1 = Task(user_id=user1_id, title="Active task")
        task2 = Task(user_id=user1_id, title="Deleted task", is_deleted=True)
        session.add_all([task1, task2])
        session.commit()

        service = TaskService(session)
        tasks = service.get_tasks_by_user(user1_id)

        assert len(tasks) == 1
        assert tasks[0].title == "Active task"

    def test_soft_deleted_task_not_accessible_by_id(
        self, session: Session, user1_id: str
    ):
        """Soft-deleted task should not be accessible by ID."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        task = Task(user_id=user1_id, title="Deleted task", is_deleted=True)
        session.add(task)
        session.commit()
        session.refresh(task)

        service = TaskService(session)
        result = service.get_task_by_id(task.id, user1_id)

        assert result is None

    def test_can_include_deleted_tasks_if_requested(
        self, session: Session, user1_id: str
    ):
        """Should be able to include deleted tasks if explicitly requested."""
        from src.models.task import Task
        from src.services.task_service import TaskService

        task1 = Task(user_id=user1_id, title="Active task")
        task2 = Task(user_id=user1_id, title="Deleted task", is_deleted=True)
        session.add_all([task1, task2])
        session.commit()

        service = TaskService(session)
        tasks = service.get_tasks_by_user(user1_id, include_deleted=True)

        assert len(tasks) == 2
