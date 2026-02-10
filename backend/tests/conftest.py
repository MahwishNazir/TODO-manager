"""
Pytest configuration and fixtures for Phase II and Phase III tests.

This module provides test fixtures for:
- In-memory SQLite database for fast testing
- FastAPI TestClient for API endpoint testing
- Database session management
- JWT authentication for protected endpoints
- Phase III: Extended Task model fixtures (priority, status, due_date)
- Phase III: Conversation and Message model fixtures
- Phase III: Context reconstruction fixtures
"""

import pytest
import pytest_asyncio
from datetime import datetime, date, timedelta, timezone
from typing import Optional
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
import jwt

from src.main import app
from src.api.dependencies import get_db
from src.auth.jwt_handler import get_current_user, CurrentUser
from src.config import settings
from src.models.enums import Priority, TaskStatus, MessageRole


# Create in-memory SQLite database for testing
# StaticPool ensures the same database is used for all connections
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="function")
def test_session():
    """
    Provide a clean database session for each test.

    This fixture creates all tables before each test and drops them
    after the test completes, ensuring test isolation.

    Yields:
        Session: SQLModel database session for testing
    """
    # Create all tables
    SQLModel.metadata.create_all(test_engine)

    # Create session
    with Session(test_engine) as session:
        yield session

    # Drop all tables after test
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def client(test_session: Session):
    """
    Provide FastAPI TestClient with test database.

    This fixture overrides the get_db dependency to use the test
    database instead of the production Neon database.

    Args:
        test_session: Test database session from test_session fixture

    Yields:
        TestClient: FastAPI test client for API testing
    """

    def override_get_db():
        """Override get_db dependency to use test database."""
        try:
            yield test_session
        except Exception:
            test_session.rollback()
            raise

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Provide test client
    with TestClient(app) as test_client:
        yield test_client

    # Clear dependency overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_user_id():
    """
    Provide a sample user ID for testing.

    Returns:
        str: Test user ID
    """
    return "test_user_123"


@pytest.fixture(scope="function")
def another_user_id():
    """
    Provide a different user ID for testing user isolation.

    Returns:
        str: Another test user ID
    """
    return "test_user_456"


