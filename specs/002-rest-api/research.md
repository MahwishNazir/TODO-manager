# Research & Technical Decisions: REST API with Persistent Storage

**Feature**: Phase II Step 1 - REST API with Persistent Storage
**Date**: 2026-01-12
**Branch**: 002-rest-api
**Status**: Completed

## Overview

This document consolidates all technical research and decisions for implementing a FastAPI-based REST API with SQLModel ORM and Neon PostgreSQL database. All "NEEDS CLARIFICATION" items from the plan's Technical Context have been resolved through research of official documentation, best practices, and real-world implementations.

## Research Tasks & Resolutions

### 1. FastAPI Project Structure Best Practices

**Decision**: Use layered architecture with clear separation between API routes, business logic (services), and data access (models)

**Rationale**:
- Recommended by FastAPI creator (Sebastián Ramírez) in official full-stack template
- Aligns with Clean Architecture principles
- Facilitates testing (can test services without HTTP layer)
- Scales well as API grows

**Structure**:
```
backend/src/
├── main.py              # FastAPI app initialization, middleware, CORS
├── config.py            # Settings (Pydantic BaseSettings)
├── database.py          # SQLModel engine and session factory
├── models/              # Data layer
│   ├── task.py          # SQLModel table models
│   └── schemas.py       # Pydantic request/response schemas
├── services/            # Business logic layer
│   └── task_service.py  # CRUD operations, business rules
└── api/                 # Presentation layer
    ├── dependencies.py  # FastAPI dependencies (get_db, etc.)
    ├── middleware.py    # Logging, error handling
    └── routes/
        └── tasks.py     # HTTP route handlers
```

