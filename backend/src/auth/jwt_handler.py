"""
JWT verification and user extraction for Phase II Step 2.

This module provides FastAPI dependencies for JWT token verification
and current user extraction from validated tokens.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError

from src.config import settings


# HTTP Bearer security scheme - auto_error=False to manually handle 401 responses
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """
    Current authenticated user extracted from JWT token.

    Attributes:
        user_id: User identifier (UUID) from JWT 'sub' claim
        email: User email address from JWT 'email' claim
    """

    user_id: str
    email: str


async def verify_jwt(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> dict:
    """
    Verify JWT token signature and claims.

    Args:
        credentials: HTTP Bearer credentials containing JWT token (or None if missing)

    Returns:
        dict: Decoded JWT payload with verified claims

    Raises:
        HTTPException: 401 if token is missing, invalid, expired, or malformed
    """
    # Check if Authorization header is missing
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
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
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    payload: Annotated[dict, Depends(verify_jwt)]
) -> CurrentUser:
    """
    Extract current user information from verified JWT payload.

    Args:
        payload: Verified JWT payload from verify_jwt dependency

    Returns:
        CurrentUser: User information extracted from JWT claims

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
