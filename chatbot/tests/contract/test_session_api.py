"""
Contract tests for session API endpoints (T091).

Verifies session endpoints conform to the OpenAPI specification.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from chatbot.api.main import app
from chatbot.agent.config import get_settings


@pytest.fixture
def settings():
    """Get test settings."""
    return get_settings()


@pytest.fixture
def valid_token(settings):
    """Create a valid JWT token for testing."""
    user_id = str(uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    token = jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)
    return token, user_id


@pytest.fixture
def expired_token(settings):
    """Create an expired JWT token for testing."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid4()),
        "email": "test@example.com",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),  # Expired
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture
def invalid_signature_token(settings):
    """Create a token with invalid signature."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid4()),
        "email": "test@example.com",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, "wrong-secret", algorithm=settings.jwt_algorithm)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestCreateSession:
    """Contract tests for POST /api/agent/sessions."""

    def test_create_session_success(self, client, valid_token):
        """Should create session and return session details."""
        token, user_id = valid_token
        response = client.post(
            "/api/agent/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["success"] is True
        assert "data" in data
        assert "session" in data["data"]

        session = data["data"]["session"]
        assert "session_id" in session
        assert session["user_id"] == user_id
        assert "created_at" in session
        assert "last_active" in session
        assert session["status"] == "ACTIVE"

    def test_create_session_no_auth(self, client):
        """Should return 401 without authorization header."""
        response = client.post("/api/agent/sessions")

        assert response.status_code == 401

    def test_create_session_expired_token(self, client, expired_token):
        """Should return 401 with expired token."""
        response = client.post(
            "/api/agent/sessions",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_create_session_invalid_signature(self, client, invalid_signature_token):
        """Should return 401 with invalid signature."""
        response = client.post(
            "/api/agent/sessions",
            headers={"Authorization": f"Bearer {invalid_signature_token}"}
        )

        assert response.status_code == 401


class TestGetSession:
    """Contract tests for GET /api/agent/sessions/{session_id}."""

    def test_get_session_success(self, client, valid_token):
        """Should return session details for valid session."""
        token, user_id = valid_token

        # Create session first
        create_response = client.post(
            "/api/agent/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        session_id = create_response.json()["data"]["session"]["session_id"]

        # Get session
        response = client.get(
            f"/api/agent/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["session"]["session_id"] == session_id
        assert data["data"]["session"]["user_id"] == user_id

    def test_get_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.get(
            f"/api/agent/sessions/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_get_session_other_user(self, client, valid_token, settings):
        """Should return 403 when accessing another user's session."""
        token1, user1_id = valid_token

        # Create session with first user
        create_response = client.post(
            "/api/agent/sessions",
            headers={"Authorization": f"Bearer {token1}"}
        )
        session_id = create_response.json()["data"]["session"]["session_id"]

        # Create token for different user
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(uuid4()),  # Different user
            "email": "other@example.com",
            "iat": now,
            "exp": now + timedelta(hours=1),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        }
        token2 = jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)

        # Try to access session with second user
        response = client.get(
            f"/api/agent/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403

    def test_get_session_invalid_uuid(self, client, valid_token):
        """Should return 422 for invalid UUID format."""
        token, _ = valid_token

        response = client.get(
            "/api/agent/sessions/not-a-uuid",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 422


class TestDeleteSession:
    """Contract tests for DELETE /api/agent/sessions/{session_id}."""

    def test_delete_session_success(self, client, valid_token):
        """Should delete session successfully."""
        token, _ = valid_token

        # Create session first
        create_response = client.post(
            "/api/agent/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        session_id = create_response.json()["data"]["session"]["session_id"]

        # Delete session
        response = client.delete(
            f"/api/agent/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify session is gone
        get_response = client.get(
            f"/api/agent/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.delete(
            f"/api/agent/sessions/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_delete_session_other_user(self, client, valid_token, settings):
        """Should return 403 when deleting another user's session."""
        token1, _ = valid_token

        # Create session with first user
        create_response = client.post(
            "/api/agent/sessions",
            headers={"Authorization": f"Bearer {token1}"}
        )
        session_id = create_response.json()["data"]["session"]["session_id"]

        # Create token for different user
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(uuid4()),
            "email": "other@example.com",
            "iat": now,
            "exp": now + timedelta(hours=1),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        }
        token2 = jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)

        # Try to delete session with second user
        response = client.delete(
            f"/api/agent/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403
