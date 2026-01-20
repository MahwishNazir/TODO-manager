"""
Pytest configuration and fixtures for Phase II Step 2 tests.

This module provides test fixtures for:
- In-memory SQLite database for fast testing
- FastAPI TestClient for API endpoint testing
- Database session management
- JWT authentication for protected endpoints
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
import jwt

from src.main import app
from src.api.dependencies import get_db
from src.auth.jwt_handler import get_current_user, CurrentUser
from src.config import settings


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

