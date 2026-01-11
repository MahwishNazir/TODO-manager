---
name: fastapi-development
description: FastAPI development for Todo application Phase 2 with JWT authentication, SQLModel integration, and secure API endpoints. Includes dependency injection, error handling, and REST API patterns for Next.js integration.
---

# FastAPI Development for Todo Application Phase 2

## Instructions

Use this skill when implementing FastAPI components for the Todo application in Phase 2. Follow these guidelines for proper implementation with JWT authentication, SQLModel integration, and security validation.

### 1. FastAPI Application Structure
- Create main FastAPI app with proper configuration
- Implement CORS middleware for Next.js frontend integration
- Configure startup events for database initialization
- Set up global exception handlers
- Include automatic interactive documentation (Swagger UI and ReDoc)

### 2. Dependency Injection Patterns
- Use FastAPI Depends() for database sessions
- Implement JWT authentication dependencies
- Create reusable dependencies for current user validation
- Follow dependency injection best practices
- Chain dependencies for complex validation (get_current_user → get_current_active_user)

### 3. API Endpoint Development
- Follow RESTful API design principles
- Implement proper HTTP status codes
- Use Pydantic models for request/response validation
- Include comprehensive error handling
- Follow the Phase 2 endpoint specification: `/api/{user_id}/tasks`, `/api/{user_id}/tasks/{id}`

### 4. Phase 2 JWT Authentication Dependencies
- Create dependency to extract user_id from JWT token issued by Next.js
- Validate JWT using shared secret (BETTER_AUTH_SECRET) with HS256 algorithm
- Ensure user_id from JWT matches URL parameter in all endpoints
- Return appropriate 401/403 responses for auth failures
- Implement proper Authorization header validation

### 5. Database Session Management
- Use SQLModel sessions with proper lifecycle management
- Implement dependency for database session injection
- Handle transactions appropriately
- Close sessions to prevent connection leaks
- Use asyncpg for Neon Serverless PostgreSQL connections

### 6. Error Handling and Validation
- Use Pydantic for request/response validation
- Implement custom exception handlers
- Return proper HTTP status codes (401, 403, 404, etc.)
- Provide meaningful error messages without exposing sensitive information
- Handle database-specific exceptions gracefully

### 7. Phase 2 Security Requirements
- **CRITICAL**: Validate that user_id in URL matches JWT user_id in all endpoints
- Implement proper access controls
- Follow security best practices for JWT validation
- Handle authentication failures appropriately
- Prevent cross-user data access through user_id validation

### 8. Performance Considerations for Neon Serverless
- Use async functions for all endpoints to handle concurrent requests efficiently
- Implement proper database session management
- Optimize queries with proper indexing
- Use connection pooling appropriate for serverless (pool_size=5, pool_pre_ping=True)
- Use pagination for list endpoints (limit/offset)

### 9. Configuration Management
- Use pydantic-settings for configuration
- Store secrets in environment variables
- Configure CORS to allow Authorization header from frontend
- Set up proper logging for debugging and monitoring

## Examples

### Example 1: Main FastAPI Application with CORS
```python
# backend/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import tasks
from .core.config import settings
from .core.database import create_db_and_tables

app = FastAPI(
    title="Todo API - Phase 2",
    description="FastAPI backend for Todo application with JWT authentication from Next.js",
    version="1.0.0",
    # Enable automatic documentation
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS to allow requests from Next.js frontend
# CRITICAL: Allow Authorization header for JWT tokens from Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # IMPORTANT: Allow Authorization header for JWT from Next.js
    allow_headers=["Authorization", "Content-Type"],
)

# Include API routers
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

@app.on_event("startup")
def on_startup():
    """Create database tables on startup"""
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Todo API - Phase 2 Backend", "status": "ready"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "todo-api"}
```

### Example 2: JWT Authentication Dependencies
```python
# backend/src/api/deps.py
from fastapi import Depends, HTTPException, status, Request
from typing import Dict, Any
from jose import jwt, JWTError
import os
from ..core.security import verify_jwt

# Get the shared secret used for JWT validation
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

ALGORITHM = "HS256"

async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current user from JWT token issued by Better Auth in Next.js
    Uses shared secret for validation (HS256 algorithm)
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
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
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

### Example 3: JWT Validation Service
```python
# backend/src/core/security.py
from jose import jwt, JWTError
import os

# Get the shared secret used for JWT validation
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

ALGORITHM = "HS256"

