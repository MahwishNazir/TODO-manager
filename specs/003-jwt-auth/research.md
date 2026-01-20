# JWT Authentication Research: FastAPI + Next.js Integration

**Feature**: 003-jwt-auth
**Date**: 2026-01-12
**Purpose**: Technical research for implementing JWT-based authentication using Better Auth on Next.js App Router frontend and PyJWT verification on FastAPI backend with shared secret.

---

## Executive Summary

This research documents the technical approach for securing a FastAPI REST API with JWT authentication issued by Better Auth on a Next.js App Router frontend. The solution uses:

- **Frontend**: Better Auth library with Next.js App Router for user registration/login and JWT issuance
- **Backend**: PyJWT library with FastAPI for JWT verification middleware
- **Algorithm**: HS256 (HMAC with SHA-256) with shared secret key
- **Token Storage**: HttpOnly cookies (primary) with localStorage fallback
- **Token Lifetime**: 1-hour access tokens with refresh mechanism
- **Architecture**: Stateless backend with no session storage

This approach maintains zero breaking changes to existing REST API endpoints while enforcing strict user isolation and security.

---

## 1. Better Auth Setup for Next.js App Router

### Decision: Better Auth Library

**Chosen**: Better Auth with JWT plugin for Next.js 14+ App Router

**Rationale**:
- Native Next.js App Router support with Server Components integration
- Built-in JWT token issuance via plugin architecture
- Automatic cookie handling through `nextCookies` plugin
- Simpler configuration than NextAuth.js v5 for stateless JWT scenarios
- Active development and modern API design aligned with React Server Components
- Performance: 8-10ms validation time with zero database roundtrips

### Installation

```bash
npm install better-auth
```

### Configuration

**File**: `auth.ts` (Next.js project root or `lib/auth.ts`)

```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { nextCookies } from "better-auth/adapters/next"

export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL, // Neon PostgreSQL connection
  },
  secret: process.env.BETTER_AUTH_SECRET, // Shared with FastAPI backend
  plugins: [
    jwt({
      // JWT configuration
      expiresIn: "1h", // 1-hour access token lifetime
      issuer: "todo-app",
      audience: "todo-api",
    }),
    nextCookies(), // Automatic cookie handling for App Router
  ],
})
```

### Environment Variables

```env
# Shared secret for JWT signing (minimum 32 characters, 256 bits)
BETTER_AUTH_SECRET=your-secure-secret-key-min-32-chars

# Neon PostgreSQL connection
DATABASE_URL=postgresql://user:password@host/dbname
```

### Server Component Integration

**File**: `app/api/auth/[...all]/route.ts`

```typescript
import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth.handler)
```

**File**: `app/dashboard/page.tsx` (Protected Server Component)

```typescript
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    redirect("/login")
  }

  return (
    <div>
      <h1>Welcome {session.user.email}</h1>
      <p>User ID: {session.user.id}</p>
    </div>
  )
}
```

### Client-Side Usage

**File**: `lib/auth-client.ts`

```typescript
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
})

// Usage in components
export async function loginUser(email: string, password: string) {
  const result = await authClient.signIn.email({
    email,
    password,
  })

  return result
}

// Get JWT token for API calls
export async function getJWTToken() {
  const token = await authClient.token()
  return token // Use in Authorization: Bearer {token}
}
```

### Alternatives Considered

1. **NextAuth.js v5 (Auth.js)**
   - **Pros**: Most popular, extensive provider support, mature ecosystem
   - **Cons**: Complex v5 migration, heavier for stateless JWT-only use cases, more configuration overhead
   - **Why Rejected**: Better Auth offers simpler API for JWT-only stateless authentication and better App Router integration

2. **Clerk**
   - **Pros**: Hosted solution, beautiful UI components, enterprise features
   - **Cons**: External dependency, vendor lock-in, potential cost scaling, data sovereignty concerns
   - **Why Rejected**: Project requires self-hosted solution with full control over authentication flow

3. **Custom JWT Implementation**
   - **Pros**: Full control, minimal dependencies, learning opportunity
   - **Cons**: Security risks, complex edge cases (token rotation, CSRF), maintenance burden
   - **Why Rejected**: Better Auth provides battle-tested security with minimal complexity overhead

---

## 2. PyJWT Library Usage for FastAPI

### Decision: PyJWT with FastAPI Dependency Injection

**Chosen**: PyJWT 2.10+ with custom HTTPBearer middleware using FastAPI's dependency injection system

**Rationale**:
- Official FastAPI documentation recommends PyJWT for JWT operations
- Simpler API than python-jose with focused JWT functionality
- Excellent performance: <5ms token validation on typical hardware
- Well-maintained with active security updates
- Natural integration with FastAPI's security utilities
- Type-safe with proper typing annotations

### Installation

```bash
pip install pyjwt[crypto]
# [crypto] adds cryptography library for RSA/ECDSA algorithms (optional for HS256)
# For HS256 only: pip install pyjwt
```

**File**: `backend/requirements.txt`

```text
fastapi==0.115.0
pyjwt==2.10.1
python-multipart==0.0.6
```

### JWT Utilities Module

**File**: `backend/src/utils/jwt.py`

```python
"""
JWT token verification utilities for FastAPI.

Uses PyJWT library with HS256 algorithm and shared secret.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from src.config import settings

logger = logging.getLogger(__name__)


def decode_jwt(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload with claims
        None: If token is invalid or expired

    Raises:
        No exceptions - returns None on any validation failure
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat", "sub"],
            },
            issuer="todo-app",
            audience="todo-api",
            leeway=10,  # 10-second leeway for clock skew
        )

        # Extract user_id from 'sub' (subject) claim
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("JWT token missing 'sub' claim")
            return None

        return payload

    except ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding JWT: {e}")
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user_id from JWT token.

    Args:
        token: JWT token string

    Returns:
        str: User ID from 'sub' claim
        None: If token is invalid or missing user_id
    """
    payload = decode_jwt(token)
    if not payload:
        return None

    return payload.get("sub")
```

### Configuration

**File**: `backend/src/config.py`

