# JWT Authentication Quickstart Guide

**Feature**: JWT Authentication with Better Auth
**Branch**: `003-jwt-auth`
**Last Updated**: 2026-01-12

This guide walks through setting up JWT-based authentication for the TODO application, from development environment configuration to testing the complete authentication flow.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Backend Setup (FastAPI)](#backend-setup-fastapi)
4. [Frontend Setup (Next.js)](#frontend-setup-nextjs)
5. [Testing Authentication Flow](#testing-authentication-flow)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Required versions:**
- Node.js 18+ (for Next.js)
- Python 3.11+ (for FastAPI)
- PostgreSQL 14+ (via Neon or local)

**Existing setup from Step 1:**
- ✅ FastAPI backend with task endpoints
- ✅ Neon PostgreSQL database with tasks table
- ✅ SQLModel configured

**New dependencies to install:**
- Better Auth (frontend: JWT issuance)
- PyJWT (backend: JWT verification)

---

## Environment Configuration

### Step 1: Generate Shared Secret

The `BETTER_AUTH_SECRET` must be identical in both frontend and backend for JWT signature verification.

Generate a secure 256-bit secret:

```bash
# Linux/Mac
openssl rand -base64 32

# Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))

# Alternative: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

Example output (DO NOT use this in production):
```
Kv3z8F2xN9mQ5pW7rT4yU6gH8jL1nM0oP2aS4dF6gH8j
```

### Step 2: Configure Environment Variables

**Backend (`.env` in `backend/` directory):**

```env
# Database (existing from Step 1)
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# JWT Authentication (NEW)
BETTER_AUTH_SECRET=Kv3z8F2xN9mQ5pW7rT4yU6gH8jL1nM0oP2aS4dF6gH8j
JWT_ALGORITHM=HS256
JWT_ISSUER=todo-app
JWT_AUDIENCE=todo-api
JWT_EXPIRATION_HOURS=1

# CORS (allow Next.js frontend)
CORS_ORIGINS=http://localhost:3000
```

**Frontend (`.env.local` in `frontend/` directory):**

```env
# Better Auth Configuration
BETTER_AUTH_SECRET=Kv3z8F2xN9mQ5pW7rT4yU6gH8jL1nM0oP2aS4dF6gH8j
BETTER_AUTH_URL=http://localhost:3000

# Database connection (for Better Auth user storage)
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**IMPORTANT**:
- `BETTER_AUTH_SECRET` must be **identical** in both files
- Never commit `.env` or `.env.local` to version control
- Use different secrets for development, staging, and production

---

## Backend Setup (FastAPI)

### Step 1: Install Dependencies

```bash
cd backend

# Install PyJWT and python-jose for JWT handling
pip install PyJWT==2.10.1 python-jose[cryptography]==3.3.0

# Update requirements.txt
pip freeze > requirements.txt
```

### Step 2: Create Configuration Module

**File**: `backend/src/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # JWT Configuration
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "todo-app"
    JWT_AUDIENCE: str = "todo-api"
    JWT_EXPIRATION_HOURS: int = 1

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
```

### Step 3: Create JWT Verification Dependency

**File**: `backend/src/auth/jwt_handler.py`

```python
import jwt
from datetime import datetime
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import get_settings, Settings

security = HTTPBearer()

def verify_jwt_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)]
) -> str:
    """
    Verify JWT token and extract user_id.

    Args:
        credentials: JWT token from Authorization header
        settings: Application settings with JWT secret

    Returns:
        str: user_id extracted from JWT 'sub' claim

    Raises:
        HTTPException: 401 if token is invalid, expired, or malformed
    """
    token = credentials.credentials

    try:
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
                "require": ["sub", "email", "exp", "iat"],
                "leeway": 10,  # 10 seconds clock skew tolerance
            }
        )

        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID (sub claim)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token audience mismatch",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token issuer mismatch",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Type alias for cleaner dependency injection
CurrentUser = Annotated[str, Depends(verify_jwt_token)]
```

### Step 4: Update Task Endpoints

**File**: `backend/src/api/tasks.py` (update existing endpoints)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.jwt_handler import CurrentUser
from src.services.task_service import TaskService

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: CurrentUser,  # NEW: JWT authentication
    task_service: TaskService = Depends()
):
    """Create new task for authenticated user."""
    # Verify path user_id matches JWT user_id
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's tasks"
        )

    # Use current_user from JWT (ignore path parameter internally)
    task = await task_service.create_task(current_user, task_data)
    return task

# Similar updates for GET, PUT, PATCH, DELETE endpoints...
```

### Step 5: Update CORS Configuration

**File**: `backend/src/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings

settings = get_settings()

app = FastAPI(title="TODO API", version="1.0.0")

# Update CORS to include credentials for HttpOnly cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,  # NEW: Required for HttpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

---

## Frontend Setup (Next.js)

### Step 1: Install Better Auth

```bash
cd frontend

# Install Better Auth with JWT plugin
npm install better-auth
npm install @better-auth/react  # React hooks

# Install database adapter for PostgreSQL
npm install pg
```

### Step 2: Configure Better Auth

**File**: `frontend/src/lib/auth.ts`

```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    pool,
  },

  plugins: [
    jwt({
      issuer: "todo-app",
      audience: "todo-api",
      expiresIn: "1h",
      secret: process.env.BETTER_AUTH_SECRET!,
    }),
  ],

  session: {
    cookieOptions: {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 3600, // 1 hour (matches JWT expiration)
    },
  },

  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
});

export type Session = typeof auth.$Infer.Session;
```

### Step 3: Create Authentication API Routes

**File**: `frontend/src/app/api/auth/[...all]/route.ts`

```typescript
import { auth } from "@/lib/auth";

// Better Auth handles all authentication routes:
// POST /api/auth/register
// POST /api/auth/login
// POST /api/auth/refresh
// POST /api/auth/logout
export const { GET, POST } = auth.handler;
```

### Step 4: Create Auth Context Provider

**File**: `frontend/src/components/AuthProvider.tsx`

```typescript
"use client";

import { createAuthClient } from "@better-auth/react";
import { SessionProvider } from "@better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000",
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider client={authClient}>
      {children}
    </SessionProvider>
  );
}
```

### Step 5: Create API Client with JWT Injection

**File**: `frontend/src/lib/api-client.ts`

```typescript
import { authClient } from "@/components/AuthProvider";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function getAuthHeaders(): Promise<HeadersInit> {
  const session = await authClient.getSession();

  if (!session?.token) {
    throw new Error("Not authenticated");
  }

  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${session.token}`,
  };
}

