"""
Unit tests for JWT token parsing and verification (Phase II Step 2).

Tests verify JWT token validation, claim extraction, and error handling.
"""

import jwt
import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from src.auth.jwt_handler import verify_jwt, get_current_user, CurrentUser
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


class MockCredentials:
    """Mock HTTPAuthCredentials for testing."""

    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_verify_jwt_valid_token():
    """Test JWT verification with valid token."""
    token = create_test_token()
    credentials = MockCredentials(token)

    payload = await verify_jwt(credentials)

    assert payload["sub"] == "test-user-123"
    assert payload["email"] == "test@example.com"
    assert payload["iss"] == settings.JWT_ISSUER
    assert payload["aud"] == settings.JWT_AUDIENCE


@pytest.mark.asyncio
async def test_verify_jwt_expired_token():
    """Test JWT verification with expired token."""
    token = create_test_token(exp_minutes=-10)  # Expired 10 minutes ago
    credentials = MockCredentials(token)

    with pytest.raises(HTTPException) as exc_info:
        await verify_jwt(credentials)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_jwt_invalid_signature():
    """Test JWT verification with invalid signature."""
    token = create_test_token()
    # Tamper with token by changing last character
    tampered_token = token[:-1] + "X"
    credentials = MockCredentials(tampered_token)

    with pytest.raises(HTTPException) as exc_info:
        await verify_jwt(credentials)

    assert exc_info.value.status_code == 401
    assert "signature" in exc_info.value.detail.lower() or "invalid" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_jwt_wrong_audience():
    """Test JWT verification with wrong audience claim."""
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
    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)
    credentials = MockCredentials(token)

    with pytest.raises(HTTPException) as exc_info:
        await verify_jwt(credentials)

    assert exc_info.value.status_code == 401
    assert "audience" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_jwt_wrong_issuer():
    """Test JWT verification with wrong issuer claim."""
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
    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)
    credentials = MockCredentials(token)

    with pytest.raises(HTTPException) as exc_info:
        await verify_jwt(credentials)

    assert exc_info.value.status_code == 401
    assert "issuer" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_jwt_missing_required_claim():
    """Test JWT verification with missing required claim."""
    # Create token without 'sub' claim
    now = datetime.now(timezone.utc)
    payload = {
        "email": "test@example.com",
        "iat": now,
        "exp": now + timedelta(minutes=60),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        # Missing 'sub' claim
    }
    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)
    credentials = MockCredentials(token)

    # Token will be valid but get_current_user should fail
    payload = await verify_jwt(credentials)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(payload)

    assert exc_info.value.status_code == 401
    assert "user id" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_valid_payload():
    """Test CurrentUser extraction from valid JWT payload."""
    token = create_test_token()
    credentials = MockCredentials(token)
    payload = await verify_jwt(credentials)

    user = await get_current_user(payload)

    assert isinstance(user, CurrentUser)
    assert user.user_id == "test-user-123"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_missing_email():
    """Test CurrentUser extraction with missing email claim."""
    # Create payload without email
    payload = {
        "sub": "test-user-123",
        # Missing email
    }

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(payload)

    assert exc_info.value.status_code == 401
    assert "email" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_jwt_clock_skew_tolerance():
    """Test JWT verification with clock skew (should succeed with ±10 seconds)."""
    # Create token issued 5 seconds in the future (simulating clock skew)
    now = datetime.now(timezone.utc)
    future_time = now + timedelta(seconds=5)
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "iat": future_time,  # 5 seconds in future
        "exp": future_time + timedelta(minutes=60),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)
    credentials = MockCredentials(token)

    # Should succeed due to 10-second leeway
    result = await verify_jwt(credentials)

    assert result["sub"] == "test-user-123"