```python
"""
Application configuration from environment variables.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # JWT Configuration
    JWT_SECRET: str  # Same as BETTER_AUTH_SECRET in Next.js
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # Database
    DATABASE_URL: str

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "TODO API"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

**File**: `backend/.env`

```env
# Must match BETTER_AUTH_SECRET from Next.js exactly
JWT_SECRET=your-secure-secret-key-min-32-chars

# Database
DATABASE_URL=postgresql://user:password@host/dbname
```

### Alternatives Considered

1. **python-jose**
   - **Pros**: Used in older FastAPI documentation examples
   - **Cons**: Heavier dependency with cryptography backend requirements, less actively maintained than PyJWT
   - **Why Rejected**: PyJWT offers simpler API with equivalent security and better maintenance

2. **fastapi-jwt-auth**
   - **Pros**: Higher-level abstraction with automatic token refresh, built-in cookie handling
   - **Cons**: Additional dependency layer, potential version compatibility issues, less flexibility for custom flows
   - **Why Rejected**: Adds unnecessary complexity for our stateless JWT verification needs

3. **AuthLib**
   - **Pros**: Comprehensive OAuth2/OIDC support, multiple authentication schemes
   - **Cons**: Overkill for simple JWT verification, steeper learning curve, heavier package
   - **Why Rejected**: Project only needs JWT verification, not full OAuth2 implementation

---

## 3. JWT Verification Middleware Implementation

### Decision: FastAPI Dependency Injection with HTTPBearer

**Chosen**: Custom HTTPBearer subclass with FastAPI dependency injection for per-route JWT verification

**Rationale**:
- FastAPI's dependency system provides natural middleware integration
- HTTPBearer handles Authorization header parsing automatically
- Per-route flexibility (some routes can be public, others protected)
- Type-safe user_id injection into route handlers
- Testable in isolation without full app context
- Performance: Minimal overhead, runs only on protected routes

### Implementation

**File**: `backend/src/api/dependencies.py`

```python
"""
FastAPI dependencies for authentication and database.
"""
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from src.database import engine
from src.utils.jwt import get_user_id_from_token

logger = logging.getLogger(__name__)

# HTTPBearer scheme for JWT token extraction
bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT token in Authorization header",
    auto_error=True,  # Automatically return 401 if token missing
)


def get_db() -> Session:
    """
    Database session dependency.

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
) -> str:
    """
    Extract and validate user_id from JWT token.

    This dependency verifies the JWT token from the Authorization header
    and returns the user_id for use in route handlers.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        str: Verified user_id from JWT token

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing user_id
    """
    token = credentials.credentials

    # Decode and verify token
    user_id = get_user_id_from_token(token)

    if not user_id:
        logger.warning("JWT verification failed - invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"Authenticated user: {user_id}")
    return user_id
```

### Route Integration

**File**: `backend/src/api/routes/tasks.py` (Modified Endpoints)

```python
"""
Task API routes with JWT authentication.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from src.api.dependencies import get_db, get_current_user_id
from src.models.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from src.services import task_service

router = APIRouter()


