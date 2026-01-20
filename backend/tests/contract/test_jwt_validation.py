"""
Contract tests for JWT middleware validation (T025).

These tests verify JWT token validation middleware behavior:
- Missing token returns 401
- Invalid token returns 401
- Expired token returns 401
- Tampered token returns 401

RED PHASE: These tests will FAIL until endpoints require authentication.
"""

import jwt
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from src.main import app
from src.config import settings


def create_test_token(
    user_id: str = "test-user-123",
    email: str = "test@example.com",
    exp_minutes: int = 60,
    **extra_claims
) -> str:
    """
    Create a test JWT token with specified claims.

    Args:
        user_id: User ID for 'sub' claim
        email: Email for 'email' claim
        exp_minutes: Expiration time in minutes from now
        **extra_claims: Additional claims to include

    Returns:
        str: Encoded JWT token
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(minutes=exp_minutes),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        **extra_claims,
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


class TestJWTMiddlewareMissingToken:
    """Test JWT validation when token is missing."""

    def test_list_tasks_without_token_returns_401(self, client):
        """Test listing tasks without Authorization header returns 401."""
        response = client.get("/api/test-user-123/tasks")

        # RED PHASE: This should return 401 but currently returns 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_create_task_without_token_returns_401(self, client):
        """Test creating task without Authorization header returns 401."""
        response = client.post(
            "/api/test-user-123/tasks",
            json={"title": "Test task"}
        )

        # RED PHASE: This should return 401 but currently returns 201
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_get_task_without_token_returns_401(self, client):
        """Test getting task without Authorization header returns 401."""
        response = client.get("/api/test-user-123/tasks/1")

        # RED PHASE: This should return 401 but currently returns 404 or 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_update_task_without_token_returns_401(self, client):
        """Test updating task without Authorization header returns 401."""
        response = client.put(
            "/api/test-user-123/tasks/1",
            json={"title": "Updated task"}
        )

        # RED PHASE: This should return 401 but currently returns 404 or 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_delete_task_without_token_returns_401(self, client):
        """Test deleting task without Authorization header returns 401."""
        response = client.delete("/api/test-user-123/tasks/1")

        # RED PHASE: This should return 401 but currently returns 404 or 204
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_toggle_complete_without_token_returns_401(self, client):
        """Test toggling completion without Authorization header returns 401."""
        response = client.patch("/api/test-user-123/tasks/1/complete")

        # RED PHASE: This should return 401 but currently returns 404 or 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()


class TestJWTMiddlewareInvalidToken:
    """Test JWT validation with invalid tokens."""

    def test_list_tasks_with_malformed_token_returns_401(self, client):
        """Test listing tasks with malformed token returns 401."""
        response = client.get(
            "/api/test-user-123/tasks",
            headers={"Authorization": "Bearer not-a-valid-jwt-token"}
        )

        # RED PHASE: This should return 401 but currently returns 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "invalid" in response.json()["detail"].lower() or "token" in response.json()["detail"].lower()

    def test_create_task_with_malformed_token_returns_401(self, client):
        """Test creating task with malformed token returns 401."""
        response = client.post(
            "/api/test-user-123/tasks",
            json={"title": "Test task"},
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        # RED PHASE: This should return 401 but currently returns 201
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_request_with_missing_bearer_prefix_returns_401(self, client):
        """Test request with Authorization header missing 'Bearer ' prefix returns 401."""
        token = create_test_token()
        response = client.get(
            "/api/test-user-123/tasks",
            headers={"Authorization": token}  # Missing "Bearer " prefix
        )

        # RED PHASE: This should return 401 but currently returns 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()


class TestJWTMiddlewareExpiredToken:
    """Test JWT validation with expired tokens."""

    def test_list_tasks_with_expired_token_returns_401(self, client):
        """Test listing tasks with expired token returns 401."""
        # Create token that expired 10 minutes ago
        expired_token = create_test_token(exp_minutes=-10)

        response = client.get(
            "/api/test-user-123/tasks",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # RED PHASE: This should return 401 but currently returns 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "expired" in response.json()["detail"].lower()

    def test_create_task_with_expired_token_returns_401(self, client):
        """Test creating task with expired token returns 401."""
        # Create token that expired 5 minutes ago
        expired_token = create_test_token(exp_minutes=-5)

        response = client.post(
            "/api/test-user-123/tasks",
            json={"title": "Test task"},
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # RED PHASE: This should return 401 but currently returns 201
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "expired" in response.json()["detail"].lower()


class TestJWTMiddlewareTamperedToken:
    """Test JWT validation with tampered tokens."""

    def test_list_tasks_with_tampered_signature_returns_401(self, client):
        """Test listing tasks with tampered token signature returns 401."""
        # Create valid token then tamper with it
        valid_token = create_test_token()
        tampered_token = valid_token[:-5] + "XXXXX"  # Change last 5 chars

        response = client.get(
            "/api/test-user-123/tasks",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )

        # RED PHASE: This should return 401 but currently returns 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "signature" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()

    def test_create_task_with_wrong_secret_returns_401(self, client):
        """Test creating task with token signed with wrong secret returns 401."""
        # Create token with wrong secret
        wrong_secret = "wrong-secret-key"
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "iat": now,
            "exp": now + timedelta(minutes=60),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
        }
        wrong_token = jwt.encode(payload, wrong_secret, algorithm=settings.JWT_ALGORITHM)

        response = client.post(
            "/api/test-user-123/tasks",
            json={"title": "Test task"},
            headers={"Authorization": f"Bearer {wrong_token}"}
        )

        # RED PHASE: This should return 401 but currently returns 201
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "signature" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()

    def test_update_task_with_modified_payload_returns_401(self, client):
        """Test updating task with modified token payload returns 401."""
        # Create valid token
        valid_token = create_test_token(user_id="original-user")

        # Decode without verification (to modify payload)
        payload = jwt.decode(valid_token, options={"verify_signature": False})

        # Modify the user_id in payload
        payload["sub"] = "hacker-user"

        # Re-encode with wrong secret (signature won't match)
        tampered_token = jwt.encode(payload, "wrong-secret", algorithm=settings.JWT_ALGORITHM)

        response = client.put(
            "/api/test-user-123/tasks/1",
            json={"title": "Hacked task"},
            headers={"Authorization": f"Bearer {tampered_token}"}
        )

        # RED PHASE: This should return 401 but currently returns 404 or 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()


class TestJWTMiddlewareInvalidClaims:
    """Test JWT validation with invalid claims."""

    def test_token_with_wrong_audience_returns_401(self, client):
        """Test token with wrong audience claim returns 401."""
        # Create token with wrong audience
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "iat": now,
            "exp": now + timedelta(minutes=60),
            "iss": settings.JWT_ISSUER,
            "aud": "wrong-audience",  # Wrong audience
        }
        wrong_token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)

        response = client.get(
            "/api/test-user-123/tasks",
            headers={"Authorization": f"Bearer {wrong_token}"}
        )

        # RED PHASE: This should return 401 but currently returns 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "audience" in response.json()["detail"].lower()

    def test_token_with_wrong_issuer_returns_401(self, client):
        """Test token with wrong issuer claim returns 401."""
        # Create token with wrong issuer
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "iat": now,
            "exp": now + timedelta(minutes=60),
            "iss": "wrong-issuer",  # Wrong issuer
            "aud": settings.JWT_AUDIENCE,
        }
        wrong_token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)

        response = client.get(
            "/api/test-user-123/tasks",
            headers={"Authorization": f"Bearer {wrong_token}"}
        )

        # RED PHASE: This should return 401 but currently returns 200
        # because endpoints don't require auth yet
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "issuer" in response.json()["detail"].lower()
