# Backend JWT Validation Pattern - FastAPI + python-jose

## Overview
Production-ready FastAPI JWT validation using shared secret approach with Better Auth. Implements comprehensive user isolation and security best practices.

## Full Implementation

### 1. JWT Validation Service (`src/auth/jwt.py`)

```python
"""
JWT token validation using python-jose with shared BETTER_AUTH_SECRET.

This module provides JWT verification for tokens issued by Better Auth (Next.js frontend).
Uses HS256 symmetric signing algorithm with shared secret key.

Security:
- Validates token signature using BETTER_AUTH_SECRET
- Verifies token expiration (exp claim)
- Extracts user_id from 'sub' claim
- Raises appropriate exceptions for invalid/expired tokens
"""

from dotenv import load_dotenv
from jose import jwt, JWTError
from typing import Dict, Any
import os

load_dotenv()

# JWT configuration - shared secret with Next.js Better Auth
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

ALGORITHM = "HS256"  # Symmetric signing algorithm


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token using shared secret from Better Auth (Next.js).

    This validates tokens issued by Better Auth using the shared BETTER_AUTH_SECRET.
    Uses HS256 algorithm for symmetric signature verification.

    Args:
        token (str): JWT token string from Authorization header

    Returns:
        Dict[str, Any]: Decoded JWT payload containing:
            - sub (str): User ID
            - exp (int): Expiration timestamp
            - iat (int): Issued at timestamp
            - iss (str): Issuer (optional)
            - aud (str): Audience (optional)
            - Other claims from Better Auth

    Raises:
        ValueError: If token is invalid, expired, or missing required claims

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = verify_jwt_token(token)
        >>> user_id = payload["sub"]
    """
    try:
        # Decode and verify JWT signature with shared secret
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                # Make issuer and audience validation optional
                "verify_iss": False,
                "verify_aud": False,
            },
        )

        # Validate required claims exist
        if "sub" not in payload:
            raise ValueError("Token missing 'sub' claim (user_id)")

        # Optional: Validate issuer if present (for additional security)
        if "iss" in payload and payload["iss"] != "nextjs-frontend":
            raise ValueError(f"Invalid token issuer: {payload['iss']}")

        # Optional: Validate audience if present (for additional security)
        if "aud" in payload and payload["aud"] != "fastapi-backend":
            raise ValueError(f"Invalid token audience: {payload['aud']}")

        return payload

    except JWTError as e:
        # Handle JWT-specific errors (expired, invalid signature, etc.)
        raise ValueError(f"Invalid JWT token: {str(e)}")
    except Exception as e:
        # Handle any other unexpected errors
        raise ValueError(f"Token validation failed: {str(e)}")


def extract_user_id(payload: Dict[str, Any]) -> str:
    """
    Extract user_id from decoded JWT payload.

    Args:
        payload (Dict[str, Any]): Decoded JWT payload from verify_jwt_token()

    Returns:
        str: User ID from 'sub' claim

    Raises:
        ValueError: If 'sub' claim is missing or invalid

    Example:
        >>> payload = verify_jwt_token(token)
        >>> user_id = extract_user_id(payload)
    """
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token: missing user_id in 'sub' claim")

    if not isinstance(user_id, str):
        raise ValueError("Invalid token: user_id must be a string")

    return user_id
```

### 2. FastAPI Authentication Dependencies (`src/auth/dependencies.py`)