@router.post(
    "/tasks",  # Changed from /{user_id}/tasks
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
def create_task(
    task_data: TaskCreate,
    user_id: Annotated[str, Depends(get_current_user_id)],  # From JWT
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Create a new task for authenticated user.

    User ID is automatically extracted from JWT token.

    Args:
        task_data: Task creation data (title)
        user_id: User ID from JWT token (dependency injection)
        db: Database session

    Returns:
        TaskResponse: Created task with generated ID
    """
    task = task_service.create_task(db, user_id, task_data.title)
    return task


@router.get(
    "/tasks",  # Changed from /{user_id}/tasks
    response_model=TaskListResponse,
    tags=["Tasks"],
)
def get_tasks(
    user_id: Annotated[str, Depends(get_current_user_id)],  # From JWT
    db: Session = Depends(get_db),
) -> TaskListResponse:
    """
    Get all tasks for authenticated user.

    User ID is automatically extracted from JWT token.
    """
    tasks = task_service.get_all_tasks(db, user_id)
    return TaskListResponse(tasks=tasks, count=len(tasks))


@router.delete(
    "/tasks/{task_id}",  # Changed from /{user_id}/tasks/{task_id}
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
)
def delete_task(
    task_id: Annotated[int, Path(..., gt=0)],
    user_id: Annotated[str, Depends(get_current_user_id)],  # From JWT
    db: Session = Depends(get_db),
):
    """
    Delete a task for authenticated user.
    """
    success = task_service.delete_task(db, user_id, task_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    return None
```

### Testing JWT Middleware

**File**: `backend/tests/unit/test_jwt_middleware.py`

```python
"""
Unit tests for JWT verification middleware.
"""
import pytest
from datetime import datetime, timedelta, timezone
import jwt

from src.config import settings
from src.utils.jwt import decode_jwt, get_user_id_from_token


def create_test_token(user_id: str, exp_minutes: int = 60) -> str:
    """Helper to create test JWT tokens."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=exp_minutes),
        "iss": "todo-app",
        "aud": "todo-api",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def test_decode_valid_token():
    """Test decoding a valid JWT token."""
    token = create_test_token("user123")
    payload = decode_jwt(token)

    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["iss"] == "todo-app"
    assert payload["aud"] == "todo-api"


def test_decode_expired_token():
    """Test decoding an expired JWT token."""
    token = create_test_token("user123", exp_minutes=-1)  # Expired 1 min ago
    payload = decode_jwt(token)

    assert payload is None  # Should return None for expired token


def test_decode_tampered_token():
    """Test decoding a token with invalid signature."""
    token = create_test_token("user123")
    tampered_token = token[:-10] + "tampered!!"  # Corrupt signature

    payload = decode_jwt(tampered_token)
    assert payload is None


def test_get_user_id_from_valid_token():
    """Test extracting user_id from valid token."""
    token = create_test_token("user456")
    user_id = get_user_id_from_token(token)

    assert user_id == "user456"


def test_get_user_id_from_invalid_token():
    """Test extracting user_id from invalid token."""
    user_id = get_user_id_from_token("invalid.token.here")

    assert user_id is None
```

### Alternatives Considered

1. **Global Middleware (Starlette Middleware)**
   - **Pros**: Applies to all routes automatically, centralized authentication logic
   - **Cons**: No per-route flexibility, harder to test, runs on public routes unnecessarily, all-or-nothing approach
   - **Why Rejected**: Some routes need to be public (health checks, docs), dependency injection provides better control

2. **Decorator-Based Authentication**
   - **Pros**: Pythonic, familiar pattern from Flask
   - **Cons**: Less type-safe, doesn't integrate with FastAPI dependency system, harder to compose dependencies
   - **Why Rejected**: FastAPI's dependency injection is more idiomatic and type-safe

3. **JWT in Cookies Only (No Authorization Header)**
   - **Pros**: Automatic browser handling, some CSRF protection with SameSite
   - **Cons**: Harder for non-browser clients (mobile apps, CLI tools), requires CSRF tokens, complicates CORS
   - **Why Rejected**: Authorization header is more flexible for various client types and standard for REST APIs

---

## 4. Shared Secret Configuration

### Decision: Environment Variable with Validation

**Chosen**: Shared `BETTER_AUTH_SECRET` environment variable synchronized between Next.js and FastAPI with startup validation

**Rationale**:
- Simple deployment model (single secret to manage)
- Compatible with Docker, Kubernetes, and cloud platforms
- Easy to rotate (update env var, restart services)
- No key management infrastructure needed for MVP
- HS256 algorithm provides adequate security for shared secret scenario
- Validates on startup to catch misconfigurations early

### Configuration Management

**Next.js Environment (.env.local)**

```env
# JWT Shared Secret (minimum 32 characters, 256 bits)
BETTER_AUTH_SECRET=your-very-secure-random-string-min-32-characters-do-not-commit

# Database
DATABASE_URL=postgresql://user:password@neon-host/dbname

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**FastAPI Environment (.env)**

```env
# JWT Shared Secret (MUST match BETTER_AUTH_SECRET from Next.js)
JWT_SECRET=your-very-secure-random-string-min-32-characters-do-not-commit

# Database
DATABASE_URL=postgresql://user:password@neon-host/dbname

# API Configuration
API_V1_PREFIX=/api/v1
```

### Secret Generation

```bash
# Generate secure random secret (Linux/macOS)
openssl rand -base64 32

# Generate secure random secret (Python)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate secure random secret (Node.js)
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### Startup Validation

**File**: `backend/src/main.py`

```python
"""
FastAPI application entrypoint with JWT secret validation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routes import tasks

# Validate JWT secret on startup
if not settings.JWT_SECRET or len(settings.JWT_SECRET) < 32:
    raise ValueError(
        "JWT_SECRET must be set and at least 32 characters long. "
        "Generate with: openssl rand -base64 32"
    )

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX, tags=["Tasks"])


@app.get("/health")
def health_check():
    """Health check endpoint (no authentication required)."""
    return {"status": "healthy"}
```

### Security Considerations

1. **Secret Rotation Strategy**
   - Current limitation: Rotating secret invalidates all existing tokens
   - Users must re-login after secret rotation
   - For production: Consider JWT key versioning with multiple valid keys during rotation window
   - Rotate secret quarterly or after suspected compromise

2. **Secret Storage Best Practices**
   - Never commit secrets to version control (`.env` in `.gitignore`)
   - Use separate secrets for development, staging, production
   - Consider secret management services (AWS Secrets Manager, HashiCorp Vault) for production
   - Restrict access to production secrets to DevOps team only

3. **Algorithm Security**
   - HS256 (HMAC-SHA256) is adequate for shared secret scenarios
   - Minimum 256-bit (32-byte) key strength required
   - For higher security (future): Consider RS256 (RSA) with public/private key pairs

### Alternatives Considered

1. **Asymmetric Keys (RS256 with RSA)**
   - **Pros**: Public key can be shared freely, private key only on auth server, better for multi-service architectures
   - **Cons**: More complex key management, requires public key distribution, slower verification
   - **Why Rejected**: HS256 is simpler for two-service architecture, adequate security for MVP

2. **Key Management Service (AWS Secrets Manager, Vault)**
   - **Pros**: Centralized secret management, audit logs, automatic rotation, access controls
   - **Cons**: Additional infrastructure, external dependency, complexity, potential cost
   - **Why Rejected**: Over-engineering for Phase II MVP, revisit for Phase V production deployment

3. **Separate Secrets with Key Exchange**
   - **Pros**: Each service has its own secret, reduced blast radius
   - **Cons**: Requires key exchange protocol, more complex, additional network calls
   - **Why Rejected**: Unnecessary complexity for stateless JWT verification with shared secret

---

## 5. JWT Token Structure and Claims

### Decision: Standard JWT Claims with Custom User Data

**Chosen**: RFC 7519 compliant JWT with registered claims (sub, exp, iat, iss, aud) plus custom user claims

**Rationale**:
- Standards-compliant for interoperability with any JWT library
- `sub` (subject) holds user_id for database queries
- `exp` (expiration) enforces 1-hour token lifetime
- `iat` (issued at) enables token freshness checks
- `iss` (issuer) and `aud` (audience) prevent token misuse across services
- Minimal payload size keeps HTTP headers under 1KB
- All claims verifiable by PyJWT without custom logic

### Token Structure

#### Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### Payload (Claims)

```json
{
  "sub": "uuid-or-user-id",
  "email": "user@example.com",
  "iat": 1704067200,
  "exp": 1704070800,
  "iss": "todo-app",
  "aud": "todo-api"
}
```

#### Signature

```text
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  BETTER_AUTH_SECRET
)
```

### Complete Token Example

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA0MDY3MjAwLCJleHAiOjE3MDQwNzA4MDAsImlzcyI6InRvZG8tYXBwIiwiYXVkIjoidG9kby1hcGkifQ.signature-here
```

### Claim Definitions

| Claim | Type | Description | Required | Verified By |
|-------|------|-------------|----------|-------------|
| `sub` | string | User ID (primary key from database) | Yes | FastAPI extracts for queries |
| `email` | string | User email address | Yes | Frontend display, logging |
| `iat` | number | Issued at timestamp (Unix epoch) | Yes | PyJWT validates not in future |
| `exp` | number | Expiration timestamp (iat + 1 hour) | Yes | PyJWT validates not expired |
| `iss` | string | Issuer identifier ("todo-app") | Yes | PyJWT validates matches config |
| `aud` | string | Audience identifier ("todo-api") | Yes | PyJWT validates matches config |

### Better Auth Configuration for Claims

**File**: `lib/auth.ts` (Next.js)

```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [
    jwt({
      expiresIn: "1h",
      issuer: "todo-app",
      audience: "todo-api",
      schema: {
        // Custom claims added to JWT payload
        user: {
          fields: {
            id: "required",      // Maps to 'sub' claim
            email: "required",   // Added to payload
          }
        }
      }
    }),
  ],
})
```

### PyJWT Verification Configuration

**File**: `backend/src/utils/jwt.py`

```python
import jwt

def decode_jwt(token: str) -> Optional[dict]:
    """Decode and verify JWT token with claim validation."""
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=["HS256"],
        options={
            "verify_signature": True,   # Verify HMAC signature
            "verify_exp": True,         # Verify expiration time
            "verify_iat": True,         # Verify issued-at time
            "require": ["exp", "iat", "sub"],  # Required claims
        },
        issuer="todo-app",              # Must match token issuer
        audience="todo-api",            # Must match token audience
        leeway=10,                      # 10-second clock skew tolerance
    )

    return payload
```

### Token Size Considerations

**Typical Token Size**: ~350-400 bytes (Base64 encoded)

- **Header**: ~30 bytes
- **Payload**: ~200-250 bytes (6 claims)
- **Signature**: ~43 bytes (HS256)
- **Separators**: 2 bytes (dots)

**HTTP Header Impact**:
- Authorization header: `Bearer {token}` = ~410 bytes
- Well within typical 8KB header size limits
- Negligible network overhead (<0.5KB per request)

### Security Considerations

1. **Sensitive Data in Claims**
   - Never include passwords, API keys, or secrets in JWT payload
   - JWT payload is Base64-encoded (NOT encrypted), readable by anyone
   - Only include user_id, email, and metadata needed for authorization

2. **Token Expiration Strategy**
   - 1-hour expiration balances security and user experience
   - Short lifetime limits damage from token theft
   - Refresh mechanism prevents frequent re-logins

3. **Audience and Issuer Validation**
   - Prevents token reuse across different services/environments
   - Protects against token confusion attacks
   - Ensures tokens are used for intended purpose

### Alternatives Considered

1. **Encrypted JWT (JWE)**
   - **Pros**: Payload encrypted, safe for sensitive data
   - **Cons**: Larger tokens, slower processing, more complex
   - **Why Rejected**: No sensitive data in our tokens, performance priority

2. **Minimal Claims (sub and exp only)**
   - **Pros**: Smaller token size
   - **Cons**: Less metadata for logging/debugging, no issuer/audience protection
   - **Why Rejected**: Additional claims provide security benefits with minimal size cost

3. **Extended Claims (roles, permissions, metadata)**
   - **Pros**: Rich authorization data in token, fewer database queries
   - **Cons**: Larger tokens, stale data (permissions change), logout complexity
   - **Why Rejected**: Keep tokens minimal, query database for latest authorization data

---

## 6. Error Handling for Invalid/Expired Tokens

### Decision: HTTP 401 with Structured Error Responses

**Chosen**: Return HTTP 401 Unauthorized with detailed error messages in JSON format, including WWW-Authenticate header

**Rationale**:
- HTTP 401 is semantic standard for authentication failures
- WWW-Authenticate header guides clients on re-authentication
- Structured JSON errors enable frontend to handle specific scenarios
- Clear error messages improve debugging and user experience
- Separate error codes for expired vs. invalid tokens enables smart retry logic
- Security: Don't leak implementation details (generic errors for tampered tokens)

### Error Response Schema

**File**: `backend/src/models/schemas.py`

```python
"""
Pydantic schemas for API requests and responses.
"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str
    error_code: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid or expired authentication token",
                "error_code": "TOKEN_EXPIRED"
            }
        }
