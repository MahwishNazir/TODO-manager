---
name: fastapi-backend-structure
description: Complete FastAPI backend project structure for Todo application Phase 2 with Neon database, JWT authentication using shared secret, and proper security validation.
---

# FastAPI Backend Structure for Todo Application Phase 2

## Instructions

Use this skill when creating the complete FastAPI backend project structure for the Todo application in Phase 2. This includes the proper directory structure, configuration, and integration of all components with security validation.

### 1. Project Structure
```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app instance with CORS configuration
│   ├── core/                   # Core configurations
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # SQLModel database configuration for Neon
│   │   └── security.py         # JWT validation with shared secret
│   ├── models/                 # SQLModel database models
│   │   ├── __init__.py
│   │   └── task.py             # Task model with Better Auth user_id
│   ├── schemas/                # Pydantic schemas for API requests/responses
│   │   ├── __init__.py
│   │   └── task.py             # TaskCreate, TaskUpdate, TaskResponse
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   └── task_service.py     # Task business logic with user validation
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── deps.py             # JWT authentication dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── tasks.py    # Task CRUD endpoints with user_id validation
├── alembic/
│   ├── __init__.py
│   ├── env.py                  # Alembic environment configuration
│   ├── script.py.mako          # Migration script template
│   └── versions/               # Generated migration files
│       └── (auto-generated files)
├── tests/                      # Test files
│   ├── __init__.py
│   └── test_tasks.py
├── alembic.ini               # Alembic configuration file
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # Project documentation
```

### 2. Dependencies (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.16
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.25.2
python-multipart==0.0.6
alembic==1.13.1
asyncpg==0.29.0  # For PostgreSQL
psycopg2-binary==2.9.9  # Alternative for PostgreSQL
```

### 3. Configuration Files
- `.env.example` with proper environment variables
- `alembic.ini` for database migrations with async support
- `alembic/env.py` for SQLModel/Neon-specific configuration
- `pyproject.toml` for project configuration if needed

### 4. Phase 2 Security Requirements Integration
- JWT validation using shared secret (BETTER_AUTH_SECRET)
- User_id validation in all endpoints
- Proper CORS configuration for Next.js frontend
- Database isolation by user_id

### 5. API Endpoint Implementation
- Follow RESTful design with user_id in URL
- Implement all 5 Basic Level features
- Proper HTTP status codes and error handling
- Input validation with Pydantic schemas

### 6. Database Integration
- SQLModel models with Neon-optimized configuration
- Proper indexing for performance
- User isolation with user_id foreign key
- Connection pooling for serverless

### 7. Testing Strategy
- Unit tests for API endpoints
- Integration tests for authentication
- Database tests with proper isolation
- Security tests for user_id validation

## Examples

### Example 1: Complete main.py with CORS
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
    version="1.0.0"
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

### Example 2: Configuration with Settings
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

### Example 3: Requirements.txt
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
sqlmodel==0.0.16
pydantic>=2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
httpx==0.26.0
python-multipart==0.0.6
alembic==1.13.1
asyncpg==0.29.0
psycopg2-binary==2.9.9
pytest==7.4.3
pytest-asyncio>=0.23.0
```

### Example 4: .env.example
```bash
# Database
DATABASE_URL=postgresql://neondb_owner:npg_TSQ8nfG4PtZC@ep-mute-moon-a4ueuef7-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&application_name=todo-app

# Authentication - MUST be the same as in Next.js
BETTER_AUTH_SECRET=your-super-secret-key-here-make-it-long-and-random

# Server
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Example 5: README.md
```markdown
# Todo API Backend - Phase 2

FastAPI backend for the Todo application with JWT authentication using Better Auth shared secret approach and Neon Serverless PostgreSQL.

## Features

- RESTful API endpoints for task management
- JWT authentication with shared secret between Next.js and FastAPI
- User isolation - each user can only access their own tasks
- Neon Serverless PostgreSQL integration
- Complete CRUD operations for tasks

## API Endpoints

- `GET /api/{user_id}/tasks` - List all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete a task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle task completion

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables (copy .env.example to .env)
3. Run the server: `uvicorn src.main:app --reload`

## Security

- All endpoints require JWT token in Authorization header
- User_id in URL is validated against JWT token
- Only user's own tasks are accessible
```

### Example 6: Alembic Configuration
```ini
# alembic.ini
[alembic]
# Path to migration scripts
script_location = alembic

# Template used to generate migration file names
# file_template = %%(rev)s_%%(slug)s

# sys.path path to the models for 'autogenerate' support
prepend_sys_path = .

# Max length of the prefix for version labels
# version_path_separator = os  # Use os.pathsep

# version_locations = %(here)s/bar:%(here)s/bat:alembic/versions

# The timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# For Linux/Unix systems, the default value is:
# timezone = %(dateutil.tz.tzlocal)s

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
level = NOTSET
```

### Example 7: Alembic Environment Configuration
```python
# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models and database configuration
from src.models.task import Task  # Add all your models here
from src.core.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
from sqlmodel import SQLModel
target_metadata = SQLModel.metadata

def configure_engine():
    """Configure the database URL for async usage"""
    config.set_main_option(
        "sqlalchemy.url",
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    )

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    configure_engine()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode."""
    configure_engine()
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Example 8: Alembic Usage Commands
```bash
# Initialize Alembic (run once)
alembic init -t async alembic

# Generate a new migration after model changes
alembic revision --autogenerate -m "Create task table"

# Apply migrations to database
alembic upgrade head

# Check current migration status
alembic current

# Run migrations before starting the application in production
alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Best Practices

- Follow the directory structure exactly as specified
- Use environment variables for all configuration
- Implement proper error handling and logging
- Follow security best practices for authentication
- Validate user_id in all endpoints to ensure data isolation
- Use proper database connection pooling for Neon Serverless
- Write comprehensive tests for all functionality
- Document the API endpoints properly
- Follow FastAPI best practices for dependency injection
- Use Pydantic for request/response validation
- Implement proper CORS configuration for frontend integration
- Use Alembic for database migrations in production
- Monitor performance and optimize queries for Neon