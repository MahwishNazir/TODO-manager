# Research: Phase I - Python Console TODO Application

**Feature**: 001-phase1-console-app
**Date**: 2026-01-10
**Purpose**: Document technical decisions, best practices, and patterns for Phase I implementation

## Overview

This document captures research findings and technical decisions for implementing a console-based TODO application in Python. All technical context was clear from the specification, so this research focuses on best practices, patterns, and implementation strategies.

## Research Areas

### 1. Python Project Structure Best Practices

**Research Question**: What is the recommended project structure for a Python CLI application that will evolve into a web application?

**Decision**: Use `/backend` directory structure with clear separation of concerns

**Rationale**:
- Prepares for Phase II transition to full-stack (frontend + backend)
- Follows industry standard for web applications
- Allows models/services to be easily shared between CLI and API
- Clear separation: models → services → presentation

**Best Practices Applied**:

```
backend/
├── src/              # Source code
│   ├── models/       # Data entities
│   ├── services/     # Business logic
│   ├── cli/          # Presentation layer
│   └── main.py       # Entry point
├── tests/            # Test suite
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
└── [config files]    # Tool configurations
```

**Sources**:
- Python Packaging Authority (PyPA) recommendations
- Real Python project structure guide
- "The Hitchhiker's Guide to Python" best practices

**Alternatives Considered**:
- Flat structure: Rejected - doesn't scale, hard to maintain
- `src/` at root: Rejected - conflicts with Phase II frontend directory
- No separation: Rejected - violates clean architecture principles

### 2. In-Memory Storage Patterns

**Research Question**: What's the most efficient pattern for in-memory task storage in Python?

**Decision**: Dictionary with integer keys (task IDs)

**Pattern**:
```python
class TaskManager:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1
```

**Performance Characteristics**:
- **Lookup**: O(1) - direct access by ID
- **Insert**: O(1) - dict assignment
- **Delete**: O(1) - dict.pop()
- **Update**: O(1) - modify in place
- **List all**: O(n) - iterate dict.values()

**Rationale**:
- Meets performance requirement (<100ms for 1000 tasks)
- Simple and Pythonic
- Type-safe with type hints
- Easy to test and mock

**Alternatives Considered**:
- List of tasks: O(n) lookup - too slow for requirements
- Database (SQLite): Violates no-persistence constraint
- OrderedDict: Unnecessary - we don't need insertion order

**Memory Estimate**:
- Task object: ~200 bytes (id, title, bool, timestamp)
- 1000 tasks: ~200KB - well within limits

### 3. CLI Menu Design Patterns

**Research Question**: What's the best pattern for a menu-driven CLI in Python?

**Decision**: Numbered menu with input loop and command dispatch

**Pattern**:
```python
def main_loop():
    while True:
        display_menu()
        choice = get_user_choice()
        dispatch_command(choice)
        if choice == 'exit':
            break
```

**Menu Structure**:
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

**Rationale**:
- Intuitive - users recognize numbered menus
- Extensible - easy to add new options
- Error handling - validate choice before dispatch
- Standard pattern - predictable for users

**Best Practices**:
- Clear menu headers and separators
- Validate input before processing
- Provide feedback after each action
- Confirm destructive operations (delete)
- Handle Ctrl+C gracefully

**Sources**:
- Python Click library patterns (inspiration, not using lib)
- "Python CLI Design" best practices
- UX patterns from GNU coreutils

**Alternatives Considered**:
- Command-line args (like git): Rejected - poor UX for interactive app
- REPL with text commands: Rejected - more complex, less intuitive
- TUI with ncurses: Rejected - external dependency, overengineered

### 4. Exception Handling Strategy

**Research Question**: How should we handle errors in a CLI application?

**Decision**: Custom exception hierarchy with user-friendly messages

**Exception Hierarchy**:
```python
class TodoError(Exception):
    """Base exception for TODO application"""
    pass

class TaskNotFoundError(TodoError):
    """Raised when task ID doesn't exist"""
    pass

class InvalidTaskDataError(TodoError):
    """Raised when task data fails validation"""
    pass

class ValidationError(TodoError):
    """Raised when user input is invalid"""
    pass
```

**Error Handling Pattern**:
```python
try:
    task_manager.delete_task(task_id)
    print(f"✓ Task {task_id} deleted successfully")
except TaskNotFoundError:
    print(f"✗ Error: Task {task_id} not found")
except TodoError as e:
    print(f"✗ Error: {str(e)}")
```

