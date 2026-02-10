"""
Contract tests for plan API endpoints (T094).

Verifies plan endpoints conform to the OpenAPI specification.
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


class TestGetCurrentPlan:
    """Contract tests for GET /api/agent/sessions/{session_id}/plan."""

    def test_get_plan_no_active_plan(self, client, valid_token, session_id):
        """Should return empty when no active plan."""
        token, _ = valid_token

        response = client.get(
            f"/api/agent/sessions/{session_id}/plan",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["plan"] is None

    def test_get_plan_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.get(
            f"/api/agent/sessions/{session_id}/plan"
        )

        assert response.status_code == 401

    def test_get_plan_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.get(
            f"/api/agent/sessions/{fake_id}/plan",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_get_plan_other_user(self, client, valid_token, session_id, settings):
        """Should return 403 when accessing another user's plan."""
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
            f"/api/agent/sessions/{session_id}/plan",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403


class TestApprovePlan:
    """Contract tests for POST /api/agent/sessions/{session_id}/plan/approve."""

    def test_approve_plan_no_pending(self, client, valid_token, session_id):
        """Should return 400 when no pending plan approval."""
        token, _ = valid_token

        response = client.post(
            f"/api/agent/sessions/{session_id}/plan/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"approve": True}
        )

        assert response.status_code == 400
        assert "pending" in response.json()["detail"].lower()

    def test_approve_plan_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.post(
            f"/api/agent/sessions/{session_id}/plan/approve",
            json={"approve": True}
        )

        assert response.status_code == 401

    def test_approve_plan_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.post(
            f"/api/agent/sessions/{fake_id}/plan/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"approve": True}
        )

        assert response.status_code == 404

    def test_approve_plan_missing_approve(self, client, valid_token, session_id):
        """Should return 422 for missing approve field."""
        token, _ = valid_token

        response = client.post(
            f"/api/agent/sessions/{session_id}/plan/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )

        assert response.status_code == 422

    def test_approve_plan_other_user(self, client, valid_token, session_id, settings):
        """Should return 403 when approving another user's plan."""
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
            f"/api/agent/sessions/{session_id}/plan/approve",
            headers={"Authorization": f"Bearer {token2}"},
            json={"approve": True}
        )

        assert response.status_code == 403


class TestCancelPlan:
    """Contract tests for DELETE /api/agent/sessions/{session_id}/plan."""

    def test_cancel_plan_no_active(self, client, valid_token, session_id):
        """Should succeed gracefully when no active plan."""
        token, _ = valid_token

        response = client.delete(
            f"/api/agent/sessions/{session_id}/plan",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "no active" in data["data"]["message"].lower()

    def test_cancel_plan_no_auth(self, client, session_id):
        """Should return 401 without authorization."""
        response = client.delete(
            f"/api/agent/sessions/{session_id}/plan"
        )

        assert response.status_code == 401

    def test_cancel_plan_session_not_found(self, client, valid_token):
        """Should return 404 for non-existent session."""
        token, _ = valid_token
        fake_id = str(uuid4())

        response = client.delete(
            f"/api/agent/sessions/{fake_id}/plan",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    def test_cancel_plan_other_user(self, client, valid_token, session_id, settings):
        """Should return 403 when cancelling another user's plan."""
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

        response = client.delete(
            f"/api/agent/sessions/{session_id}/plan",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403


class TestPlanResponseFormat:
    """Tests for plan response format per OpenAPI spec."""

    def test_get_plan_response_structure(self, client, valid_token, session_id):
        """Should return proper structure for get plan."""
        token, _ = valid_token

        response = client.get(
            f"/api/agent/sessions/{session_id}/plan",
            headers={"Authorization": f"Bearer {token}"}
        )

        data = response.json()

        # Verify base APIResponse structure
        assert "success" in data
        assert isinstance(data["success"], bool)
        assert "data" in data

    def test_cancel_plan_response_structure(self, client, valid_token, session_id):
        """Should return proper structure for cancel plan."""
        token, _ = valid_token

        response = client.delete(
            f"/api/agent/sessions/{session_id}/plan",
            headers={"Authorization": f"Bearer {token}"}
        )

        data = response.json()

        # Verify base APIResponse structure
        assert "success" in data
        assert isinstance(data["success"], bool)
        assert "data" in data
        assert "message" in data["data"]