**References**:
- [FastAPI Full-Stack Template](https://github.com/tiangolo/full-stack-fastapi-postgresql)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

### 2. SQLModel Connection Pooling with Neon

**Decision**: Use connection pooling with the following configuration:
- `pool_size=5` (default connections)
- `max_overflow=10` (additional connections under load)
- `pool_pre_ping=True` (verify connection health before use)
- `pool_recycle=3600` (recycle connections every hour)

**Rationale**:
- **pool_pre_ping**: Essential for serverless databases like Neon that may close idle connections
- **pool_size=5**: Adequate for Step 1 API with expected low concurrent traffic
- **max_overflow=10**: Allows burst capacity up to 15 total connections (well under 20-connection target)
- **pool_recycle=3600**: Prevents stale connections; Neon recommends recycling within 1-2 hours

**Implementation**:
```python
from sqlmodel import create_engine, Session
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL query logging in development
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,   # Recycle connections every hour
    connect_args={
        "connect_timeout": 10,
        "application_name": "todo-api"
    }
)
```

**Neon-Specific Considerations**:
- Neon auto-scales and pauses inactive databases (cold start ~1s)
- `pool_pre_ping` ensures first request after pause doesn't fail
- Connection string format: `postgresql://user:pass@host/db?sslmode=require`
- SSL required for Neon connections

**References**:
- [Neon PostgreSQL Connection](https://neon.tech/docs/connect/connect-from-any-app)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)

---

### 3. FastAPI Dependency Injection for Database Sessions

**Decision**: Use FastAPI's dependency injection with `yield` pattern for automatic session management

**Rationale**:
- Ensures session is closed after request (no connection leaks)
- Supports automatic rollback on exceptions
- Testable (can override dependency in tests)
- FastAPI best practice recommended in official docs

**Implementation**:
```python
# backend/src/api/dependencies.py
from typing import Generator
from sqlmodel import Session
from backend.src.database import engine

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields:
        Session: SQLModel database session

    Note:
        Session is automatically closed when request completes.
        Rollback occurs automatically on exceptions.
    """
    with Session(engine) as session:
        yield session
```

**Usage in Routes**:
```python
# backend/src/api/routes/tasks.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend.src.api.dependencies import get_db

router = APIRouter()

@router.get("/api/{user_id}/tasks")
def list_tasks(
    user_id: str,
    db: Session = Depends(get_db)
):
    # Session automatically injected
    # Automatically closed when handler returns
    return task_service.get_all_tasks(db, user_id)
```

**Testing Override**:
```python
# tests/conftest.py
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from backend.src.api.dependencies import get_db

# Test database engine
test_engine = create_engine("sqlite:///:memory:")

def override_get_db():
    with Session(test_engine) as session:
        yield session

# Override dependency in tests
app.dependency_overrides[get_db] = override_get_db
```

**References**:
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLModel with FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/)

---

### 4. API Error Handling and Exception Mapping

**Decision**: Use FastAPI exception handlers to map exceptions to HTTP status codes with consistent JSON error responses

**Rationale**:
- Centralized error handling (DRY principle)
- Consistent error response format across all endpoints
- Separates error handling from business logic
- FastAPI provides built-in exception handler mechanism

**Error Response Schema**:
```python
# backend/src/models/schemas.py
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    error_type: str = "unknown_error"
```

**Exception Handlers**:
```python
# backend/src/main.py or middleware.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handle database errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error_type": "database_error"
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(
    request: Request,
    exc: ValueError
) -> JSONResponse:
    """Handle validation errors from service layer."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "error_type": "validation_error"
        }
    )
```

**Service Layer Pattern**:
```python
# backend/src/services/task_service.py
from fastapi import HTTPException, status

def get_task_by_id(db: Session, user_id: str, task_id: int):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != user_id:
        # Don't reveal task exists for other users
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task
```

**Status Code Mapping**:
- `400 Bad Request`: Malformed request (FastAPI handles automatically)
- `404 Not Found`: Resource doesn't exist or belongs to different user
- `422 Unprocessable Entity`: Validation error (Pydantic handles automatically)
- `500 Internal Server Error`: Database errors, unexpected exceptions

**References**:
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [HTTPException](https://fastapi.tiangolo.com/tutorial/handling-errors/#use-httpexception)

---

### 5. Testing Strategy for FastAPI + SQLModel

**Decision**: Multi-layered testing approach with SQLite in-memory database for speed

**Rationale**:
- **In-memory SQLite**: Fast test execution (no network I/O)
- **TestClient**: Tests full HTTP stack without running server
- **Fixtures**: Reusable test setup (database, client, test data)
- **Pytest**: Constitutional requirement; excellent FastAPI support

**Test Layers**:

1. **Unit Tests** (models, schemas, services):
```python
# tests/unit/test_task_service.py
import pytest
from sqlmodel import Session, create_engine, SQLModel
from backend.src.models.task import Task
from backend.src.services.task_service import create_task

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_task(db_session):
    task = create_task(db_session, "user123", "Buy milk")
    assert task.title == "Buy milk"
    assert task.user_id == "user123"
    assert task.is_completed is False
```

2. **Integration Tests** (API endpoints):
```python
# tests/integration/test_api_tasks.py
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_task_api(client):
    response = client.post(
        "/api/user123/tasks",
        json={"title": "Buy milk"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert "id" in data
```

3. **Contract Tests** (OpenAPI validation):
```python
# tests/contract/test_openapi.py
def test_openapi_schema_valid(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"] == "3.1.0"
    assert "/api/{user_id}/tasks" in schema["paths"]
```

**Pytest Configuration**:
```python
# tests/conftest.py
import pytest
from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.api.dependencies import get_db

# In-memory SQLite for tests
SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """Provide clean database session for each test."""
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Provide TestClient with test database."""
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**Coverage Target**: ≥80% per constitution

**References**:
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)

---

### 6. OpenAPI Schema Export and Validation

**Decision**: Export OpenAPI schema from FastAPI's auto-generated `/openapi.json` endpoint to version-controlled YAML file

**Rationale**:
- FastAPI auto-generates accurate OpenAPI 3.1 schema from route definitions
- Version-controlled schema enables contract testing and frontend code generation
- YAML format more readable for code review than JSON

**Export Process**:
```bash
# After running API locally
curl http://localhost:8000/openapi.json | \
  python -m json.tool | \
  yq eval -P - > specs/002-rest-api/contracts/openapi.yaml
```

**Or programmatically**:
```python
# scripts/export_openapi.py
import yaml
from backend.src.main import app

with open("specs/002-rest-api/contracts/openapi.yaml", "w") as f:
    yaml.dump(app.openapi(), f, sort_keys=False)
```

**Schema Validation in Tests**:
```python
# tests/contract/test_openapi.py
import yaml
from pathlib import Path

def test_openapi_matches_spec(client):
    # Get current schema from API
    response = client.get("/openapi.json")
    current_schema = response.json()

    # Load version-controlled schema
    spec_path = Path("specs/002-rest-api/contracts/openapi.yaml")
    with open(spec_path) as f:
        spec_schema = yaml.safe_load(f)

    # Compare critical fields (paths, schemas)
    assert current_schema["paths"] == spec_schema["paths"]
    assert current_schema["components"] == spec_schema["components"]
```

**FastAPI OpenAPI Customization**:
```python
# backend/src/main.py
app = FastAPI(
    title="TODO API",
    description="Task management REST API with user isolation",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc alternative
    openapi_url="/openapi.json"
)
```

**References**:
- [FastAPI OpenAPI](https://fastapi.tiangolo.com/tutorial/metadata/)
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)

---

### 7. Database Migration Workflow with Alembic

**Decision**: Use Alembic with auto-generate capability, manual review, and version control

**Rationale**:
- Alembic is SQLAlchemy's official migration tool (SQLModel uses SQLAlchemy)
- Auto-generate detects schema changes from models
- Manual review prevents accidental destructive migrations
- Version-controlled migrations enable team collaboration and rollback

**Setup Process**:
```bash
# Initialize Alembic
cd backend
alembic init alembic

# Configure Alembic to use SQLModel
# Edit alembic/env.py to import SQLModel metadata
```

**Alembic Configuration**:
```python
# backend/alembic/env.py
from sqlmodel import SQLModel
from backend.src.models.task import Task  # Import all models

target_metadata = SQLModel.metadata

# Use async engine if using asyncpg
from backend.src.database import engine

def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()
```

**Migration Workflow**:

1. **Create Migration** (after model changes):
```bash
alembic revision --autogenerate -m "Add tasks table"
```

2. **Review Migration** (manual check of generated SQL):
```python
# alembic/versions/001_add_tasks_table.py
def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(50), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('is_completed', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now())
    )
    op.create_index('idx_user_id', 'tasks', ['user_id'])

def downgrade():
    op.drop_table('tasks')
```

3. **Apply Migration**:
```bash
# Upgrade to latest version
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Check current version
alembic current
```

4. **Version Control**: Commit migration files to git

**Best Practices**:
- Never edit applied migrations (create new migration instead)
- Always review auto-generated migrations before applying
- Test migrations on staging database before production
- Keep migrations small and focused (one logical change per migration)

**References**:
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLModel with Alembic](https://sqlmodel.tiangolo.com/tutorial/fastapi/app-testing/#alembic-migrations)

---

### 8. CORS Configuration for Future Frontend

**Decision**: Configure CORS middleware with environment-based allowed origins

**Rationale**:
- Next.js frontend (Step 3) will run on different port/domain than API
- Development: Allow localhost origins
- Production: Restrict to specific frontend domain
- Security: Credentials support disabled (using JWT instead)

**Implementation**:
```python
# backend/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration from environment
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Frontend URLs
    allow_credentials=False,     # Will use True with JWT in Step 2
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Length"],
    max_age=3600  # Cache preflight requests for 1 hour
)
```

**Environment Configuration**:
```bash
# .env (development)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# .env (production)
CORS_ORIGINS=https://todo.example.com
```

**Testing CORS**:
```python
def test_cors_headers(client):
    response = client.options(
        "/api/user123/tasks",
        headers={"Origin": "http://localhost:3000"}
    )
    assert response.status_code == 200
    assert "http://localhost:3000" in response.headers["access-control-allow-origin"]
