---
name: better-auth
description: Better Auth integration using shared secret for JWT tokens between Next.js frontend and FastAPI backend for Phase 2 Todo application. Simpler approach using HS256 algorithm with shared BETTER_AUTH_SECRET.
---

# Better Auth Shared Secret JWT for Todo Application Phase 2

## Instructions

Use this skill when implementing authentication for the Todo application Phase 2 using Better Auth with a shared secret approach. This follows the Phase 2 specification where Better Auth and FastAPI use the same secret key for JWT signing and verification.

### 1. Shared Secret Architecture
- Both frontend (Better Auth) and backend (FastAPI) use the **same secret key** for JWT signing and verification
- Use environment variable **BETTER_AUTH_SECRET** in both services
- Simpler than JWKS approach - both services can verify tokens independently
- Uses HS256 algorithm for symmetric signing

### 2. Token Flow Pattern (Phase 2 Specific)
1. User signs in with Better Auth in Next.js
2. Better Auth creates a session and issues a JWT token with shared secret
3. Frontend includes JWT token in Authorization: Bearer <token> header for API calls
4. FastAPI extracts token from header, verifies signature using shared secret
5. FastAPI decodes token to get user ID and matches it with user ID in URL
6. FastAPI filters data to return only tasks belonging to that user

### 3. Better Auth Configuration for Shared Secret
- Configure Better Auth with JWT plugin using shared secret
- Set up proper session management
- Configure token expiration (typically 7 days)
- Ensure token includes user ID for backend verification

### 4. Next.js Integration
- Install Better Auth in Next.js application
- Configure auth with shared secret (BETTER_AUTH_SECRET)
- Set up proper auth routes
- Implement API client that attaches JWT to requests

### 5. FastAPI JWT Validation with Shared Secret
- Validate JWT using the shared secret key
- Extract user_id from JWT claims (typically in 'sub' field)
- Verify that user_id from JWT matches URL parameter
- Implement dependency for current user validation

### 6. Phase 2 Security Requirements
- **CRITICAL**: Validate that user_id in URL matches authenticated user from JWT in all endpoints
- All endpoints require valid JWT token
- Requests without token receive 401 Unauthorized
- Each user only sees/modifies their own tasks
- Task ownership is enforced on every operation

### 7. Security Best Practices
- Use HTTPS in production
- Store BETTER_AUTH_SECRET securely in environment variables
- Implement proper error handling without exposing sensitive information
- Apply proper CORS configuration
- Use secure token transmission

## Examples

### Example 1: Better Auth Configuration with Shared Secret (Next.js)
```typescript
// lib/auth.ts
import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { nextCookies } from 'better-auth/next-js';
import { db } from '@/lib/db';
import { user, session, account } from '@/db/schema';

export const auth = betterAuth({
  // Database adapter using Drizzle ORM for Neon PostgreSQL
  database: drizzleAdapter(db, {
    provider: 'pg',
    schema: {
      user,
      session,
      account, // Contains password field for email/password auth
    },
  }),

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Phase 2: No email verification
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },

  // Secret for signing tokens
  secret: process.env.BETTER_AUTH_SECRET!,

  // Base URL for auth routes
  baseURL: process.env.BETTER_AUTH_URL!,

  // Next.js integration plugin
  plugins: [nextCookies()],

  // Advanced options
  advanced: {
    // Use secure cookies in production
    useSecureCookies: process.env.NODE_ENV === 'production',
    cookiePrefix: 'better-auth',
    defaultCookieAttributes: {
      sameSite: 'lax',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      path: '/',
    },
  },

  // Trust proxy headers (for deployment behind reverse proxies)
  trustedOrigins: process.env.NEXT_PUBLIC_APP_URL
    ? [process.env.NEXT_PUBLIC_APP_URL]
    : [],
});
```

### Example 2: Next.js Auth Route Handler
```typescript
// app/api/auth/[...auth]/route.ts
import { auth } from '@/lib/auth';
export const { GET, POST } = auth.handler();
```