def create_jwt_token(user_id: str, email: str = "test@example.com") -> str:
    """
    Create a valid JWT token for testing.

    Args:
        user_id: User ID to encode in the token
        email: Email address to encode in the token

    Returns:
        str: Encoded JWT token
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=1),
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
    }

    token = jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token


@pytest.fixture(scope="function")
def sample_user_token(sample_user_id: str) -> str:
    """
    Provide a valid JWT token for the sample user.

    Args:
        sample_user_id: User ID from sample_user_id fixture

    Returns:
        str: JWT token for sample user
    """
    return create_jwt_token(sample_user_id, "test@example.com")


@pytest.fixture(scope="function")
def another_user_token(another_user_id: str) -> str:
    """
    Provide a valid JWT token for another user.

    Args:
        another_user_id: User ID from another_user_id fixture

    Returns:
        str: JWT token for another user
    """
    return create_jwt_token(another_user_id, "another@example.com")


@pytest.fixture(scope="function")
def auth_headers(sample_user_token: str) -> dict:
    """
    Provide authentication headers with JWT token.

    Args:
        sample_user_token: JWT token from sample_user_token fixture

    Returns:
        dict: Headers with Authorization bearer token
    """
    return {"Authorization": f"Bearer {sample_user_token}"}


@pytest.fixture(scope="function")
def another_auth_headers(another_user_token: str) -> dict:
    """
    Provide authentication headers for another user.

    Args:
        another_user_token: JWT token from another_user_token fixture

    Returns:
        dict: Headers with Authorization bearer token
    """
    return {"Authorization": f"Bearer {another_user_token}"}


# =============================================================================
# Phase III: Extended Task Model Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def sample_task_data(sample_user_id: str) -> dict:
    """
    Provide sample task data with Phase III extended fields.

    Args:
        sample_user_id: User ID from sample_user_id fixture

    Returns:
        dict: Task data with priority, status, due_date
    """
    return {
        "user_id": sample_user_id,
        "title": "Test task with extended fields",
        "is_completed": False,
        "priority": Priority.MEDIUM,
        "status": TaskStatus.INCOMPLETE,
        "due_date": date.today() + timedelta(days=7),
        "is_deleted": False,
    }


@pytest.fixture(scope="function")
def sample_high_priority_task_data(sample_user_id: str) -> dict:
    """
    Provide sample high priority task data.

    Args:
        sample_user_id: User ID from sample_user_id fixture

    Returns:
        dict: High priority task data
    """
    return {
        "user_id": sample_user_id,
        "title": "Urgent task",
        "is_completed": False,
        "priority": Priority.HIGH,
        "status": TaskStatus.INCOMPLETE,
        "due_date": date.today(),
        "is_deleted": False,
    }


@pytest.fixture(scope="function")
def sample_completed_task_data(sample_user_id: str) -> dict:
    """
    Provide sample completed task data.

    Args:
        sample_user_id: User ID from sample_user_id fixture

    Returns:
        dict: Completed task data
    """
    return {
        "user_id": sample_user_id,
        "title": "Completed task",
        "is_completed": True,
        "priority": Priority.LOW,
        "status": TaskStatus.COMPLETE,
        "due_date": date.today() - timedelta(days=1),
        "is_deleted": False,
    }


@pytest.fixture(scope="function")
def sample_deleted_task_data(sample_user_id: str) -> dict:
    """
    Provide sample soft-deleted task data.

    Args:
        sample_user_id: User ID from sample_user_id fixture

    Returns:
        dict: Soft-deleted task data
    """
    return {
        "user_id": sample_user_id,
        "title": "Deleted task",
        "is_completed": False,
        "priority": Priority.MEDIUM,
        "status": TaskStatus.INCOMPLETE,
        "due_date": None,
        "is_deleted": True,
    }


# =============================================================================
# Phase III: Conversation Model Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def sample_conversation_id() -> str:
    """
    Provide a sample conversation UUID.

    Returns:
        str: UUID string for conversation
    """
    return str(uuid4())


@pytest.fixture(scope="function")
def another_conversation_id() -> str:
    """
    Provide another conversation UUID for isolation tests.

    Returns:
        str: UUID string for another conversation
    """
    return str(uuid4())


@pytest.fixture(scope="function")
def sample_conversation_data(sample_user_id: str) -> dict:
    """
    Provide sample conversation data.

    Args:
        sample_user_id: User ID from sample_user_id fixture

    Returns:
        dict: Conversation data with all fields
    """
    now = datetime.now(timezone.utc)
    return {
        "user_id": sample_user_id,
        "started_at": now,
        "last_message_at": now,
        "is_active": True,
    }


@pytest.fixture(scope="function")
def sample_inactive_conversation_data(sample_user_id: str) -> dict:
    """
    Provide sample inactive conversation data.

    Args:
        sample_user_id: User ID from sample_user_id fixture

    Returns:
        dict: Inactive conversation data
    """
    now = datetime.now(timezone.utc)
    return {
        "user_id": sample_user_id,
        "started_at": now - timedelta(hours=2),
        "last_message_at": now - timedelta(hours=1),
        "is_active": False,
    }


# =============================================================================
# Phase III: Message Model Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def sample_user_message_data(sample_conversation_id: str) -> dict:
    """
    Provide sample user message data.

    Args:
        sample_conversation_id: Conversation ID from fixture

    Returns:
        dict: User message data
    """
    return {
        "conversation_id": sample_conversation_id,
        "role": MessageRole.USER,
        "content": "Show me my tasks for today",
        "created_at": datetime.now(timezone.utc),
        "last_mentioned_task_id": None,
        "message_metadata": {},
    }


@pytest.fixture(scope="function")
def sample_assistant_message_data(sample_conversation_id: str) -> dict:
    """
    Provide sample assistant message data.

    Args:
        sample_conversation_id: Conversation ID from fixture

    Returns:
        dict: Assistant message data
    """
    return {
        "conversation_id": sample_conversation_id,
        "role": MessageRole.ASSISTANT,
        "content": "Here are your tasks for today: 1. Buy groceries 2. Call mom",
        "created_at": datetime.now(timezone.utc),
        "last_mentioned_task_id": None,
        "message_metadata": {"tasks_mentioned": [1, 2]},
    }


@pytest.fixture(scope="function")
def sample_message_with_task_reference(sample_conversation_id: str) -> dict:
    """
    Provide sample message data with task reference.

    Args:
        sample_conversation_id: Conversation ID from fixture

    Returns:
        dict: Message data with last_mentioned_task_id
    """
    return {
        "conversation_id": sample_conversation_id,
        "role": MessageRole.ASSISTANT,
        "content": "I've marked 'Buy groceries' as complete.",
        "created_at": datetime.now(timezone.utc),
        "last_mentioned_task_id": 1,  # Reference to task ID
        "message_metadata": {"action": "complete_task", "task_id": 1},
    }


@pytest.fixture(scope="function")
def sample_system_message_data(sample_conversation_id: str) -> dict:
    """
    Provide sample system message data.

    Args:
        sample_conversation_id: Conversation ID from fixture

    Returns:
        dict: System message data
    """
    return {
        "conversation_id": sample_conversation_id,
        "role": MessageRole.SYSTEM,
        "content": "You are a helpful task management assistant.",
        "created_at": datetime.now(timezone.utc),
        "last_mentioned_task_id": None,
        "message_metadata": {"system_prompt": True},
    }


# =============================================================================
# Phase III: Context Reconstruction Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def sample_conversation_history() -> list[dict]:
    """
    Provide a sample conversation history for context reconstruction tests.

    Returns:
        list[dict]: List of message dictionaries in chronological order
    """
    now = datetime.now(timezone.utc)
    conv_id = str(uuid4())

    return [
        {
            "conversation_id": conv_id,
            "role": MessageRole.USER,
            "content": "What are my tasks?",
            "created_at": now - timedelta(minutes=10),
            "last_mentioned_task_id": None,
            "message_metadata": {},
        },
        {
            "conversation_id": conv_id,
            "role": MessageRole.ASSISTANT,
            "content": "You have 3 tasks: 1. Buy groceries 2. Call mom 3. Finish report",
            "created_at": now - timedelta(minutes=9),
            "last_mentioned_task_id": 3,
            "message_metadata": {"tasks_mentioned": [1, 2, 3]},
        },
        {
            "conversation_id": conv_id,
            "role": MessageRole.USER,
            "content": "Mark the first one as done",
            "created_at": now - timedelta(minutes=5),
            "last_mentioned_task_id": None,
            "message_metadata": {},
        },
        {
            "conversation_id": conv_id,
            "role": MessageRole.ASSISTANT,
            "content": "Done! I've marked 'Buy groceries' as complete.",
            "created_at": now - timedelta(minutes=4),
            "last_mentioned_task_id": 1,
            "message_metadata": {"action": "complete_task", "task_id": 1},
        },
    ]


@pytest.fixture(scope="function")
def max_context_messages() -> int:
    """
    Provide the maximum number of messages to include in context.

    Returns:
        int: Maximum context window size (50 messages per spec)
    """
    return 50


# =============================================================================
# Phase III: User Isolation Test Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def multi_user_task_data(sample_user_id: str, another_user_id: str) -> list[dict]:
    """
    Provide task data for multiple users to test isolation.

    Args:
        sample_user_id: First user ID
        another_user_id: Second user ID

    Returns:
        list[dict]: Tasks for both users
    """
    return [
        {
            "user_id": sample_user_id,
            "title": "User 1 Task 1",
            "priority": Priority.HIGH,
            "status": TaskStatus.INCOMPLETE,
        },
        {
            "user_id": sample_user_id,
            "title": "User 1 Task 2",
            "priority": Priority.MEDIUM,
            "status": TaskStatus.COMPLETE,
        },
        {
            "user_id": another_user_id,
            "title": "User 2 Task 1",
            "priority": Priority.LOW,
            "status": TaskStatus.INCOMPLETE,
        },
        {
            "user_id": another_user_id,
            "title": "User 2 Task 2",
            "priority": Priority.HIGH,
            "status": TaskStatus.INCOMPLETE,
        },
    ]


@pytest.fixture(scope="function")
def multi_user_conversation_data(
    sample_user_id: str, another_user_id: str
) -> list[dict]:
    """
    Provide conversation data for multiple users to test isolation.

    Args:
        sample_user_id: First user ID
        another_user_id: Second user ID

    Returns:
        list[dict]: Conversations for both users
    """
    now = datetime.now(timezone.utc)
    return [
        {
            "user_id": sample_user_id,
            "started_at": now,
            "last_message_at": now,
            "is_active": True,
        },
        {
            "user_id": another_user_id,
            "started_at": now,
            "last_message_at": now,
            "is_active": True,
        },
    ]

