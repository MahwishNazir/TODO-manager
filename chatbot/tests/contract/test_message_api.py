"""
Contract tests for message API endpoints (T092).

Verifies message endpoints conform to the OpenAPI specification.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import patch, AsyncMock

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


class TestSendMessage:
    """Contract tests for POST /api/agent/sessions/{session_id}/messages."""

    def test_send_message_success(self, client, valid_token, session_id):
        """Should process message and return agent response."""
        token, _ = valid_token

        with patch("chatbot.api.routes.messages.process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "response": "I'll help you create that task.",
                "context": None,
                "confirmation_state": None,
            }

            response = client.post(
                f"/api/agent/sessions/{session_id}/messages",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "Create a task to buy groceries"}
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert "response" in data["data"]

    def test_send_message_requires_confirmation(self, client, valid_token, session_id):
        """Should indicate when confirmation is required."""
        token, _ = valid_token

        with patch("chatbot.api.routes.messages.process_message") as mock_process:
            # Simulate a response that requires confirmation
            from chatbot.agent.models import ConfirmationStatus
            mock_state = AsyncMock()
            mock_state.state = ConfirmationStatus.AWAITING_DELETE
            mock_state.is_awaiting_confirmation.return_value = True

            mock_process.return_value = {
                "success": True,
                "response": "Are you sure you want to delete this task?",
                "context": None,
                "confirmation_state": mock_state,
            }

            response = client.post(
                f"/api/agent/sessions/{session_id}/messages",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "Delete my grocery task"}
            )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["requires_confirmation"] is True

    def test_send_message_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.post(
            f"/api/agent/sessions/{session_id}/messages",
            json={"message": "Hello"}
        )

        assert response.status_code == 401

    def test_send_message_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.post(
            f"/api/agent/sessions/{fake_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Hello"}
        )

        assert response.status_code == 404

    def test_send_message_empty_message(self, client, valid_token, session_id):
        """Should return 422 for empty message."""
        token, _ = valid_token

        response = client.post(
            f"/api/agent/sessions/{session_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": ""}
        )

        assert response.status_code == 422

    def test_send_message_missing_message(self, client, valid_token, session_id):
        """Should return 422 for missing message field."""
        token, _ = valid_token

        response = client.post(
            f"/api/agent/sessions/{session_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )

        assert response.status_code == 422


class TestSendMessageStream:
    """Contract tests for POST /api/agent/sessions/{session_id}/messages/stream."""

    def test_stream_message_success(self, client, valid_token, session_id):
        """Should return SSE stream with agent response."""
        token, _ = valid_token

        with patch("chatbot.api.routes.messages.process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "response": "Here is your task list.",
                "context": None,
            }

            response = client.post(
                f"/api/agent/sessions/{session_id}/messages/stream",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "Show my tasks"}
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        # Verify SSE format
        content = response.text
        assert "data:" in content

    def test_stream_message_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.post(
            f"/api/agent/sessions/{session_id}/messages/stream",
            json={"message": "Hello"}
        )

        assert response.status_code == 401

    def test_stream_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.post(
            f"/api/agent/sessions/{fake_id}/messages/stream",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Hello"}
        )

        assert response.status_code == 404


class TestGetHistory:
    """Contract tests for GET /api/agent/sessions/{session_id}/history."""

    def test_get_history_success(self, client, valid_token, session_id):
        """Should return conversation history."""
        token, _ = valid_token

        response = client.get(
            f"/api/agent/sessions/{session_id}/history",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert "messages" in data["data"]
        assert isinstance(data["data"]["messages"], list)

    def test_get_history_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.get(
            f"/api/agent/sessions/{session_id}/history"
        )

        assert response.status_code == 401

    def test_get_history_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.get(
            f"/api/agent/sessions/{fake_id}/history",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_get_history_other_user(self, client, valid_token, session_id, settings):
        """Should return 403 when accessing another user's history."""
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
            f"/api/agent/sessions/{session_id}/history",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403
