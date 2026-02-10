"""
Contract tests for confirmation API endpoints (T093).

Verifies confirmation endpoints conform to the OpenAPI specification.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from chatbot.api.main import app
from chatbot.agent.config import get_settings
from chatbot.agent.session import set_session_confirmation
from chatbot.agent.models import ConfirmationState, ConfirmationStatus


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
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def session_id(client, valid_token):
    """Create a session and return its ID."""
    token, _ = valid_token
    response = client.post(
        "/api/agent/sessions",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["data"]["session"]["session_id"]


class TestConfirmAction:
    """Contract tests for POST /api/agent/sessions/{session_id}/confirm."""

    @pytest.mark.asyncio
    async def test_confirm_action_no_pending(self, client, valid_token, session_id):
        """Should return 400 when no pending confirmation."""
        token, _ = valid_token

        response = client.post(
            f"/api/agent/sessions/{session_id}/confirm",
            headers={"Authorization": f"Bearer {token}"},
            json={"response": "yes"}
        )

        assert response.status_code == 400
        assert "pending" in response.json()["detail"].lower()

    def test_confirm_action_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.post(
            f"/api/agent/sessions/{session_id}/confirm",
            json={"response": "yes"}
        )

        assert response.status_code == 401

    def test_confirm_action_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.post(
            f"/api/agent/sessions/{fake_id}/confirm",
            headers={"Authorization": f"Bearer {token}"},
            json={"response": "yes"}
        )

        assert response.status_code == 404

    def test_confirm_action_missing_response(self, client, valid_token, session_id):
        """Should return 422 for missing response field."""
        token, _ = valid_token

        response = client.post(
            f"/api/agent/sessions/{session_id}/confirm",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )

        assert response.status_code == 422

    def test_confirm_action_other_user(self, client, valid_token, session_id, settings):
        """Should return 403 when confirming for another user's session."""
        token1, _ = valid_token

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

        response = client.post(
            f"/api/agent/sessions/{session_id}/confirm",
            headers={"Authorization": f"Bearer {token2}"},
            json={"response": "yes"}
        )

        assert response.status_code == 403


class TestGetConfirmationStatus:
    """Contract tests for GET /api/agent/sessions/{session_id}/confirm/status."""

    def test_get_status_idle(self, client, valid_token, session_id):
        """Should return idle state when no pending confirmation."""
        token, _ = valid_token

        response = client.get(
            f"/api/agent/sessions/{session_id}/confirm/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["has_pending"] is False
        assert data["data"]["state"] == "IDLE"

    def test_get_status_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.get(
            f"/api/agent/sessions/{session_id}/confirm/status"
        )

        assert response.status_code == 401

    def test_get_status_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.get(
            f"/api/agent/sessions/{fake_id}/confirm/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_get_status_other_user(self, client, valid_token, session_id, settings):
        """Should return 403 when checking another user's session status."""
        token1, _ = valid_token

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

        response = client.get(
            f"/api/agent/sessions/{session_id}/confirm/status",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403


class TestConfirmationResponseFormat:
    """Tests for confirmation response format per OpenAPI spec."""

    def test_response_structure_on_success(self, client, valid_token, session_id):
        """Should return proper structure on successful status check."""
        token, _ = valid_token

        response = client.get(
            f"/api/agent/sessions/{session_id}/confirm/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        data = response.json()

        # Verify base APIResponse structure
        assert "success" in data
        assert isinstance(data["success"], bool)
        assert "data" in data

    def test_error_response_structure(self, client, valid_token):
        """Should return proper error structure for 404."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.get(
            f"/api/agent/sessions/{fake_id}/confirm/status",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        data = response.json()

        # FastAPI default error format
        assert "detail" in data