export async function createTask(userId: string, title: string) {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE_URL}/${userId}/tasks`, {
    method: "POST",
    headers,
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired - trigger refresh
      await authClient.refreshSession();
      throw new Error("Session expired, please retry");
    }
    throw new Error(`Failed to create task: ${response.statusText}`);
  }

  return response.json();
}

// Similar functions for listTasks, updateTask, deleteTask...
```

### Step 6: Implement Auto-Refresh

**File**: `frontend/src/hooks/useTokenRefresh.ts`

```typescript
"use client";

import { useEffect } from "react";
import { authClient } from "@/components/AuthProvider";

const REFRESH_INTERVAL = 50 * 60 * 1000; // 50 minutes (10 min before expiry)

export function useTokenRefresh() {
  useEffect(() => {
    const interval = setInterval(async () => {
      const session = await authClient.getSession();

      if (session) {
        try {
          await authClient.refreshSession();
          console.log("Token refreshed successfully");
        } catch (error) {
          console.error("Token refresh failed:", error);
        }
      }
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, []);
}
```

---

## Testing Authentication Flow

### Step 1: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 2: Test Registration

```bash
# Register new user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securePassword123"
  }'

# Expected response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com"
  },
  "expires_in": 3600
}
```

### Step 3: Test Login

```bash
# Login with registered user
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securePassword123"
  }'

# Expected response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com"
  },
  "expires_in": 3600
}
```

### Step 4: Test Protected Task Endpoints

```bash
# Extract token from login response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USER_ID="550e8400-e29b-41d4-a716-446655440000"

# Test: Create task (should succeed with valid token)
curl -X POST http://localhost:8000/api/${USER_ID}/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"title": "Buy groceries"}'

# Expected response (201 Created):
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "is_completed": false,
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T10:00:00Z"
}

# Test: Create task without token (should fail)
curl -X POST http://localhost:8000/api/${USER_ID}/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "This should fail"}'

# Expected response (403 Forbidden):
{
  "detail": "Not authenticated"
}

# Test: Access another user's tasks (should fail)
WRONG_USER_ID="00000000-0000-0000-0000-000000000000"
curl -X GET http://localhost:8000/api/${WRONG_USER_ID}/tasks \
  -H "Authorization: Bearer ${TOKEN}"

# Expected response (403 Forbidden):
{
  "error": "Forbidden",
  "detail": "Cannot access other user's tasks",
  "type": "authorization_error"
}
```