```

### Error Handling Implementation

**File**: `backend/src/utils/jwt.py` (Enhanced)

```python
"""
JWT utilities with detailed error tracking.
"""
from enum import Enum


class JWTError(Enum):
    """JWT verification error types."""
    EXPIRED = "TOKEN_EXPIRED"
    INVALID_SIGNATURE = "TOKEN_INVALID_SIGNATURE"
    MALFORMED = "TOKEN_MALFORMED"
    MISSING_CLAIMS = "TOKEN_MISSING_CLAIMS"
    INVALID_ISSUER = "TOKEN_INVALID_ISSUER"
    INVALID_AUDIENCE = "TOKEN_INVALID_AUDIENCE"


def decode_jwt(token: str) -> tuple[Optional[dict], Optional[JWTError]]:
    """
    Decode and verify JWT token with error tracking.

    Returns:
        tuple: (payload dict or None, error type or None)
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat", "sub"],
            },
            issuer="todo-app",
            audience="todo-api",
            leeway=10,
        )

        return (payload, None)

    except ExpiredSignatureError:
        logger.warning("JWT token expired")
        return (None, JWTError.EXPIRED)

    except jwt.InvalidSignatureError:
        logger.warning("JWT token has invalid signature")
        return (None, JWTError.INVALID_SIGNATURE)

    except jwt.InvalidIssuerError:
        logger.warning("JWT token has invalid issuer")
        return (None, JWTError.INVALID_ISSUER)

    except jwt.InvalidAudienceError:
        logger.warning("JWT token has invalid audience")
        return (None, JWTError.INVALID_AUDIENCE)

    except jwt.MissingRequiredClaimError as e:
        logger.warning(f"JWT token missing required claim: {e}")
        return (None, JWTError.MISSING_CLAIMS)

    except jwt.DecodeError:
        logger.warning("JWT token is malformed")
        return (None, JWTError.MALFORMED)

    except Exception as e:
        logger.error(f"Unexpected JWT error: {e}")
        return (None, JWTError.MALFORMED)
```

**File**: `backend/src/api/dependencies.py` (Enhanced Error Handling)

```python
"""
Authentication dependencies with detailed error responses.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.utils.jwt import decode_jwt, JWTError


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
) -> str:
    """
    Extract and validate user_id from JWT token with detailed errors.
    """
    token = credentials.credentials

    payload, error = decode_jwt(token)

    if error == JWTError.EXPIRED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    if error == JWTError.INVALID_SIGNATURE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    if error in [JWTError.MALFORMED, JWTError.MISSING_CLAIMS]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    if error in [JWTError.INVALID_ISSUER, JWTError.INVALID_AUDIENCE]:
        logger.error(f"JWT token with wrong issuer/audience: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    return payload["sub"]
```

### Frontend Error Handling

**File**: `lib/api-client.ts` (Next.js)

```typescript
/**
 * API client with automatic token refresh on 401 errors.
 */
import { authClient } from "./auth-client"

export class APIError extends Error {
  constructor(
    public status: number,
    public message: string,
    public code?: string
  ) {
    super(message)
  }
}

export async function fetchAPI(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = await authClient.token()

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  })

  // Handle 401 errors (authentication failures)
  if (response.status === 401) {
    const errorData = await response.json()

    // Check if token expired
    if (errorData.detail?.includes("expired")) {
      // Attempt token refresh
      try {
        await authClient.refresh()

        // Retry original request with new token
        const newToken = await authClient.token()
        const retryResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
          {
            ...options,
            headers: {
              ...options.headers,
              "Authorization": `Bearer ${newToken}`,
              "Content-Type": "application/json",
            },
          }
        )

        if (retryResponse.ok) {
          return retryResponse
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = "/login"
        throw new APIError(401, "Session expired. Please login again.")
      }
    }

    // Other 401 errors (invalid token, etc.)
    window.location.href = "/login"
    throw new APIError(401, errorData.detail || "Authentication failed")
  }

  if (!response.ok) {
    const errorData = await response.json()
    throw new APIError(
      response.status,
      errorData.detail || "Request failed",
      errorData.error_code
    )
  }

  return response
}
```

### Error Response Examples

**Expired Token**:
```json
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer error="invalid_token"
Content-Type: application/json

