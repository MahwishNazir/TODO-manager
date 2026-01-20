# TODO Application - Phase II Step 1: REST API with Persistent Storage

**Phase**: II Step 1 - Web API Foundation (No Authentication)
**Version**: 2.0.0
**Status**: Development

## Description

A RESTful API for task management built with FastAPI and SQLModel, with persistent storage in Neon Serverless PostgreSQL. This is Phase II Step 1 (of 3) - converting the console app to a web-based API while keeping authentication simple.

### Features (Basic Tier via REST API)

- ✅ Create tasks via POST /api/{user_id}/tasks
- ✅ Retrieve all tasks via GET /api/{user_id}/tasks
- ✅ Retrieve single task via GET /api/{user_id}/tasks/{id}
- ✅ Update task titles via PUT /api/{user_id}/tasks/{id}
- ✅ Delete tasks via DELETE /api/{user_id}/tasks/{id}
- ✅ Toggle completion via PATCH /api/{user_id}/tasks/{id}/complete
- ✅ Database persistence (Neon PostgreSQL)
- ✅ User isolation by user_id (no authentication yet)
- ✅ Auto-generated OpenAPI documentation at /docs

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Neon account (free tier): https://neon.tech
- Git

## Quick Start

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Neon database URL
# DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

### 4. Setup Database

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Run migrations to create tables
alembic upgrade head
```

### 5. Start API Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation**: http://localhost:8000/docs (Swagger UI)

## API Usage

### Using Swagger UI (Browser)

1. Open http://localhost:8000/docs
2. Click on any endpoint to try it out
3. Enter parameters and request body
4. Click "Execute" to send request

### Using curl (Command Line)

#### Create Task

```bash
curl -X POST "http://localhost:8000/api/user123/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```

#### List All Tasks

```bash
curl "http://localhost:8000/api/user123/tasks"
```

#### Get Single Task

```bash
curl "http://localhost:8000/api/user123/tasks/1"
```

#### Update Task

```bash
curl -X PUT "http://localhost:8000/api/user123/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy organic groceries"}'
```

#### Mark Complete

```bash
curl -X PATCH "http://localhost:8000/api/user123/tasks/1/complete"
```

#### Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/user123/tasks/1"
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_task.py

# Run integration tests only
pytest tests/integration/
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Check types with mypy
mypy src/

# Lint code with pylint
pylint src/
```

### Code Quality Standards

- **Test Coverage**: ≥ 80%
- **Pylint Score**: ≥ 8.0/10
- **Mypy**: 0 errors
- **PEP 8**: Enforced via black formatter

## Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration and environment variables
│   ├── database.py              # SQLModel engine and session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py              # Task SQLModel with database fields
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py      # Task CRUD operations with user isolation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py      # FastAPI dependencies (get_db, etc.)
│   │   ├── middleware.py        # Logging, CORS, error handling
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py         # Task API endpoints (6 routes)
│   └── cli/                     # Phase I console app (preserved)
│       ├── __init__.py
│       └── menu.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures (TestClient, test DB)
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_task.py
│   │   ├── test_task_service.py
│   │   └── test_schemas.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_tasks.py
│   │   └── test_database.py
│   └── contract/
│       ├── __init__.py
│       └── test_openapi.py
│
├── alembic/                     # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env.example                 # Environment variable template
├── .env                         # Environment variables (not in git)
├── requirements.txt             # Production dependencies (FastAPI, SQLModel, etc.)
├── requirements-dev.txt         # Development dependencies (pytest, httpx, etc.)
├── pyproject.toml               # Project metadata
├── .pylintrc                    # Pylint configuration
├── mypy.ini                     # Mypy configuration
└── README.md                    # This file
```

## Architecture

### Clean Architecture Layers

- **Models** (`src/models/`): SQLModel entities (Task) and Pydantic schemas for API
- **Services** (`src/services/`): Business logic with user isolation enforcement
- **API Routes** (`src/api/routes/`): REST API endpoints (FastAPI)
- **Middleware** (`src/api/middleware.py`): Logging, CORS, error handling
- **Database** (`src/database.py`): SQLModel engine with connection pooling

### Data Storage

Phase II Step 1 uses persistent PostgreSQL storage (Neon Serverless):
- Tasks stored in `tasks` table with indexes on `user_id`
- Auto-incrementing integer primary key `id`
- Persistence across application restarts
- User isolation via `user_id` filtering (no authentication verification yet)
- Connection pooling: pool_size=5, max_overflow=10, pool_pre_ping=True

## Testing

### Test Strategy

1. **Unit Tests** (`tests/unit/`): Test models and services in isolation
2. **Integration Tests** (`tests/integration/`): Test complete user workflows
3. **Contract Tests**: Validate data structures for Phase II compatibility

### Running Specific Tests

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test function
pytest tests/unit/test_task.py::test_task_creation -v
```

## Troubleshooting

### Virtual Environment Not Activated

**Problem**: Commands installing globally instead of in venv

**Solution**:
```bash
# Check if venv is activated
which python  # Should show venv path

# If not activated:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Make sure you're in backend/ directory
cd backend

# Run with python -m to ensure PYTHONPATH is set
python -m pytest tests/
python -m src.main
```

### Type Checking Errors

**Problem**: mypy reports type errors

**Solution**:
```bash
# Run mypy incrementally during development
mypy src/

# Check specific file
mypy src/models/task.py
```

## Phase I Constraints

- **No external dependencies** (standard library only)
- **No data persistence** (in-memory only)
- **Console/CLI only** (no GUI)
- **Single user per session**
- **No network connectivity**

## Migration to Phase II

At the end of Phase I, data can be exported to JSON for migration to Phase II (web application with database):

```python
# JSON export feature (to be implemented)
task_manager.export_to_json("tasks_export.json")
```

## Contributing

### Code Style

- Follow PEP 8 (enforced by black)
- Use type hints for all public functions
- Write docstrings (Google style) for all modules/classes/functions
- Keep functions under 50 lines

### Testing

- Write tests BEFORE implementation (TDD)
- Achieve ≥80% code coverage
- All tests must pass before committing

### Git Workflow

- Work on feature branch (`001-phase1-console-app`)
- Commit frequently with descriptive messages
- Run quality checks before committing:
  ```bash
  black src/ tests/ && mypy src/ && pylint src/ && pytest
  ```

## License

Phase I - TODO Application Foundation

## Next Phases

- **Phase II**: Full-Stack Web Application (Next.js + FastAPI + Neon DB)
- **Phase III**: AI-Powered Todo Chatbot (OpenAI ChatKit + MCP)
- **Phase IV**: Local Kubernetes Deployment (Docker + Minikube + Helm)
- **Phase V**: Advanced Cloud Deployment (Kafka + Dapr + DigitalOcean DOKS)