**Rationale**:
- Pythonic - exceptions are idiomatic in Python
- Type-safe - can catch specific errors
- Testable - can assert exceptions raised
- Clear - each exception type has specific meaning

**Best Practices**:
- Never swallow exceptions silently
- Provide actionable error messages
- Log exceptions for debugging
- Differentiate between user errors and bugs

**Sources**:
- PEP 8 exception conventions
- "Clean Code" error handling chapter
- Python official documentation

**Alternatives Considered**:
- Return codes: Rejected - not Pythonic, error-prone
- Result types: Rejected - unnecessary complexity
- No custom exceptions: Rejected - hard to distinguish error types

### 5. Type Hints and Validation

**Research Question**: How to implement comprehensive type safety and validation?

**Decision**: Full type hints + runtime validation for user input

**Type Hints Pattern**:
```python
from typing import Dict, Optional
from datetime import datetime

class Task:
    def __init__(
        self,
        id: int,
        title: str,
        completed: bool = False,
        created_at: Optional[datetime] = None
    ) -> None:
        self.id = id
        self.title = title
        self.completed = completed
        self.created_at = created_at or datetime.now()
```

**Validation Pattern**:
```python
def validate_title(title: str) -> str:
    """Validate task title"""
    if not title or not title.strip():
        raise ValidationError("Task title cannot be empty")
    if len(title) > 500:
        raise ValidationError("Task title too long (max 500 characters)")
    return title.strip()
```

**Rationale**:
- Type hints improve IDE support and catch errors
- mypy provides static type checking
- Runtime validation ensures data integrity
- Clear separation: types (compile-time) vs validation (runtime)

**Best Practices**:
- Type hint all public functions
- Use Optional for nullable values
- Validate at boundaries (user input, external data)
- Don't validate internal operations (trust your code)

**Tools**:
- mypy: Static type checker
- Type annotations: Built-in since Python 3.5
- dataclasses: Consider for future (Phase II)

**Sources**:
- PEP 484 (Type Hints)
- mypy documentation
- "Effective Python" type hints chapter

**Alternatives Considered**:
- No type hints: Rejected - violates NFR-002, loses IDE support
- Pydantic validation: Rejected - external dependency
- Full dataclass usage: Deferred - simple classes sufficient for Phase I

### 6. Testing Strategy and Fixtures

**Research Question**: What's the optimal testing approach for a CLI application?

**Decision**: Three-layer testing with pytest

**Testing Layers**:

1. **Unit Tests** (fast, isolated):
```python
def test_task_creation():
    task = Task(id=1, title="Test task")
    assert task.id == 1
    assert task.title == "Test task"
    assert task.completed == False
```

2. **Integration Tests** (realistic, mocked I/O):
```python
def test_add_task_flow(monkeypatch, capsys):
    inputs = iter(["2", "Buy milk", "6"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    main()
    captured = capsys.readouterr()
    assert "Task added successfully" in captured.out
```

3. **Contract Tests** (data structure validation):
```python
def test_task_serialization():
    task = Task(id=1, title="Test")
    data = task.to_dict()
    assert data == {"id": 1, "title": "Test", "completed": False}
```

**pytest Fixtures**:
```python
@pytest.fixture
def task_manager():
    """Provide clean TaskManager for each test"""
    return TaskManager()

@pytest.fixture
def sample_tasks():
    """Provide sample task data"""
    return [
        Task(id=1, title="Task 1"),
        Task(id=2, title="Task 2"),
    ]
```

**Coverage Strategy**:
- Focus on business logic (models, services): 90%+ coverage
- CLI layer: Test critical paths, 70%+ coverage
- Overall target: ≥80% as required

**Rationale**:
- Fast feedback loop (unit tests run in <1s)
- Confidence in UX (integration tests)
- Future-proof (contract tests for Phase II)

**Best Practices**:
- One assertion per test (when possible)
- Descriptive test names
- Arrange-Act-Assert pattern
- Use fixtures for test data
- Mock external dependencies (I/O)

**Sources**:
- pytest documentation
- "Test Driven Development with Python"
- pytest best practices guide

**Tools**:
- pytest: Test framework
- pytest-cov: Coverage reporting
- pytest-mock: Mocking utilities (built on unittest.mock)

**Alternatives Considered**:
- unittest: Rejected - pytest is more Pythonic and powerful
- Manual testing: Rejected - not sustainable, violates NFR-005
- Hypothesis (property testing): Deferred - nice to have, not required

### 7. Code Quality Tooling

**Research Question**: What tools ensure code quality standards are met?

