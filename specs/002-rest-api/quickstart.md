# Quick Start Guide: REST API with Persistent Storage

**Feature**: Phase II Step 1 - REST API
**Goal**: Get the FastAPI + SQLModel + Neon PostgreSQL API running locally in under 15 minutes

## Prerequisites

Before starting, ensure you have:

1. **Python 3.10+** installed
   ```bash
   python --version  # Should show 3.10 or higher
   ```

2. **Neon Account** (free tier)
   - Sign up at [https://neon.tech](https://neon.tech)
   - Create a new project named "todo-app"
   - Copy the connection string (starts with `postgresql://`)

3. **Git** (to clone repository)

4. **Code Editor** (VS Code, PyCharm, or similar)

## Setup Steps

### 1. Clone Repository and Navigate to Backend

```bash
cd C:\Users\User\Documents\Quarter-04\TODO_app\backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Verify**: Your terminal prompt should show `(venv)` prefix

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

**Expected packages**:
- FastAPI (web framework)
- SQLModel (ORM)
- Uvicorn (ASGI server)
- Psycopg2-binary (PostgreSQL driver)
- Alembic (database migrations)
- pytest, httpx (testing)

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Copy example file
cp .env.example .env

# Edit .env with your Neon connection string
```

**`.env` contents**:
```env
# Database
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# API Settings
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Development
DEBUG=True
```

**Important**: Replace `DATABASE_URL` with your Neon connection string from Step 1 (Prerequisites).

### 5. Run Database Migrations

```bash
# Initialize Alembic (first time only, if not already done)
alembic init alembic

# Run migrations to create tables
alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Add tasks table
INFO  [alembic.runtime.migration] Running upgrade 001 -> head
```

**Verify**: Check Neon dashboard - you should see a `tasks` table with columns: id, user_id, title, is_completed, created_at, updated_at

### 6. Start the API Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**API is now running!** 🎉

### 7. Access API Documentation

Open your browser and navigate to:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

You should see an interactive API documentation interface with all 6 endpoints.

## Testing the API

### Using Swagger UI (Browser)

1. Go to [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click on `POST /api/{user_id}/tasks`
3. Click "Try it out"
4. Enter `user123` for `user_id`
5. Enter request body:
   ```json
   {
     "title": "Buy groceries"
   }
   ```
6. Click "Execute"
7. Check the response (should be HTTP 201 with created task)

### Using curl (Command Line)

#### 1. Create a Task

```bash
curl -X POST "http://localhost:8000/api/user123/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```

**Expected response** (HTTP 201):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "is_completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

#### 2. List All Tasks

```bash
curl -X GET "http://localhost:8000/api/user123/tasks"
```

**Expected response** (HTTP 200):
```json
[
  {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "is_completed": false,
    "created_at": "2026-01-12T10:30:00Z",
    "updated_at": "2026-01-12T10:30:00Z"
  }
]
```

#### 3. Get Single Task

```bash
curl -X GET "http://localhost:8000/api/user123/tasks/1"
```

#### 4. Update Task

```bash
curl -X PUT "http://localhost:8000/api/user123/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy organic groceries"}'
```

#### 5. Mark Task Complete

```bash
curl -X PATCH "http://localhost:8000/api/user123/tasks/1/complete"
```

**Expected response** (HTTP 200, `is_completed` toggled to `true`):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy organic groceries",
  "is_completed": true,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T12:00:00Z"
}
```

#### 6. Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/user123/tasks/1"
```

**Expected response** (HTTP 204, no body)

### Using Postman

1. Import collection from `specs/002-rest-api/contracts/postman_collection.json` (if available)
2. Set base URL: `http://localhost:8000`
3. Run requests in order: Create → List → Get → Update → Complete → Delete

## Running Tests

### Run All Tests

```bash
# Run all tests with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected output**:
```
===== test session starts =====
collected 25 items

tests/unit/test_task.py ........          [ 32%]
tests/unit/test_task_service.py .......   [ 60%]
tests/integration/test_api_tasks.py ..... [ 80%]
tests/contract/test_openapi.py .....      [100%]

===== 25 passed in 2.34s =====

---------- coverage: 82% -----------
```

### Run Specific Test Files

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Single test file
pytest tests/integration/test_api_tasks.py

# Single test function
pytest tests/integration/test_api_tasks.py::test_create_task
```

### Run with Verbose Output

```bash
pytest -v tests/
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Activate virtual environment and install dependencies
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: "sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server"

**Solutions**:
1. Check DATABASE_URL in `.env` is correct
2. Verify internet connection (Neon is cloud-hosted)
3. Check Neon project is not paused (visit Neon dashboard)
4. Test connection string directly:
   ```bash
   psql "postgresql://user:password@host/dbname?sslmode=require"
   ```

### Issue: "alembic.util.exc.CommandError: Target database is not up to date"

**Solution**: Run pending migrations
```bash
alembic upgrade head
```

### Issue: "Port 8000 is already in use"

**Solutions**:
1. Stop existing uvicorn process (CTRL+C)
2. Use different port:
   ```bash
   uvicorn src.main:app --reload --port 8001
   ```
3. Find and kill process using port 8000 (Windows):
   ```bash
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

### Issue: "CORS error" when testing from frontend

**Solution**: Add frontend origin to CORS_ORIGINS in `.env`
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```

### Issue: Tests failing with "Table 'tasks' does not exist"

**Solution**: Tests use in-memory SQLite, which is created on the fly. Check `tests/conftest.py` to ensure `SQLModel.metadata.create_all(engine)` is called.

## Development Workflow

### Making Changes

1. **Modify Code**: Edit files in `backend/src/`
2. **Auto-Reload**: Uvicorn automatically reloads on file changes (thanks to `--reload` flag)
3. **Test Changes**: Visit `http://localhost:8000/docs` to test updated endpoints
4. **Run Tests**: `pytest tests/` to ensure no regressions

### Adding Database Migrations

When you modify models in `backend/src/models/task.py`:

```bash
# 1. Generate migration (auto-detects changes)
alembic revision --autogenerate -m "Description of change"

# 2. Review migration file in backend/alembic/versions/
# Check the generated SQL is correct

# 3. Apply migration
alembic upgrade head

# 4. Verify in Neon dashboard that changes were applied
```

### Code Quality Checks

```bash
# Format code (black)
black src/ tests/

# Lint code (pylint)
pylint src/

# Type check (mypy)
mypy src/

# All checks (recommended before commit)
black src/ tests/ && pylint src/ && mypy src/ && pytest tests/
```

## Next Steps

After successfully running the API:

1. **Explore Endpoints**: Test all 6 endpoints via Swagger UI
2. **User Isolation**: Create tasks for different user_ids (`user123`, `user456`) and verify isolation
3. **Read Spec**: Review `specs/002-rest-api/spec.md` for detailed requirements
4. **Run Tasks**: Proceed to implementation via `/sp.tasks` command
5. **Prepare for Step 2**: Understand authentication integration plan in `specs/002-rest-api/plan.md`

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | None | Neon PostgreSQL connection string |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated frontend URLs |
| `DEBUG` | No | `False` | Enable debug mode (detailed errors) |
| `HOST` | No | `0.0.0.0` | Server host (use `127.0.0.1` for local only) |
| `PORT` | No | `8000` | Server port |

## Useful Commands

```bash
# Start API server
uvicorn src.main:app --reload

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Check database connection
python -c "from src.database import engine; print('Connected!' if engine.connect() else 'Failed')"

# Export OpenAPI schema
curl http://localhost:8000/openapi.json > contracts/openapi.json

# Check Alembic migration history
alembic history

# Downgrade migration (rollback)
alembic downgrade -1
```

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
- **Neon Docs**: https://neon.tech/docs
- **Alembic Docs**: https://alembic.sqlalchemy.org
- **Project Spec**: `specs/002-rest-api/spec.md`
- **Implementation Plan**: `specs/002-rest-api/plan.md`

---

**Estimated Time to Complete**: 10-15 minutes (after prerequisites)

**Success Indicator**: Swagger UI accessible at http://localhost:8000/docs with all 6 endpoints visible and testable

🎉 **Congratulations!** You've successfully set up the Phase II Step 1 REST API. You're now ready to implement the full feature set following the task breakdown in `/sp.tasks`.
