# Quickstart Guide: Phase I - Python Console TODO Application

**Feature**: 001-phase1-console-app
**Date**: 2026-01-10
**Purpose**: Get developers up and running quickly with development environment and workflow

## Overview

This guide helps you set up your development environment and start implementing the Phase I Python console TODO application. Follow these steps in order for the smoothest experience.

## Prerequisites

**Required**:
- Python 3.10 or higher
- Git (for version control)
- Text editor or IDE (VS Code, PyCharm, or similar)

**Recommended**:
- Windows Terminal or modern terminal emulator
- VS Code with Python extension

**Verify Prerequisites**:

```bash
# Check Python version (must be 3.10+)
python --version  # or python3 --version

# Check Git
git --version

# Confirm we're on the correct branch
git branch --show-current  # Should show: 001-phase1-console-app
```

## Project Setup

### 1. Navigate to Project Root

```bash
cd TODO_app
```

### 2. Create Virtual Environment

Create an isolated Python environment for the project:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
which python  # Should point to venv/bin/python or venv\Scripts\python.exe
```

### 3. Install Development Dependencies

Create `backend/requirements-dev.txt`:

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pylint>=2.15.0
mypy>=1.0.0
black>=23.0.0
```

Install dependencies:

```bash
cd backend
pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
# Check pytest
pytest --version

# Check black
black --version

# Check pylint
pylint --version

# Check mypy
mypy --version
```

## Project Structure

**Before Implementation**:
```
TODO_app/
├── backend/                    # To be created
│   ├── src/                    # Source code (to be created)
│   ├── tests/                  # Test suite (to be created)
│   └── requirements-dev.txt    # Dev dependencies
├── specs/001-phase1-console-app/  # Specification artifacts
│   ├── spec.md                 # Feature specification
│   ├── plan.md                 # Implementation plan
│   ├── research.md             # Technical research
│   ├── data-model.md           # Entity definitions
│   ├── contracts/              # Interface contracts
│   └── quickstart.md           # This file
└── .specify/                   # Framework configuration
```

**After Implementation** (see `plan.md` for full structure):
```
backend/
├── src/
│   ├── models/
│   │   └── task.py
│   ├── services/
│   │   └── task_manager.py
│   ├── cli/
│   │   └── menu.py
│   └── main.py
└── tests/
    ├── unit/
    └── integration/
```

## Development Workflow

### Step 1: Read the Specifications

**Essential Reading** (in order):
1. `spec.md` - Understand requirements and success criteria
2. `plan.md` - Review architecture decisions and technical approach
3. `data-model.md` - Study entity definitions and relationships
4. `contracts/task_interface.py` - Review interface contracts

**Time Investment**: 30-45 minutes

**Why?**: Understanding the requirements prevents rework and ensures alignment with constitutional requirements.

### Step 2: Set Up Tool Configurations

Create tool configuration files in `backend/`:

**`pyproject.toml`** (project metadata):
```toml
[build-system]
requires = ["setuptools>=65.0"]
build-backend = "setuptools.build_meta"

[project]
name = "todo-app"
version = "1.0.0"
description = "Phase I Python Console TODO Application"
requires-python = ">=3.10"

[tool.black]
line-length = 88
target-version = ['py310']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--cov=src --cov-report=term-missing --cov-report=html"
```

**`.pylintrc`**:
```ini
[MASTER]
max-line-length = 88

[MESSAGES CONTROL]
disable = C0111  # docstrings checked manually

[DESIGN]
max-args = 5
max-locals = 15
max-attributes = 10
```

**`mypy.ini`**:
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
strict_optional = True
```

### Step 3: Create Directory Structure

```bash
cd backend

# Create source directories
mkdir -p src/models
mkdir -p src/services
mkdir -p src/cli

# Create test directories
mkdir -p tests/unit
mkdir -p tests/integration

# Create __init__.py files for packages
touch src/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/cli/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

# Create conftest.py for pytest fixtures
touch tests/conftest.py
```

### Step 4: Follow TDD Workflow

**IMPORTANT**: Follow the constitutional requirement for Test-First Development.

**TDD Cycle**:

1. **RED** - Write a failing test
2. **GREEN** - Write minimal code to pass
3. **REFACTOR** - Improve code while keeping tests green

**Example for Task Model**:

```python
# tests/unit/test_task.py
import pytest
from src.models.task import Task, ValidationError

def test_task_creation():
    """Test creating a task with valid data."""
    task = Task(id=1, title="Buy milk")
    assert task.id == 1
    assert task.title == "Buy milk"
    assert task.completed == False
    assert task.created_at is not None

def test_task_empty_title_raises_error():
    """Test that empty title raises ValidationError."""
    with pytest.raises(ValidationError):
        Task(id=1, title="")
```

Run test (should FAIL - RED):
```bash
pytest tests/unit/test_task.py -v
```

Implement minimal code to pass (GREEN):
```python
# src/models/task.py
from datetime import datetime

class ValidationError(Exception):
    pass

class Task:
    def __init__(self, id: int, title: str, completed: bool = False, created_at=None):
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")
        self.id = id
        self.title = title.strip()
        self.completed = completed
        self.created_at = created_at or datetime.utcnow()