```python
"""
FastAPI authentication dependencies for JWT validation.

Provides dependency injection functions for extracting and validating
JWT tokens from Authorization header in API endpoints.

Security:
- HTTPBearer security scheme for Authorization header
- Validates JWT token signature using shared secret
- Extracts user_id from token for authorization checks
- Raises HTTPException 401 for authentication failures
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from .jwt import verify_jwt_token, extract_user_id


# HTTPBearer security scheme for Authorization header with Bearer token
security = HTTPBearer(
    scheme_name="BearerAuth",
    description="JWT token from Better Auth (Next.js)",
    auto_error=True  # Automatically raise 401 if Authorization header is missing
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current user from JWT token.

    Extracts token from Authorization header, validates signature using
    shared BETTER_AUTH_SECRET, and returns decoded payload.

    Args:
        credentials: HTTPAuthorizationCredentials from HTTPBearer security scheme

    Returns:
        Dict[str, Any]: Decoded JWT payload containing user information

    Raises:
        HTTPException 401: If token is missing, invalid, or expired

    Example usage in endpoint:
        @app.get("/api/{user_id}/tasks")
        async def list_tasks(
            user_id: str,
            current_user: Dict[str, Any] = Depends(get_current_user)
        ):
            # Validate user_id matches token
            if user_id != current_user["sub"]:
                raise HTTPException(403, "Not authorized")
            # ... endpoint logic
    """
    try:
        # Extract token from credentials
        token = credentials.credentials

        # Verify JWT signature and decode payload
        payload = verify_jwt_token(token)

        return payload

    except ValueError as e:
        # Token validation failed (invalid, expired, missing claims)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Unexpected error during token validation
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    FastAPI dependency to get current user ID from JWT token.

    Extracts user_id from the 'sub' claim of the decoded JWT payload.
    This is the primary dependency to use in endpoints requiring authentication.

    CRITICAL: All endpoints MUST validate that this user_id matches the user_id
    in the URL path to ensure proper user data isolation.

    Args:
        current_user: Decoded JWT payload from get_current_user dependency

    Returns:
        str: User ID from 'sub' claim

    Raises:
        HTTPException 401: If 'sub' claim is missing or invalid

    Example usage in endpoint:
        @app.get("/api/{user_id}/tasks")
        async def list_tasks(
            user_id: str,
            current_user_id: str = Depends(get_current_user_id)
        ):
            # CRITICAL: Validate user_id matches token
            if user_id != current_user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to access this user's tasks"
                )
            # ... endpoint logic
    """
    try:
        user_id = extract_user_id(current_user)
        return user_id

    except ValueError as e:
        # Missing or invalid user_id in token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 3. Secure API Endpoint with User Validation (`src/api/v1/tasks.py`)

```python
"""
Task API endpoints with comprehensive user isolation.

CRITICAL SECURITY:
- All endpoints validate URL user_id matches JWT user_id
- Users can ONLY access their own tasks
- TaskService layer enforces additional user validation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlmodel import Session
from typing import Optional
from uuid import UUID

from ...db.session import get_session
from ...auth.dependencies import get_current_user_id
from ...schemas.task import TaskCreate, TaskResponse, TaskUpdate
from ...services.task_service import TaskService
from ...services.exceptions import UnauthorizedError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/{user_id}/tasks",
    tags=["tasks"],
)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_create: TaskCreate,
    response: Response,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    CRITICAL SECURITY:
    - Validates URL user_id matches JWT user_id
    - Users can ONLY create tasks for themselves
    """
    try:
        # CRITICAL: Validate URL user_id matches token user_id
        if user_id != current_user_id:
            raise UnauthorizedError("Not authorized to access this resource")

        # Create task using service layer
        task = TaskService.create_task(
            session=session,
            user_id=current_user_id,
            task_create=task_create
        )

        # Set Location header for REST best practices
        response.headers["Location"] = f"/api/{user_id}/tasks/{task.id}"

        logger.info(f"User {current_user_id} created task {task.id}")

        return TaskResponse.model_validate(task)

    except Exception as e:
        logger.error(f"Error creating task for user {current_user_id}: {str(e)}", exc_info=True)
        if isinstance(e, (HTTPException, UnauthorizedError)):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
) -> list[TaskResponse]:
    """
    List all tasks for the authenticated user.

    CRITICAL SECURITY:
    - Validates URL user_id matches JWT user_id
    - Users can ONLY see their own tasks
    """
    try:
        # CRITICAL: Validate URL user_id matches token user_id
        if user_id != current_user_id:
            raise UnauthorizedError("Not authorized to access this resource")

        # Get tasks for authenticated user only
        tasks, total = TaskService.get_user_tasks(
            session=session,
            user_id=current_user_id,
            completed=completed,
            limit=limit,
            offset=offset
        )

        logger.info(f"User {current_user_id} retrieved {len(tasks)} tasks (total: {total})")

        return [TaskResponse.model_validate(task) for task in tasks]

    except Exception as e:
        logger.error(f"Error listing tasks for user {current_user_id}: {str(e)}", exc_info=True)
        if isinstance(e, (HTTPException, UnauthorizedError)):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Response:
    """
    Delete a task for the authenticated user.

    CRITICAL SECURITY:
    - Validates URL user_id matches JWT user_id
    - TaskService validates task belongs to user before deletion
    """
    try:
        # CRITICAL: Validate URL user_id matches token user_id
        if user_id != current_user_id:
            raise UnauthorizedError("Not authorized to access this resource")

        # Delete task with user_id validation
        deleted = TaskService.delete_task(
            session=session,
            task_id=task_id,
            user_id=current_user_id
        )

        if not deleted:
            logger.warning(f"User {current_user_id} attempted to delete task {task_id} (not found)")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"User {current_user_id} deleted task {task_id}")

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {current_user_id}: {str(e)}", exc_info=True)
        if isinstance(e, (HTTPException, UnauthorizedError)):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
