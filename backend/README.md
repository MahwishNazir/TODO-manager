# TODO Application - Phase I: Python Console

**Phase**: I - Foundation (In-Memory Python Console)
**Version**: 1.0.0
**Status**: Development

## Description

A command-line TODO application built with Python that stores tasks in memory. This is Phase I of a 5-phase evolution from console app to cloud-deployed full-stack application.

### Features (Basic Tier)

- ✅ Add tasks with titles
- ✅ View all tasks with IDs and completion status
- ✅ Mark tasks as complete/incomplete
- ✅ Update task titles
- ✅ Delete tasks
- ✅ Session-based persistence (data clears on exit)

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Setup

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
# Install development dependencies
pip install -r requirements-dev.txt
```

## Usage

### Running the Application

```bash
# From backend/ directory
python -m src.main

# Or directly
python src/main.py
```

### Menu Options

```
TODO Application
================
1. View all tasks
2. Add new task
3. Update task
4. Mark task complete/incomplete
5. Delete task
6. Exit
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
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py           # Task entity with validation
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_manager.py   # TaskManager business logic
│   ├── cli/
│   │   ├── __init__.py
│   │   └── menu.py           # CLI menu interface
│   └── main.py               # Application entry point
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_task.py
│   │   └── test_task_manager.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_cli_flow.py
│   └── conftest.py           # pytest fixtures
│
├── requirements.txt          # Production dependencies (empty for Phase I)
├── requirements-dev.txt      # Development dependencies
├── pyproject.toml           # Project metadata and tool configs
├── .pylintrc                # Pylint configuration
├── mypy.ini                 # Mypy configuration
└── README.md                # This file
```

## Architecture

### Clean Architecture Layers

- **Models** (`src/models/`): Data entities (Task) with validation logic
- **Services** (`src/services/`): Business logic (TaskManager with CRUD operations)
- **CLI** (`src/cli/`): Presentation layer (menu-driven interface)

### Data Storage

Phase I uses in-memory storage via Python dictionaries:
- Tasks stored in `Dict[int, Task]` for O(1) lookup by ID
- Auto-incrementing integer IDs
- No persistence across sessions (data clears on exit)

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
