"""
FastAPI dependencies for AI Agent API (T096).

Provides JWT authentication and other common dependencies.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from chatbot.agent.config import get_settings


# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """Current authenticated user from JWT token."""

    user_id: str
    email: str


async def verify_jwt(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> dict:
    """
    Verify JWT token and return payload.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Decoded JWT payload

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
                "require_exp": True,
                "require_iat": True,
            },
            leeway=10,  # ±10 seconds clock skew tolerance
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    payload: Annotated[dict, Depends(verify_jwt)]
) -> CurrentUser:
    """
    Extract current user from verified JWT payload.

    Args:
        payload: Verified JWT payload

    Returns:
        CurrentUser with user_id and email

    Raises:
        HTTPException: 401 if required claims are missing
    """
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing email in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(user_id=user_id, email=email)


def validate_user_access(session_user_id: str, current_user: CurrentUser) -> None:
    """
    Validate that current user can access the session.

    Args:
        session_user_id: User ID from session
        current_user: Current authenticated user

    Raises:
        HTTPException: 403 if user doesn't own the session
    """
    if session_user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )


def validate_user_id_match(path_user_id: str, current_user: CurrentUser) -> None:
    """
    Validate that the path user_id matches the JWT subject (T008).

    This is used for stateless endpoints where user_id is in the path
    and must match the authenticated user.

    Args:
        path_user_id: User ID from URL path parameter
        current_user: Current authenticated user from JWT

    Raises:
        HTTPException: 403 FORBIDDEN if user IDs don't match
    """
    if path_user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "User ID in path does not match authenticated user",
            },
        )