{
  "detail": "Authentication token has expired. Please login again."
}
```

**Invalid Signature (Tampered Token)**:
```json
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer error="invalid_token"
Content-Type: application/json

{
  "detail": "Invalid authentication token."
}
```

**Missing Token**:
```json
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
Content-Type: application/json

{
  "detail": "Not authenticated"
}
```

### Security Considerations

1. **Error Message Disclosure**
   - Avoid exposing internal implementation details in error messages
   - Generic "Invalid authentication token" for security-sensitive errors
   - Specific "Token expired" message is safe and improves UX

2. **Timing Attacks**
   - JWT verification time should be constant regardless of error type
   - PyJWT handles this internally with constant-time comparisons

3. **Brute Force Protection**
   - Consider rate limiting on authentication endpoints (not covered in this phase)
   - Log repeated authentication failures for monitoring

### Alternatives Considered

1. **HTTP 403 Forbidden for Expired Tokens**
   - **Pros**: Distinguishes "who you are" (401) from "what you can do" (403)
   - **Cons**: 401 is semantic standard for auth failures including expiration
   - **Why Rejected**: Industry standard is 401 for both missing and expired tokens

2. **Custom Error Codes in Response Body Only**
   - **Pros**: More detailed error taxonomy
   - **Cons**: Clients must parse response body to determine auth failure
   - **Why Rejected**: HTTP status codes should convey semantic meaning, use both status + details

3. **Silent Token Refresh Without User Awareness**
   - **Pros**: Seamless user experience
   - **Cons**: Can hide authentication issues, complexity in handling refresh failures
   - **Why Rejected**: Explicit refresh attempt in API client provides better error handling control

---

## 7. Token Refresh Implementation

### Decision: Manual Refresh with Better Auth Session Extension

**Chosen**: Frontend-initiated token refresh before expiration using Better Auth's session extension mechanism

**Rationale**:
- Proactive refresh prevents interruption during user activity
- Better Auth provides built-in session extension without separate refresh tokens
- Stateless backend doesn't need refresh token storage
- Frontend controls refresh timing (e.g., 5 minutes before expiration)
- Simpler than refresh token rotation schemes
- Adequate security for 1-hour token lifetime with proper HTTPS

### Better Auth Refresh Configuration

**File**: `lib/auth.ts` (Next.js)

```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  session: {
    expiresIn: 60 * 60, // 1 hour in seconds
    updateAge: 60 * 5,  // Update session if older than 5 minutes
  },
  plugins: [
    jwt({
      expiresIn: "1h",
      issuer: "todo-app",
      audience: "todo-api",
    }),
  ],
})
```

### Frontend Refresh Logic

**File**: `lib/auth-client.ts` (Enhanced)

```typescript
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
})

/**
 * Get JWT token with automatic refresh if needed.
 *
 * Checks token expiration and refreshes if within 5 minutes of expiry.
 */
export async function getValidToken(): Promise<string> {
  const session = await authClient.getSession()

  if (!session) {
    throw new Error("No active session")
  }

  // Check if token expires within 5 minutes
  const expiresAt = session.expiresAt
  const fiveMinutesFromNow = Date.now() + (5 * 60 * 1000)

  if (expiresAt < fiveMinutesFromNow) {
    // Token expiring soon, refresh it
    await authClient.session.refresh()
  }

  // Get fresh token
  const token = await authClient.token()
  return token
}

/**
 * Force token refresh (e.g., after 401 error).
 */
export async function refreshToken(): Promise<string> {
  await authClient.session.refresh()
  return await authClient.token()
}
```

### Automatic Refresh Hook (React)

**File**: `hooks/useTokenRefresh.ts`

```typescript
import { useEffect } from "react"
import { authClient } from "@/lib/auth-client"

/**
 * Automatically refresh token every 50 minutes (10 min before expiry).
 *
 * Hook runs in background to keep session alive during user activity.
 */
export function useTokenRefresh() {
  useEffect(() => {
    const REFRESH_INTERVAL = 50 * 60 * 1000 // 50 minutes

    const intervalId = setInterval(async () => {
      try {
        const session = await authClient.getSession()

        if (session) {
          await authClient.session.refresh()
          console.log("Token refreshed automatically")
        }
      } catch (error) {
        console.error("Auto-refresh failed:", error)
        // Don't throw - let user continue with current token
        // Next API call will handle expiration with retry
      }
    }, REFRESH_INTERVAL)

    return () => clearInterval(intervalId)
  }, [])
}
```

**Usage in Layout**:

```typescript
// app/layout.tsx
import { useTokenRefresh } from "@/hooks/useTokenRefresh"