**Decision**: Multi-tool approach (black, pylint, mypy)

**Tool Configuration**:

**black** (code formatting):
```toml
[tool.black]
line-length = 88
target-version = ['py310']
```

**pylint** (.pylintrc):
```ini
[MASTER]
max-line-length = 88
disable = C0111  # Missing docstrings handled separately

[DESIGN]
max-args = 5
max-locals = 15
```

**mypy** (mypy.ini):
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

**Enforcement Workflow**:
1. Black auto-formats code (pre-commit)
2. Pylint checks code quality (≥8.0/10 required)
3. Mypy checks type safety (zero errors required)
4. pytest runs tests (100% pass required)

**Rationale**:
- Black: Eliminates formatting debates, ensures PEP 8
- Pylint: Catches code smells, enforces best practices
- Mypy: Ensures type safety, catches type errors
- Layered approach: Each tool has specific purpose

**Best Practices**:
- Run black first (fixes formatting)
- Fix mypy errors before implementing
- Address pylint warnings iteratively
- Don't disable checks without justification

**Sources**:
- Black project documentation
- Pylint best practices
- Mypy usage guide
- PEP 8 style guide

**Alternatives Considered**:
- flake8: Rejected - pylint is more comprehensive
- autopep8: Rejected - black is more opinionated and consistent
- No formatters: Rejected - leads to style debates

### 8. Performance Optimization Strategies

**Research Question**: How to ensure <100ms operations for 1000 tasks?

**Decision**: Efficient data structures + lazy evaluation

**Optimization Strategies**:

1. **Use dict for O(1) lookups**:
   - Direct access by ID avoids iteration
   - Insert/update/delete are instant

2. **Lazy list generation**:
```python
def get_all_tasks(self) -> List[Task]:
    """Return tasks only when needed"""
    return list(self._tasks.values())  # Create list on demand
```

3. **Avoid premature optimization**:
   - No caching (YAGNI for 1000 tasks)
   - No indexing (dict is already indexed)
   - No threading (single-user, sequential)

4. **Performance testing**:
```python
def test_performance_1000_tasks():
    manager = TaskManager()
    # Add 1000 tasks
    start = time.time()
    for i in range(1000):
        manager.add_task(f"Task {i}")
    duration = time.time() - start
    assert duration < 0.1  # <100ms
```

**Rationale**:
- Dict provides O(1) for all required operations
- Python is fast enough for 1000 items
- Simplicity > premature optimization
- Performance tests catch regressions

**Performance Estimates**:
- Add task: <0.01ms (dict insert + object creation)
- Get task: <0.01ms (dict lookup)
- List 1000 tasks: ~1ms (iterate dict)
- Well under 100ms requirement

**Sources**:
- Python TimeComplexity wiki
- "High Performance Python" book
- Python profiling documentation

**Alternatives Considered**:
- Caching: Rejected - unnecessary for in-memory data
- Async/await: Rejected - no I/O to async
- Multiprocessing: Rejected - single-user app

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Project Structure | /backend with models/services/cli | Phase II preparation, clean separation |
| Storage | Dictionary with integer keys | O(1) operations, simple, performant |
| CLI Pattern | Numbered menu with input loop | Intuitive, extensible, standard |
| Error Handling | Custom exception hierarchy | Pythonic, type-safe, testable |
| Type Safety | Full type hints + runtime validation | IDE support, mypy checking, data integrity |
| Testing | Three-layer (unit/integration/contract) | Fast feedback, UX confidence, future-proof |
| Code Quality | black + pylint + mypy | Automated enforcement, multi-faceted quality |
| Performance | Efficient data structures, no premature optimization | Meets requirements, keeps code simple |

## Implementation Readiness

All research questions resolved. No NEEDS CLARIFICATION markers remain.

**Status**: ✅ **Ready for Phase 1 Design**

**Next Steps**:
1. Generate data-model.md (detailed entity definitions)
2. Generate contracts/ (Python interface definitions)
3. Generate quickstart.md (developer onboarding guide)
4. Proceed to /sp.tasks for task breakdown

## References

- **PEP 8**: Style Guide for Python Code
- **PEP 484**: Type Hints
- **Python Packaging Authority (PyPA)**: Project structure guidelines
- **pytest documentation**: Testing best practices
- **Real Python**: Python project structure guide
- **"Clean Code" by Robert C. Martin**: Error handling patterns
- **"Test Driven Development with Python"**: Testing strategies
- **mypy documentation**: Type checking guide
- **Python official documentation**: Language reference and stdlib
