"""
Unit tests for ConfirmationTokenService (Phase III Part 5).

TDD: These tests are written FIRST and should FAIL until implementation.
Tests T046-T047 for User Story 5.
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch


# =============================================================================
# User Story 5: Confirmation Flow (T046-T047)
# =============================================================================

class TestConfirmationTokenService:
    """Unit tests for User Story 5."""

    def test_generates_valid_jwt(self):
        """T046: ConfirmationTokenService generates valid JWT."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        # Use a test secret
        service = ConfirmationTokenService(secret_key="test-secret-key-123")

        result = service.generate_token(
            action="delete_task",
            user_id="user-123",
            description="Delete task 'Buy milk'",
            task_id="task-456",
        )

        # Verify structure
        assert "token" in result
        assert "action" in result
        assert "description" in result
        assert "expires_at" in result

        # Token should be a string
        assert isinstance(result["token"], str)

        # Should be decodable JWT
        payload = jwt.decode(
            result["token"],
            "test-secret-key-123",
            algorithms=["HS256"],
        )

        # Payload should contain expected claims
        assert payload["sub"] == "user-123"
        assert payload["action"] == "delete_task"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload  # Unique token ID

        # Action params should be in payload
        assert payload["params"]["task_id"] == "task-456"

    def test_validates_token_correctly(self):
        """T047: ConfirmationTokenService validates token correctly."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret-key-123")

        # Generate a token
        generated = service.generate_token(
            action="delete_task",
            user_id="user-123",
            description="Delete task",
            task_id="task-456",
        )

        # Validate the token
        result = service.validate_token(
            token=generated["token"],
            user_id="user-123",
        )

        assert result["valid"] is True
        assert result["action"] == "delete_task"
        assert result["params"]["task_id"] == "task-456"

    def test_rejects_expired_token(self):
        """Expired token should be rejected with CONFIRMATION_EXPIRED."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret-key-123")

        # Create an already-expired token manually
        expired_payload = {
            "jti": "test-jti",
            "sub": "user-123",
            "action": "delete_task",
            "params": {},
            "iat": int((datetime.now(timezone.utc) - timedelta(minutes=10)).timestamp()),
            "exp": int((datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp()),
        }
        expired_token = jwt.encode(expired_payload, "test-secret-key-123", algorithm="HS256")

        result = service.validate_token(
            token=expired_token,
            user_id="user-123",
        )

        assert result["valid"] is False
        assert result["error"] == "CONFIRMATION_EXPIRED"

    def test_rejects_wrong_user(self):
        """Token for different user should be rejected."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret-key-123")

        # Generate token for user-123
        generated = service.generate_token(
            action="delete_task",
            user_id="user-123",
            description="Delete task",
        )

        # Try to validate for different user
        result = service.validate_token(
            token=generated["token"],
            user_id="user-999",  # Different user
        )

        assert result["valid"] is False
        assert result["error"] == "INVALID_CONFIRMATION"

    def test_rejects_invalid_token(self):
        """Malformed token should be rejected."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret-key-123")

        result = service.validate_token(
            token="not-a-valid-jwt-token",
            user_id="user-123",
        )

        assert result["valid"] is False
        assert result["error"] == "INVALID_CONFIRMATION"

    def test_rejects_wrong_signature(self):
        """Token signed with wrong key should be rejected."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        # Generate with one key
        service1 = ConfirmationTokenService(secret_key="secret-key-1")
        generated = service1.generate_token(
            action="delete_task",
            user_id="user-123",
            description="Delete task",
        )

        # Validate with different key
        service2 = ConfirmationTokenService(secret_key="secret-key-2")
        result = service2.validate_token(
            token=generated["token"],
            user_id="user-123",
        )

        assert result["valid"] is False
        assert result["error"] == "INVALID_CONFIRMATION"


class TestConfirmationTokenExpiry:
    """Tests for token expiration handling."""

    def test_token_expiry_time(self):
        """Token should expire after 5 minutes."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret")

        # Verify expiry constant
        assert service.TOKEN_EXPIRY_MINUTES == 5

        # Generate token
        result = service.generate_token(
            action="delete_task",
            user_id="user-123",
            description="Test",
        )

        # Parse expires_at
        expires_at = datetime.fromisoformat(result["expires_at"])
        now = datetime.now(timezone.utc)

        # Should be approximately 5 minutes in the future
        delta = expires_at - now
        assert 4 * 60 < delta.total_seconds() < 6 * 60  # 4-6 minutes tolerance


class TestDestructiveActionDetection:
    """Tests for destructive action identification."""

    def test_delete_task_is_destructive(self):
        """delete_task should be considered destructive."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret")

        assert service.is_destructive_action("delete_task") is True

    def test_delete_all_tasks_is_destructive(self):
        """delete_all_tasks should be considered destructive."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret")

        assert service.is_destructive_action("delete_all_tasks") is True

    def test_clear_completed_is_destructive(self):
        """clear_completed should be considered destructive."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret")

        assert service.is_destructive_action("clear_completed") is True

    def test_add_task_is_not_destructive(self):
        """add_task should NOT be considered destructive."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret")

        assert service.is_destructive_action("add_task") is False

    def test_list_tasks_is_not_destructive(self):
        """list_tasks should NOT be considered destructive."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret")

        assert service.is_destructive_action("list_tasks") is False

    def test_update_task_is_not_destructive(self):
        """update_task should NOT be considered destructive."""
        from chatbot.agent.confirmation_token import ConfirmationTokenService

        service = ConfirmationTokenService(secret_key="test-secret")

        assert service.is_destructive_action("update_task") is False