### Example 3: Frontend API Client with JWT
```typescript
// lib/api.ts
class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  // Get JWT token from Better Auth session
  private async getAuthToken(): Promise<string | null> {
    try {
      // Better Auth stores session with nested structure
      const { getSession } = await import('@/lib/auth-client');
      const sessionData = await getSession();

      // Type-safe extraction of token from nested session data
      if (sessionData && typeof sessionData === 'object' && 'data' in sessionData) {
        const data = sessionData.data;
        if (data && typeof data === 'object' && 'session' in data) {
          const session = data.session as { token?: string } | null;
          return session?.token || null;
        }
      }

      return null;
    } catch (error) {
      console.error('Failed to get session token:', error);
      return null;
    }
  }

  // Make authenticated API request
  async request(endpoint: string, options: RequestInit = {}) {
    const token = await this.getAuthToken();

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Redirect to login if unauthorized
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // API methods for task operations
  async getTasks(userId: string) {
    return this.request(`/api/${userId}/tasks`);
  }

  async createTask(userId: string, taskData: any) {
    return this.request(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(userId: string, taskId: number, taskData: any) {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(userId: string, taskId: number) {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(userId: string, taskId: number) {
    return this.request(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }
}

export const api = new ApiClient();
```

### Example 4: FastAPI JWT Validation with Shared Secret
```python
# backend/src/security/jwt_validator.py
from typing import Dict, Any
from fastapi import HTTPException, status
from jose import jwt, JWTError
import os

# Use the same BETTER_AUTH_SECRET for validation
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")
ALGORITHM = "HS256"

def verify_jwt(token: str) -> Dict[str, Any]:
    """
    Verify JWT token using shared secret
    This function validates tokens issued by Better Auth using the shared secret
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )
```

### Example 5: FastAPI JWT Dependency
```python
# backend/src/api/deps.py
from fastapi import Depends, HTTPException, status, Request
from typing import Dict, Any
from ..security.jwt_validator import verify_jwt

async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current user from JWT token issued by Better Auth
    Uses shared secret for validation
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = auth_header.split(" ", 1)[1]
    try:
        user_data = verify_jwt(token)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

def get_user_id_from_token(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Extract user_id from current user JWT claims
    CRITICAL: This user_id must match the user_id in the URL for all endpoints
    """
    user_id = current_user.get("sub")  # User ID is typically in 'sub' field
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: no user_id found"
        )
    return user_id
```

### Example 6: Secure API Endpoint with User Validation
```python
# backend/src/api/v1/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlmodel import Session
from ...models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from ...services.task_service import TaskService
from ..deps import get_user_id_from_token
from ...core.database import get_session

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    current_user_id: str = Depends(get_user_id_from_token),  # JWT user_id
    completed: bool = Query(None, description="Filter by completion status"),
    limit: int = Query(50, ge=1, le=100, description="Number of tasks to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    session: Session = Depends(get_session)
):
    """
    List all tasks for the authenticated user
    CRITICAL: Validate that URL user_id matches JWT user_id
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    tasks = TaskService.get_tasks_by_user(
        session=session,
        user_id=user_id,
        completed=completed,
        limit=limit,
        offset=offset
    )

    return tasks

@router.post("/{user_id}/tasks", response_model=TaskResponse)
async def create_task(
    user_id: str,
    task_create: TaskCreate,
    current_user_id: str = Depends(get_user_id_from_token),  # JWT user_id
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user
    CRITICAL: Validate that URL user_id matches JWT user_id
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )

    task = TaskService.create_task(
        session=session,
        user_id=user_id,
        task_create=task_create
    )

    return task
```

### Example 7: Environment Variables Setup
```bash
# Next.js (.env.local)
BETTER_AUTH_SECRET=your-super-secret-key-here-make-it-long-and-random
NEXT_PUBLIC_API_URL=http://localhost:8000

# FastAPI (.env)
BETTER_AUTH_SECRET=your-super-secret-key-here-make-it-long-and-random
```

## Best Practices for Phase 2

- Use the same BETTER_AUTH_SECRET in both Next.js and FastAPI
- Implement proper error handling for JWT validation failures
- Always validate that user_id in URL matches JWT user_id in all endpoints
- Use HTTPS in production for secure token transmission
- Store BETTER_AUTH_SECRET securely in environment variables
- Implement proper session management
- Test authentication flows thoroughly
- Follow security best practices for token storage and transmission
- Validate all inputs to prevent injection attacks
- Log authentication events for audit trails