```

Run test again (should PASS - GREEN):
```bash
pytest tests/unit/test_task.py -v
```

### Step 5: Implement in Recommended Order

See `plan.md` section "Implementation Sequence" for detailed order.

**Summary**:
1. Task model + tests
2. TaskManager service + tests
3. CLI menu + tests
4. Integration tests
5. Quality checks (coverage, linting, type checking)

### Step 6: Run Quality Checks Frequently

**During Development**:

```bash
# Format code with black
black src/ tests/

# Check types with mypy
mypy src/

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Check code quality
pylint src/
```

**Pre-Commit Checklist**:
```bash
# 1. Format code
black src/ tests/

# 2. Run all tests
pytest

# 3. Check coverage (must be ≥80%)
pytest --cov=src --cov-report=term-missing

# 4. Check types (must be 0 errors)
mypy src/

# 5. Check code quality (must be ≥8.0/10)
pylint src/
```

## Running the Application

**After Implementation**:

```bash
# From backend/ directory
python -m src.main

# Or make main.py executable and run directly
chmod +x src/main.py  # macOS/Linux only
python src/main.py
```

**Expected Output**:
```
TODO Application
================
1. View all tasks
2. Add new task
3. Update task
4. Mark task complete/incomplete
5. Delete task
6. Exit

Enter your choice (1-6):
```

## Testing

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_task.py

# Run specific test function
pytest tests/unit/test_task.py::test_task_creation
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open coverage report in browser
# Windows:
start htmlcov/index.html
# macOS:
open htmlcov/index.html
# Linux:
xdg-open htmlcov/index.html
```

### Run Integration Tests Only

```bash
pytest tests/integration/ -v
```

### Run Performance Tests

```bash
# Performance tests with timing
pytest tests/ -v --durations=10
```

## Common Issues and Solutions

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Make sure you're in backend/ directory
cd backend

# Run with python -m to ensure PYTHONPATH is set
python -m pytest tests/
```

### Issue: pytest Not Finding Tests

**Problem**: `collected 0 items`

**Solution**:
```bash
# Verify test discovery pattern
pytest --collect-only

# Ensure test files start with test_
# Ensure test functions start with test_
# Ensure __init__.py exists in test directories
```

### Issue: mypy Type Errors

**Problem**: `error: Function is missing a return type annotation`

**Solution**:
```python
# Add return type hints to all functions
def add_task(self, title: str) -> Task:  # ✅ Good
    ...

def add_task(self, title: str):  # ❌ Bad - missing return type
    ...
```

### Issue: Coverage Below 80%

**Problem**: Coverage report shows 75% coverage

**Solution**:
```bash
# Find untested code
pytest --cov=src --cov-report=term-missing

# Look for lines not covered (marked with >>>>)
# Add tests for uncovered lines
```

### Issue: Virtual Environment Not Activated

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

## Best Practices

### Code Style

✅ **DO**:
- Use type hints for all function signatures
- Write docstrings for all public functions (Google style)
- Keep functions under 50 lines
- Use descriptive variable names
- Follow PEP 8 (enforced by black)

❌ **DON'T**:
- Mix tabs and spaces
- Use single-letter variable names (except loop counters)
- Write functions longer than 50 lines
- Ignore linter warnings without justification

### Testing

✅ **DO**:
- Write tests before implementation (TDD)
- Test one thing per test function
- Use descriptive test names (test_should_do_something_when_condition)
- Use pytest fixtures for test data
- Test edge cases and error conditions

❌ **DON'T**:
- Write tests after implementation
- Test multiple things in one test
- Use cryptic test names (test1, test2)
- Duplicate test setup code
- Only test happy paths

### Git Workflow

✅ **DO**:
- Commit frequently with descriptive messages
- Keep commits atomic (one logical change)
- Run tests before committing
- Use feature branch (001-phase1-console-app)

❌ **DON'T**:
- Commit broken code
- Make huge commits with many changes
- Commit without testing
- Work directly on master branch

## Next Steps

1. **Read Specifications**: Review all docs in `specs/001-phase1-console-app/`
2. **Set Up Environment**: Create venv, install dependencies, configure tools
3. **Start with Tests**: Begin with `/sp.tasks` to get task breakdown
4. **Follow TDD**: Write test → See it fail → Make it pass → Refactor
5. **Check Quality**: Run coverage, linting, type checking frequently
6. **Verify Success**: Ensure all acceptance criteria from spec.md are met

## Resources

**Internal Documentation**:
- [spec.md](./spec.md) - Feature specification
- [plan.md](./plan.md) - Architecture and decisions
- [data-model.md](./data-model.md) - Entity definitions
- [research.md](./research.md) - Technical research
- [contracts/task_interface.py](./contracts/task_interface.py) - Interface definitions

**External Resources**:
- Python Official Documentation: https://docs.python.org/3.10/
- pytest Documentation: https://docs.pytest.org/
- PEP 8 Style Guide: https://pep8.org/
- Type Hints (PEP 484): https://www.python.org/dev/peps/pep-0484/
- mypy Documentation: http://mypy-lang.org/

## Support

**Questions or Issues?**
- Review the specification documents first
- Check `research.md` for technical decisions
- Consult `plan.md` for architecture guidance
- Refer to constitution at `.specify/memory/constitution.md` for project principles

**Ready to implement?**
Run `/sp.tasks` to generate the task breakdown and start coding!