def verify_jwt(token: str) -> dict:
    """
    Verify JWT token using shared secret from Next.js
    This validates tokens issued by Better Auth in Next.js using the shared secret
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Could not validate credentials")
    except Exception as e:
        raise ValueError(f"Token validation failed: {str(e)}")
```

### Example 4: Secure API Endpoints with User Validation
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

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    current_user_id: str = Depends(get_user_id_from_token),  # JWT user_id
    session: Session = Depends(get_session)
):
    """
    Get a specific task for the authenticated user
    CRITICAL: Validate that URL user_id matches JWT user_id
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    task = TaskService.get_task_by_id(
        session=session,
        task_id=task_id,
        user_id=user_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),  # JWT user_id
    session: Session = Depends(get_session)
):
    """
    Update a specific task for the authenticated user
    CRITICAL: Validate that URL user_id matches JWT user_id
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    task = TaskService.update_task(
        session=session,
        task_id=task_id,
        user_id=user_id,
        task_update=task_update
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    current_user_id: str = Depends(get_user_id_from_token),  # JWT user_id
    session: Session = Depends(get_session)
):
    """
    Delete a specific task for the authenticated user
    CRITICAL: Validate that URL user_id matches JWT user_id
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    success = TaskService.delete_task(
        session=session,
        task_id=task_id,
        user_id=user_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task deleted successfully"}

@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user_id: str = Depends(get_user_id_from_token),  # JWT user_id
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task
    CRITICAL: Validate that URL user_id matches JWT user_id
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    task = TaskService.toggle_task_completion(
        session=session,
        task_id=task_id,
        user_id=user_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task
```

### Example 5: Database Session Dependency
```python
# backend/src/core/database.py
from sqlmodel import Session, create_engine
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with Neon-specific configuration for serverless
engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # Optimal for serverless workloads
    max_overflow=10,    # Allow some overflow during traffic spikes
    pool_pre_ping=True, # Verify connections before use (critical for serverless)
    pool_recycle=300,   # Recycle connections every 5 minutes to handle timeouts
    echo=False,         # Set to True for debugging only
    connect_args={
        "sslmode": "require",           # Required for Neon
        "application_name": "todo-app", # Help with monitoring
        "connect_timeout": 10,          # Connection timeout
        "options": "-c statement_timeout=30000"  # 30 second statement timeout
    }
)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Use this for all database operations in endpoints
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    Create database tables on startup
    Call this in the startup event
    """
    from ..models.task import Task  # Import here to avoid circular imports
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
```

### Example 6: Configuration with Settings
```python
# backend/src/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str

    # Auth settings - shared secret with Next.js
    BETTER_AUTH_SECRET: str

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]  # Next.js frontend

    # JWT settings
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 7 * 24 * 60 * 60  # 7 days

    # Neon-specific settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 300  # 5 minutes

    class Config:
        env_file = ".env"

settings = Settings()
```

### Example 7: Error Handling
```python
# backend/src/api/exceptions.py
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.requests import Request

async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors consistently"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions consistently"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# In main.py, register these handlers:
# app.add_exception_handler(RequestValidationError, validation_exception_handler)
# app.add_exception_handler(HTTPException, http_exception_handler)
```

## Best Practices

- **CRITICAL**: Always validate that user_id in URL matches the user_id from JWT token in all endpoints
- Use async functions for all API endpoints to handle concurrent requests efficiently
- Implement proper error responses with appropriate HTTP status codes
- Use dependency injection for database sessions and JWT authentication
- Follow RESTful API design principles with proper HTTP methods
- Implement proper logging for debugging and monitoring
- Use environment variables for configuration including JWT settings
- Validate all input data using Pydantic models
- Handle database transactions properly
- Use Neon's serverless features like automatic scaling
- Implement proper session management for database connections
- Use proper error handling for database-specific exceptions
- Implement proper resource cleanup to avoid connection leaks in serverless environment
- Use exclude_unset=True when updating to only update provided fields
- Validate input data before performing operations
- Use appropriate HTTP status codes for different error conditions
- Include meaningful error messages for debugging
- Use datetime.utcnow() for consistent timestamp generation
- Handle edge cases like non-existent records appropriately
- Implement proper transaction management for multi-step operations
- Use select() with appropriate filters to ensure data isolation
- Validate user permissions before allowing operations
- Implement proper session management with rollback mechanisms
- Use connection timeouts appropriate for serverless functions (30s statement timeout recommended)
- Include structured logging to track database operations and performance
- Use Neon's built-in monitoring and performance insights to optimize queries
- Follow Phase 2 security requirements with proper user_id validation
- Use proper field lengths to prevent oversized data in Neon
- Optimize queries using proper indexing and relationship loading strategies for Neon
- Create indexes on frequently queried fields (user_id, created_at, completed status)
- Use Neon-optimized query patterns with proper indexing
- Follow SQLModel best practices for model relationships with proper indexing
- Use parameterized queries to prevent SQL injection (SQLModel handles this automatically)
- Monitor query performance and optimize slow queries with Neon's query insights
- Use consistent application_name for monitoring across services
- Test database operations with concurrent access patterns
- Implement proper default values for timestamps in Neon
- Consider indexing completed field for status filtering in Neon
- Use datetime.utcnow for consistent timestamp generation across Neon instances
- Handle database connection timeouts gracefully with proper error responses in Neon
- Monitor connection pool usage and adjust settings as needed for traffic patterns
- Include proper error logging for connection issues
- Use proper authentication and authorization for all endpoints
- Validate content types and request formats
- Implement proper CORS configuration for frontend integration
- Use proper error responses for authentication and authorization failures
- Follow security best practices for JWT validation
- Implement proper input sanitization and validation
- Use consistent error response formats
- Include detailed logging for security events
- Implement proper session validation for user isolation
- Use appropriate pagination for list endpoints