```

## Installation

```bash
# Install dependencies
pip install fastapi python-jose[cryptography] python-dotenv sqlmodel

# Or with uv
uv add fastapi python-jose[cryptography] python-dotenv sqlmodel
```

## Environment Variables

```bash
# .env
BETTER_AUTH_SECRET=your-super-secret-key-here-make-it-long-and-random
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname
CORS_ORIGINS=http://localhost:3000
```

**CRITICAL**: `BETTER_AUTH_SECRET` must be the same in both Next.js and FastAPI!

## Security Checklist

✅ **Same secret in both services** - `BETTER_AUTH_SECRET` matches
✅ **HS256 algorithm** - Symmetric signing with shared secret
✅ **User_id validation** - URL vs JWT in all endpoints
✅ **HTTPBearer scheme** - Automatic 401 on missing token
✅ **Token expiration** - Automatically validated by python-jose
✅ **Error handling** - No sensitive info in error messages
✅ **Logging** - Security events logged for audit
✅ **CORS configured** - Only allowed origins can access

## Testing

```python
# tests/test_auth.py
import pytest
from jose import jwt
import os

def test_jwt_validation():
    secret = os.getenv("BETTER_AUTH_SECRET")

    # Create test token
    payload = {"sub": "test-user-123", "exp": 9999999999}
    token = jwt.encode(payload, secret, algorithm="HS256")

    # Validate token
    from src.auth.jwt import verify_jwt_token
    decoded = verify_jwt_token(token)

    assert decoded["sub"] == "test-user-123"
```

## Common Errors & Solutions

### Error: "Invalid JWT token: Not enough segments"
**Cause**: Token not properly formatted
**Solution**: Ensure token is in format `Bearer <token>` and Better Auth is minting JWTs

### Error: "Invalid token: missing user_id in 'sub' claim"
**Cause**: JWT doesn't contain user ID
**Solution**: Verify Better Auth configuration includes user ID in JWT payload

### Error: "Not authorized to access this resource" (403)
**Cause**: URL user_id doesn't match JWT user_id
**Solution**: This is correct behavior - user trying to access another user's data

## Best Practices

1. **Always validate URL vs JWT user_id** - Never skip this check
2. **Use dependency injection** - Consistent auth across endpoints
3. **Log security events** - Track authentication attempts
4. **Handle errors gracefully** - Don't leak sensitive info
5. **Test auth flows** - Unit test JWT validation logic
6. **Rotate secrets** - Change BETTER_AUTH_SECRET periodically
7. **Use HTTPS in production** - Never send JWTs over HTTP