### Step 5: Test Token Refresh

```bash
# Refresh token (before expiration)
curl -X POST http://localhost:3000/api/auth/refresh \
  -H "Authorization: Bearer ${TOKEN}"

# Expected response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # New token
  "expires_in": 3600
}
```

### Step 6: Test Logout

```bash
# Logout (clears HttpOnly cookie)
curl -X POST http://localhost:3000/api/auth/logout \
  -H "Authorization: Bearer ${TOKEN}"

# Expected response (200 OK):
{
  "message": "Logout successful"
}
```

---

## Troubleshooting

### Issue 1: "Invalid token signature"

**Symptom**: Backend rejects all JWT tokens with 401 error.

**Cause**: `BETTER_AUTH_SECRET` mismatch between frontend and backend.

**Solution**:
1. Verify secrets are identical in both `.env` files
2. Restart both services after changing environment variables
3. Re-login to get new token with correct signature

```bash
# Compare secrets (should be identical)
grep BETTER_AUTH_SECRET backend/.env
grep BETTER_AUTH_SECRET frontend/.env.local
```

### Issue 2: "Token has expired" immediately after login

**Symptom**: Token expires within seconds instead of 1 hour.

**Cause**: Clock skew between frontend and backend, or incorrect expiration configuration.

**Solution**:
1. Verify JWT_EXPIRATION_HOURS=1 in backend `.env`
2. Check system clocks are synchronized (NTP)
3. Increase leeway in PyJWT verification (already set to 10 seconds)

```bash
# Check system time
date  # Linux/Mac
Get-Date  # Windows PowerShell
```

### Issue 3: CORS errors when calling backend from frontend

**Symptom**: Browser console shows "CORS policy blocked" errors.

**Cause**: Backend CORS not configured for frontend origin.

**Solution**:
1. Add frontend URL to CORS_ORIGINS in backend `.env`
2. Ensure allow_credentials=True in CORS middleware
3. Restart backend after changes

```env
# backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Issue 4: "Cannot access other user's tasks" on own tasks

**Symptom**: User gets 403 Forbidden when accessing their own tasks.

**Cause**: Path user_id doesn't match JWT sub claim (possibly UUID format mismatch).

**Solution**:
1. Decode JWT token to verify sub claim format
2. Ensure user_id in path matches exactly (case-sensitive)
3. Check database user_id column type matches JWT sub claim

```bash
# Decode JWT token (header.payload.signature)
echo "eyJhbGci..." | cut -d. -f2 | base64 -d | jq .
# Should show: {"sub": "550e8400-...", "email": "user@example.com", ...}
```

### Issue 5: Token refresh fails with 401

**Symptom**: Auto-refresh hook fails to refresh token.

**Cause**: Attempting to refresh already-expired token.

**Solution**:
1. Reduce REFRESH_INTERVAL to 45 minutes (15 min buffer)
2. Handle 401 by redirecting to login instead of retrying
3. Implement exponential backoff for refresh attempts

```typescript
// Adjust refresh timing
const REFRESH_INTERVAL = 45 * 60 * 1000; // 45 minutes
```

### Issue 6: HttpOnly cookies not being set

**Symptom**: Token returned in response but not stored in browser cookies.

**Cause**: Secure flag requires HTTPS in production, or SameSite misconfiguration.

**Solution**:
1. In development, ensure secure: false in cookie options
2. In production, serve both frontend and backend over HTTPS
3. Verify SameSite="lax" allows cross-origin requests

```typescript
// Development cookie options
cookieOptions: {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",  // false in dev
  sameSite: "lax",
  path: "/",
}
```

---

## Next Steps

After successful setup and testing:

1. **Implement Frontend UI**: Create login/register pages using Better Auth React hooks
2. **Add User Profile**: Display user email and logout button
3. **Enhance Error Handling**: Show user-friendly error messages for auth failures
4. **Add Loading States**: Display spinners during authentication operations
5. **Implement Protected Routes**: Redirect unauthenticated users to login page
6. **Add Production Secrets**: Generate strong secrets for staging and production environments
7. **Configure HTTPS**: Set up SSL certificates for production deployment
8. **Monitor Performance**: Track JWT verification times (target: <5ms per request)

For detailed implementation tasks, see `specs/003-jwt-auth/tasks.md` (generated by `/sp.tasks` command).