export default function RootLayout({ children }) {
  useTokenRefresh() // Activate auto-refresh

  return (
    <html>
      <body>{children}</body>
    </html>
  )
}
```

### API Client Integration

**File**: `lib/api-client.ts` (Enhanced with Refresh)

```typescript
import { getValidToken, refreshToken } from "./auth-client"

/**
 * Fetch API with automatic token refresh on 401.
 */
export async function fetchAPI(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  // Get valid token (auto-refreshes if needed)
  const token = await getValidToken()

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  })

  // Handle 401 - token might have expired despite pre-check
  if (response.status === 401) {
    try {
      // Force refresh and retry once
      const newToken = await refreshToken()

      const retryResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
        {
          ...options,
          headers: {
            ...options.headers,
            "Authorization": `Bearer ${newToken}`,
            "Content-Type": "application/json",
          },
        }
      )

      if (retryResponse.ok) {
        return retryResponse
      }

      // Refresh succeeded but still 401 - auth failure
      throw new Error("Authentication failed after refresh")
    } catch (error) {
      // Refresh failed - redirect to login
      window.location.href = "/login"
      throw error
    }
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response
}
```

### Backend Considerations

FastAPI backend remains completely stateless - no refresh endpoint needed:

- No refresh token storage in database
- No token revocation list (stateless design)
- Each request validated independently
- Token refresh handled entirely by Better Auth on frontend

### Refresh Flow Diagram

```text
User Activity → Check Token Expiry
                    ↓
            Expires in < 5min?
            ↙             ↘
          Yes              No
           ↓                ↓
    Call Better Auth    Use Current Token
    session.refresh()        ↓
           ↓            Make API Request
    Get New JWT              ↓
           ↓            [Success/Failure]
    Make API Request
```

### Security Considerations

1. **Refresh Without Re-authentication**
   - Better Auth session extension uses existing session cookie
   - Refresh only works if session is still valid (not logged out)
   - Refresh fails if session expired (requires re-login)

2. **Refresh Token Storage**
   - No separate refresh token stored (Better Auth manages session internally)
   - Session cookies are HttpOnly and Secure
   - Frontend only stores access JWT in memory/sessionStorage

3. **Preventing Refresh Abuse**
   - Better Auth rate-limits refresh requests
   - Session cookies have finite lifetime (can't refresh forever)
   - Logout invalidates session (refresh fails after logout)

### Alternatives Considered

1. **Separate Refresh Tokens (OAuth2 Pattern)**
   - **Pros**: Standard OAuth2 flow, longer refresh token lifetime, can revoke refresh tokens
   - **Cons**: Requires backend refresh token storage, more complex flow, violates stateless principle
   - **Why Rejected**: Better Auth's session extension is simpler and adequate for stateless design

2. **Automatic Background Refresh (Service Worker)**
   - **Pros**: Completely transparent to user, maintains constant token validity
   - **Cons**: Service Worker complexity, harder debugging, potential performance impact
   - **Why Rejected**: React hook provides simpler implementation with adequate UX

3. **Short-Lived Tokens Without Refresh (15-minute expiry)**
   - **Pros**: Maximum security, less damage from token theft
   - **Cons**: Frequent re-authentication annoys users, poor UX
   - **Why Rejected**: 1-hour tokens with refresh provide better security/UX balance

---

## 8. Token Storage Strategies

### Decision: HttpOnly Cookies for Primary Storage

**Chosen**: Store JWT tokens in HttpOnly, Secure, SameSite cookies set by Better Auth, with sessionStorage fallback for client-side JavaScript access

**Rationale**:
- HttpOnly cookies are immune to XSS attacks (JavaScript cannot access)
- Secure flag ensures HTTPS-only transmission
- SameSite=Lax prevents CSRF attacks from external sites
- Better Auth sets cookies automatically on login
- sessionStorage fallback enables JavaScript access for Authorization headers
- Cookies automatically sent with same-origin requests
- Balances security (HttpOnly) with functionality (JS access via sessionStorage)

### Cookie Configuration

**File**: `lib/auth.ts` (Next.js)

```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { nextCookies } from "better-auth/adapters/next"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  session: {
    cookieName: "auth_session",
    cookieOptions: {
      httpOnly: true,        // Prevent JavaScript access
      secure: true,          // HTTPS only (set false for local dev)
      sameSite: "lax",       // CSRF protection
      path: "/",
      maxAge: 60 * 60,       // 1 hour
    },
  },
  plugins: [
    jwt({
      expiresIn: "1h",
      issuer: "todo-app",
      audience: "todo-api",
    }),
    nextCookies(), // Automatic cookie handling
  ],
})
```

### Development vs. Production Configuration

**File**: `lib/auth.ts` (Environment-Aware)

```typescript
const isProduction = process.env.NODE_ENV === "production"

export const auth = betterAuth({
  session: {
    cookieOptions: {
      httpOnly: true,
      secure: isProduction,    // HTTPS in production, HTTP allowed in dev
      sameSite: isProduction ? "strict" : "lax",  // Stricter in production
      path: "/",
      maxAge: 60 * 60,
    },
  },
  // ... rest of config
})
```

### Token Storage Architecture

Better Auth uses dual storage strategy:

1. **HttpOnly Cookie**: Stores session identifier for Better Auth backend
2. **SessionStorage**: Frontend stores JWT access token for API calls

**Why Both**:
- HttpOnly cookie authenticates user with Better Auth server
- SessionStorage provides JWT for Authorization headers to FastAPI backend
- Best security (HttpOnly) + best functionality (JS access)

### Frontend Token Access

**File**: `lib/auth-client.ts`

```typescript
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
})

/**
 * Get JWT token from Better Auth session.
 *
 * Token is retrieved from Better Auth (which uses HttpOnly cookies internally)
 * and returned for use in Authorization headers.
 */
export async function getToken(): Promise<string | null> {
  try {
    const token = await authClient.token()
    return token
  } catch (error) {
    console.error("Failed to get token:", error)
    return null
  }
}