```

**Future (Step 2 with Authentication)**:
- Set `allow_credentials=True` for JWT cookies
- Add `Authorization` header to allowed headers
- Consider wildcard origins for development only

**References**:
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

## Technology Stack Confirmed

Based on research, the following versions and tools are confirmed for implementation:

### Core Dependencies
- **Python**: 3.10+
- **FastAPI**: 0.104+ (latest stable)
- **SQLModel**: 0.0.14+ (latest stable)
- **Uvicorn**: 0.24+ (ASGI server)
- **Pydantic**: 2.5+ (included with FastAPI)
- **SQLAlchemy**: 2.0+ (SQLModel dependency)

### Database
- **Neon PostgreSQL**: Serverless, free tier available
- **Psycopg2-binary**: 2.9+ (PostgreSQL driver, simpler) OR
- **Asyncpg**: 0.29+ (async driver, better performance)
- **Alembic**: 1.13+ (migrations)

### Testing
- **pytest**: 7.4+
- **pytest-asyncio**: 0.21+ (if using async endpoints)
- **pytest-cov**: 4.1+ (coverage reporting)
- **httpx**: 0.25+ (TestClient dependency)

### Development Tools
- **black**: 23.12+ (code formatting)
- **pylint**: 3.0+ (linting)
- **mypy**: 1.7+ (type checking)
- **python-dotenv**: 1.0+ (environment variables)

## Implementation Recommendations

### 1. Start Simple, Add Complexity Later
- Begin with synchronous database operations (simpler)
- Add async/await if performance testing shows need
- Use Psycopg2 first; switch to Asyncpg if needed

### 2. Leverage FastAPI Features
- Auto-generated OpenAPI docs reduce manual documentation
- Pydantic models provide automatic validation
- Dependency injection simplifies testing

### 3. Follow 12-Factor App Principles
- All configuration via environment variables
- No secrets in code or version control
- Stateless API (session state in database, not memory)

### 4. Maintain Phase I Console App
- Keep `src/cli/` directory functional
- Useful for testing business logic without HTTP
- Potential data migration tool

### 5. Plan for Step 2 (Authentication)
- Database schema already includes `user_id` column
- CORS configured for credentials
- Service layer enforces user isolation

## Open Questions (for Future Steps)

### Step 2 (Authentication):
- Which Better Auth flow (email/password, OAuth, magic link)?
- JWT storage (localStorage vs httpOnly cookies)?
- Token refresh strategy?

### Step 3 (Frontend):
- Next.js 14 or 15?
- App Router or Pages Router?
- State management (Context, Zustand, Redux)?

**Note**: These questions are out of scope for Step 1 and will be addressed in their respective specification/planning phases.

---

**Research Status**: ✅ Complete
**All Technical Unknowns Resolved**: Yes
**Ready for Phase 1 (Data Model & Contracts)**: Yes