/**
 * Store token in sessionStorage for quick access.
 *
 * Note: sessionStorage is cleared when tab closes, adding security.
 */
export function cacheTokenInSession(token: string): void {
  if (typeof window !== "undefined") {
    window.sessionStorage.setItem("jwt_token", token)
  }
}

/**
 * Get token from sessionStorage cache (faster than API call).
 */
export function getCachedToken(): string | null {
  if (typeof window !== "undefined") {
    return window.sessionStorage.getItem("jwt_token")
  }
  return null
}

/**
 * Clear token cache on logout.
 */
export function clearTokenCache(): void {
  if (typeof window !== "undefined") {
    window.sessionStorage.removeItem("jwt_token")
  }
}
```

### API Client with Cached Tokens

**File**: `lib/api-client.ts`

```typescript
import { getToken, getCachedToken, cacheTokenInSession } from "./auth-client"

/**
 * Get valid token, using cache when available.
 */
async function getAuthToken(): Promise<string> {
  // Try cache first (faster)
  let token = getCachedToken()

  if (!token) {
    // Cache miss - fetch from Better Auth
    token = await getToken()

    if (!token) {
      throw new Error("No authentication token available")
    }

    // Cache for future requests
    cacheTokenInSession(token)
  }

  return token
}

export async function fetchAPI(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = await getAuthToken()

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
    {
      ...options,
      headers: {
        ...options.headers,
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  )

  return response
}
```

### Logout Implementation

**File**: `components/LogoutButton.tsx`

```typescript
"use client"

import { authClient } from "@/lib/auth-client"
import { clearTokenCache } from "@/lib/auth-client"
import { useRouter } from "next/navigation"

export function LogoutButton() {
  const router = useRouter()

  async function handleLogout() {
    try {
      // Call Better Auth logout (clears HttpOnly cookies)
      await authClient.signOut()

      // Clear sessionStorage cache
      clearTokenCache()

      // Redirect to login
      router.push("/login")
    } catch (error) {
      console.error("Logout failed:", error)
    }
  }

  return (
    <button onClick={handleLogout}>
      Logout
    </button>
  )
}
```

### Security Comparison Table

| Storage Method | XSS Protection | CSRF Protection | JS Access | Auto-Send | Recommended |
|----------------|----------------|-----------------|-----------|-----------|-------------|
| HttpOnly Cookie | ✅ Yes | ⚠️ Needs SameSite | ❌ No | ✅ Yes | Primary |
| Secure Cookie (not HttpOnly) | ❌ No | ⚠️ Needs SameSite | ✅ Yes | ✅ Yes | Avoid |
| localStorage | ❌ No | ✅ Not vulnerable | ✅ Yes | ❌ No | Avoid |
| sessionStorage | ❌ No | ✅ Not vulnerable | ✅ Yes | ❌ No | Cache Only |
| Memory Only (React state) | ✅ Yes | ✅ Not vulnerable | ✅ Yes | ❌ No | Lost on refresh |

### Security Considerations

1. **XSS Protection**
   - HttpOnly cookies prevent JavaScript access (immune to XSS)
   - sessionStorage is vulnerable to XSS if site is compromised
   - Defense-in-depth: Use Content-Security-Policy headers, sanitize inputs

2. **CSRF Protection**
   - SameSite=Lax prevents cookie sending from external origins
   - Authorization headers don't have CSRF vulnerability (not auto-sent)
   - Double Submit Cookie pattern not needed with SameSite

3. **Token Expiration**
   - Short 1-hour lifetime limits damage from token theft
   - Session closes on tab close (sessionStorage cleared)
   - User must re-login after 1 hour without refresh

### Alternatives Considered

1. **localStorage Only**
   - **Pros**: Persists across tab closes, simple implementation
   - **Cons**: Vulnerable to XSS attacks, localStorage accessible by all scripts
   - **Why Rejected**: Security risk outweighs convenience, sessionStorage is safer

2. **HttpOnly Cookies Only (No JS Access)**
   - **Pros**: Maximum XSS protection
   - **Cons**: Can't set Authorization headers for external APIs, cookie size limits
   - **Why Rejected**: FastAPI backend requires Authorization header (not cookies)

3. **Memory-Only Storage (React State)**
   - **Pros**: Most secure (cleared on refresh), no persistence risk
   - **Cons**: Lost on page reload, poor UX (frequent re-login)
   - **Why Rejected**: Poor user experience, doesn't support refresh scenarios

---

## Implementation Checklist

### Phase 1: Backend Authentication (FastAPI)

- [ ] Install PyJWT library (`pip install pyjwt`)
- [ ] Create `backend/src/config.py` with JWT configuration
- [ ] Add `JWT_SECRET` to `backend/.env` (generate 32+ character secret)
- [ ] Create `backend/src/utils/jwt.py` with decode/verify functions
- [ ] Add startup validation for JWT_SECRET in `main.py`
- [ ] Create `backend/src/api/dependencies.py` with `get_current_user_id` dependency
- [ ] Add HTTPBearer scheme for token extraction
- [ ] Write unit tests for JWT verification (`tests/unit/test_jwt_middleware.py`)
- [ ] Verify JWT decoding with valid/expired/invalid tokens

### Phase 2: Frontend Authentication (Next.js)

- [ ] Install Better Auth (`npm install better-auth`)
- [ ] Create `lib/auth.ts` with Better Auth configuration
- [ ] Add JWT plugin with 1-hour expiration
- [ ] Add nextCookies plugin for automatic cookie handling
- [ ] Configure HttpOnly + Secure + SameSite cookies
- [ ] Add `BETTER_AUTH_SECRET` to `.env.local` (same as backend JWT_SECRET)
- [ ] Create `app/api/auth/[...all]/route.ts` for Better Auth endpoints
- [ ] Create `lib/auth-client.ts` with client helpers
- [ ] Implement login/register components
- [ ] Test user registration and login flows

### Phase 3: API Integration

- [ ] Modify existing task endpoints to remove `user_id` path parameter
- [ ] Add `Depends(get_current_user_id)` to all protected endpoints
- [ ] Update OpenAPI documentation with Bearer security scheme
- [ ] Create `lib/api-client.ts` with fetchAPI helper
- [ ] Add Authorization header with JWT token
- [ ] Implement automatic token refresh on 401 errors
- [ ] Test API calls with valid JWT tokens
- [ ] Test API calls with expired/invalid tokens
- [ ] Verify user isolation (users can't access other users' tasks)

### Phase 4: Token Refresh

- [ ] Configure Better Auth session extension (`updateAge: 5 minutes`)
- [ ] Create `hooks/useTokenRefresh.ts` for automatic refresh
- [ ] Add token expiration checking before API calls
- [ ] Implement retry logic with refreshed token on 401
- [ ] Test token refresh before expiration
- [ ] Test token refresh failure (redirect to login)
- [ ] Verify long sessions work without interruption

### Phase 5: Security Hardening

- [ ] Verify HTTPS enforcement in production
- [ ] Validate cookie configuration (HttpOnly, Secure, SameSite)
- [ ] Add CORS configuration for Next.js origin
- [ ] Implement proper error messages (avoid leaking details)
- [ ] Add structured logging for authentication events
- [ ] Test XSS protection (HttpOnly cookies)
- [ ] Test CSRF protection (SameSite cookies)
- [ ] Security audit of JWT secret storage

### Phase 6: Testing

- [ ] Unit tests for PyJWT verification
- [ ] Integration tests for protected endpoints
- [ ] E2E tests for login → task operations → logout
- [ ] Test concurrent sessions (multiple devices)
- [ ] Test token expiration during active operation
- [ ] Performance test JWT verification (<5ms target)
- [ ] Load test with 1000 concurrent authenticated users

---

## Performance Benchmarks

Based on research and industry standards:

| Metric | Target | Typical | Notes |
|--------|--------|---------|-------|
| JWT Verification Time | <5ms | 2-3ms | HS256 on modern hardware |
| Token Size | <500 bytes | 350-400 bytes | 6 standard claims |
| Login Latency (E2E) | <500ms | 300-400ms | Including database roundtrip |
| Token Refresh Time | <100ms | 50-80ms | Better Auth session extension |
| API Request Overhead | <10ms | 5-8ms | JWT extraction + verification |
| Concurrent Users | 1000+ | Unlimited | Stateless backend scales horizontally |
| Database Queries per Request | 1 | 1 | Only task queries, no session lookups |

---

## Security Best Practices Summary

1. **Secret Management**
   - Minimum 32-character secret (256 bits)
   - Never commit secrets to version control
   - Rotate secrets quarterly or after compromise
   - Use separate secrets for dev/staging/production

2. **Token Lifetime**
   - 1-hour access token expiration
   - Automatic refresh 5 minutes before expiry
   - Session terminates after 1 hour without activity

3. **Transport Security**
   - HTTPS only in production (TLS 1.3)
   - HttpOnly cookies prevent XSS
   - SameSite=Lax prevents CSRF
   - Secure flag ensures HTTPS transmission

4. **Validation**
   - Verify signature, expiration, issuer, audience
   - 10-second leeway for clock skew
   - Require sub, exp, iat claims
   - Log all authentication failures

5. **Error Handling**
   - Generic errors for security-sensitive failures
   - Structured errors for client handling
   - WWW-Authenticate header for re-auth guidance
   - No implementation detail leakage

6. **Monitoring**
   - Log all authentication events
   - Track failed authentication attempts
   - Monitor token expiration patterns
   - Alert on unusual activity (many failures)

---

## Sources and References

### Better Auth Documentation
- [Next.js integration | Better Auth](https://www.better-auth.com/docs/integrations/next)
- [JWT | Better Auth](https://www.better-auth.com/docs/plugins/jwt)
- [Complete Authentication Guide for Next.js App Router in 2025](https://clerk.com/articles/complete-authentication-guide-for-nextjs-app-router)
- [Better Auth vs NextAuth (Authjs) vs Auth0 | Better Stack Community](https://betterstack.com/community/guides/scaling-nodejs/better-auth-vs-nextauth-authjs-vs-autho/)

### PyJWT and FastAPI Integration
- [OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Securing FastAPI with JWT Token-based Authentication | TestDriven.io](https://testdriven.io/blog/fastapi-jwt-auth/)
- [JWT Authentication - FastAPI Beyond CRUD](https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter9/)
- [Usage Examples — PyJWT 2.10.1 documentation](https://pyjwt.readthedocs.io/en/latest/usage.html)
- [Implementing Secure User Authentication in FastAPI using JWT Tokens and Neon Postgres - Neon Guides](https://neon.com/guides/fastapi-jwt)

### Shared Secret and HS256 Implementation
- [Building a Secure JWT Authentication System with FastAPI and Next.js | by Sebastien M. Laignel | Medium](https://medium.com/@sl_mar/building-a-secure-jwt-authentication-system-with-fastapi-and-next-js-301e749baec2)
- [Handling Authentication and Authorization with FastAPI and Next.js](https://www.david-crimi.com/blog/user-auth)
- [Combining Next.js and NextAuth with a FastAPI backend](https://tom.catshoek.dev/posts/nextauth-fastapi/)

### Token Storage and Security
- [Ultimate Guide to Securing JWT Authentication with httpOnly Cookies - Wisp CMS](https://www.wisp.blog/blog/ultimate-guide-to-securing-jwt-authentication-with-httponly-cookies)
- [LocalStorage vs Cookies: the best-practice guide to storing JWT tokens securely in your front-end - Cyber Chief](https://www.cyberchief.ai/2023/05/secure-jwt-token-storage.html)
- [What Are Refresh Tokens and How to Use Them Securely | Auth0](https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/)
- [The Developer's Guide to JWT Storage](https://www.descope.com/blog/post/developer-guide-jwt-storage)

### JWT Standards and Best Practices
- [JSON Web Token Introduction - jwt.io](https://www.jwt.io/introduction)
- [JSON Web Token Claims](https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-token-claims)
- [JWT Security Best Practices | Curity](https://curity.io/resources/learn/jwt-best-practices/)

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-12 | 1.0.0 | Initial research document | Claude (AI Assistant) |

---

**Next Steps**: Proceed to implementation planning (`plan.md`) to translate research into concrete architecture decisions and task breakdown.
