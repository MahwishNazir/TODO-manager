# Implementation Plan: Phase I - Python Console TODO Application

**Branch**: `001-phase1-console-app` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase1-console-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a command-line TODO application in Python that stores tasks in memory and provides 5 basic operations: Add, Delete, Update, View, and Mark Complete. This is Phase I (Foundation) of a 5-phase project, focusing on proving core business logic, establishing testing patterns, and validating UX flows. The application will use clean Python architecture with proper separation of concerns, type hints, comprehensive testing (≥80% coverage), and adherence to PEP 8 standards.

**Technical Approach**: Implement a menu-driven CLI using Python's standard library with in-memory storage (dictionaries/lists). Follow clean architecture principles with separate layers for data models (Task), business logic (TaskManager), and presentation (CLI interface). Use pytest for comprehensive unit testing and type checking with mypy to ensure code quality.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**:
- **Production**: None (standard library only per constitution C-001)
- **Development**: pytest (testing), pylint (linting), mypy (type checking), black (formatting - optional)

**Storage**: In-memory using Python data structures (dict for task storage, list for ordering)
**Testing**: pytest with ≥80% code coverage requirement
**Target Platform**: Cross-platform (Windows, Linux, macOS) - Python 3.10+ runtime
**Project Type**: Single project (console application)
**Performance Goals**:
- All operations complete in <100ms for up to 1000 tasks
- User interactions (add/view/update/delete) complete in <3 seconds end-to-end

**Constraints**:
- No external dependencies except testing tools (C-001)
- No data persistence across sessions (C-002)
- Console/CLI only - no GUI (C-003)
- Single user per session (C-004)
- No network/API calls (C-005)
- Python 3.10+ required (C-006)

**Scale/Scope**:
- Support up to 1000 tasks in a single session
- 5 basic operations (CRUD + mark complete)
- Single module codebase (~500-800 LOC estimated)
- 16 acceptance scenarios to implement

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Phased Development Approach (MANDATORY)
- **Status**: PASS
- **Verification**: This is Phase I (Foundation) - In-Memory Python Console App
- **Compliance**:
  - Implements only Basic tier features (per constitution principle V)
  - No features from Phase II+ included
  - Data export capability planned for Phase I → II migration
  - All intermediate and advanced features deferred

### ✅ II. Spec-Driven Development (NON-NEGOTIABLE)
- **Status**: PASS
- **Verification**:
  - Spec created and validated (specs/001-phase1-console-app/spec.md)
  - Plan being created now (this document)
  - Tasks will be created via /sp.tasks after plan approval
  - Implementation follows after tasks approved
- **Compliance**: Following SDD workflow (spec → plan → tasks → implementation)

### ✅ III. Test-First Development (NON-NEGOTIABLE)
- **Status**: PASS
- **Verification**:
  - Test coverage target: ≥80% (per NFR-005)
  - TDD cycle will be enforced during implementation
  - pytest framework specified
  - All 16 acceptance scenarios will have corresponding tests
- **Compliance**: Tests will be written before implementation for each task

### ✅ IV. Separation of Concerns
- **Status**: PASS (with Phase I exception)
- **Verification**:
  - Phase I is console-only (no frontend/backend split needed)
  - Code will separate: Models (Task) / Business Logic (TaskManager) / Presentation (CLI)
  - Phase II will introduce proper frontend/backend separation
- **Compliance**: Clean architecture within single codebase for Phase I

### ✅ V. Feature Tiering and Progressive Enhancement
- **Status**: PASS
- **Verification**: Implementing Basic tier only
  - ✅ Add Task
  - ✅ Delete Task
  - ✅ Update Task
  - ✅ View Task List
  - ✅ Mark as Complete/Incomplete
- **Compliance**: Intermediate and Advanced tiers explicitly deferred to later iterations

### ✅ VI. Technology Stack Discipline
- **Status**: PASS
- **Verification**: Using Phase I designated stack
  - Language: Python 3.10+ ✅
  - Storage: In-memory (dict/list) ✅
  - Interface: Console/CLI ✅
  - Tools: Claude Code, Spec-Kit Plus ✅
  - Testing: pytest ✅
- **Compliance**: No deviations from constitutional stack requirements

### ✅ VII. Data Integrity and Migration
- **Status**: PASS
- **Verification**:
  - In-memory storage for Phase I (per requirements)
  - JSON export planned for Phase I → II migration
  - Migration script will be created at end of Phase I
- **Compliance**: Migration path documented in spec (section "Migration Path")

### Additional Constitutional Requirements

#### Code Quality Standards (Technology Stack Standards)
- **PEP 8 Compliance**: Code must pass black formatter
- **Type Hints**: Required for all public functions (NFR-002)
- **Docstrings**: Google style for all modules/classes/functions (NFR-003)
- **Linting**: pylint score ≥8.0/10 (SC-005)
- **Type Checking**: mypy with zero errors (SC-005)

#### Testing Standards (Test-First Development)
- **Unit Tests**: All business logic covered
- **Coverage**: Minimum 80% (NFR-005)
- **Test Framework**: pytest
- **Test Organization**: Separate test directory structure

#### Performance Standards
- **Response Time**: Operations <100ms (NFR-006)
- **Scalability**: Support 1000 tasks without degradation (NFR-008)

**GATE RESULT**: ✅ **ALL GATES PASSED** - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/001-phase1-console-app/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   └── task_interface.py  # Python interface definitions
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
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
│   │   ├── test_task.py      # Task model tests
│   │   └── test_task_manager.py  # TaskManager tests
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_cli_flow.py  # End-to-end CLI tests
│   └── conftest.py           # pytest fixtures
│
├── requirements.txt          # Production dependencies (empty for Phase I)
├── requirements-dev.txt      # Development dependencies (pytest, etc.)
├── pyproject.toml           # Project metadata and tool configs
├── setup.py                 # Package installation
├── .pylintrc                # Pylint configuration
├── mypy.ini                 # Mypy configuration
└── README.md                # Project documentation
```

**Structure Decision**: Single project structure selected for Phase I console application. Using `/backend` directory to prepare for Phase II transition to full-stack architecture. Clean separation of concerns:
- **models/**: Data entities (Task) with validation logic
- **services/**: Business logic layer (TaskManager with CRUD operations)
- **cli/**: Presentation layer (menu-driven interface)
- **tests/**: Comprehensive test suite organized by test type

This structure allows easy extraction of models/services into shared library for Phase II while keeping Phase I simple and focused.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. All gates passed without requiring justification.

## Architecture Decisions

### AD-001: In-Memory Storage Implementation

**Context**: Phase I requires task storage without persistence across sessions.

**Decision**: Use Python dictionary for task storage with integer keys (task IDs).

**Rationale**:
- O(1) lookup by task ID (required for update/delete/mark operations)
- Simple and performant for up to 1000 tasks
- Easy to export to JSON for Phase I → II migration
- No external dependencies required

**Alternatives Considered**:
- List-based storage: Rejected - O(n) lookup performance
- SQLite: Rejected - violates C-002 (no persistence) and C-001 (no external deps)
- File-based: Rejected - violates C-002 (no cross-session persistence)

**Consequences**:
- ✅ Fast operations (<100ms guaranteed)
- ✅ Simple implementation
- ✅ Easy testing
- ⚠️ Data lost on exit (documented limitation, acceptable for Phase I)

### AD-002: CLI Menu System

**Context**: Need user-friendly console interface for 5 operations.

**Decision**: Implement numbered menu with input validation loop.

**Rationale**:
- Intuitive for users (numbered choices)
- Easy to extend for future features
- Built-in error handling via input validation
- Standard CLI pattern

**Menu Structure**:
```
TODO Application
1. View all tasks
2. Add new task
3. Update task
4. Mark task complete/incomplete
5. Delete task
6. Exit
```

**Alternatives Considered**:
- Command-line arguments: Rejected - poor UX for interactive operations
- REPL with commands: Rejected - unnecessarily complex for 5 operations
- curses/rich TUI: Rejected - external dependency, over-engineered

**Consequences**:
- ✅ Simple user experience
- ✅ No learning curve
- ✅ Easy testing via input mocking
- ⚠️ Sequential operation only (acceptable for Phase I)

### AD-003: Task ID Generation

**Context**: Need unique, stable identifiers for tasks.

**Decision**: Auto-incrementing integer IDs starting from 1.

**Rationale**:
- Simple for users to reference (e.g., "delete task 3")
- Guaranteed uniqueness within session
- Easy to implement with counter
- Compatible with future database auto-increment in Phase II

**Implementation**: TaskManager maintains `_next_id` counter, incremented on each add.

**Alternatives Considered**:
- UUID: Rejected - too complex for CLI input
- Hash-based: Rejected - non-sequential, harder for users
- Title-based: Rejected - not unique, changes on update

**Consequences**:
- ✅ User-friendly
- ✅ Simple implementation
- ✅ Database-compatible for Phase II
- ⚠️ IDs not reused after deletion (acceptable - maintains stability)

### AD-004: Error Handling Strategy

**Context**: Need clear, actionable error messages per FR-010.

**Decision**: Exception-based error handling with custom exception types.

**Exception Hierarchy**:
```python
TodoError (base)
├── TaskNotFoundError
├── InvalidTaskDataError
└── ValidationError
```

**Rationale**:
- Pythonic approach
- Clear error categorization
- Easy to test
- Informative messages for users

**Alternatives Considered**:
- Return codes: Rejected - not Pythonic, error-prone
- Result type: Rejected - over-engineered for simple app
- Silent failures: Rejected - violates FR-010

**Consequences**:
- ✅ Clear error messages
- ✅ Easy debugging
- ✅ Testable error paths
- ✅ Type-safe with type hints

### AD-005: Testing Strategy

**Context**: Must achieve ≥80% coverage with meaningful tests.

**Decision**: Three-layer testing approach:

1. **Unit Tests** (models, services):
   - Test Task validation logic
   - Test TaskManager CRUD operations
   - Mock dependencies

2. **Integration Tests** (CLI flows):
   - Test complete user workflows
   - Mock user input
   - Verify end-to-end behavior

3. **Contract Tests** (Phase II preparation):
   - Validate Task data structure
   - Ensure serialization compatibility

**Rationale**:
- Comprehensive coverage
- Fast feedback (unit tests)
- Confidence in UX (integration tests)
- Future-proof (contract tests for Phase II)

**Tools**:
- pytest: Test framework
- pytest-cov: Coverage reporting
- pytest-mock: Mocking utilities

**Alternatives Considered**:
- Manual testing only: Rejected - not sustainable, violates NFR-005
- Only integration tests: Rejected - slow, hard to debug
- Only unit tests: Rejected - misses UX issues

**Consequences**:
- ✅ High confidence in code quality
- ✅ Fast test execution (<5s total)
- ✅ Easy regression detection
- ⚠️ Requires discipline to maintain (mitigated by TDD)

## Data Model

See [data-model.md](./data-model.md) for detailed entity definitions.

**Summary**:
- **Task**: Core entity with id, title, completed, created_at
- **TaskManager**: Service managing task collection and operations

## API Contracts

See [contracts/](./contracts/) for detailed interface definitions.

**Summary**:
- Task interface (data structure)
- TaskManager interface (CRUD operations)

## Implementation Sequence

**Phase 0 Complete**: Research phase concluded (see research.md)
**Phase 1 Complete**: Design artifacts generated
**Next**: Proceed to `/sp.tasks` for task breakdown

### Recommended Task Order (for future /sp.tasks)

1. **Foundation** (Task 1-3):
   - Set up project structure and tooling
   - Implement Task model with validation
   - Implement TaskManager core logic

2. **CLI Interface** (Task 4-5):
   - Build menu system
   - Integrate with TaskManager

3. **Testing** (Task 6-7):
   - Write comprehensive unit tests
   - Write integration tests

4. **Quality** (Task 8-9):
   - Achieve 80% coverage
   - Pass all linting/type checks

5. **Documentation** (Task 10):
   - Write README and usage guide

## Non-Functional Requirements Plan

### Performance (NFR-006, NFR-008)
- **Target**: <100ms per operation for 1000 tasks
- **Implementation**: Use dict for O(1) lookups
- **Verification**: Performance tests in test suite
- **Monitoring**: Time assertions in integration tests

### Code Quality (NFR-001, NFR-002, NFR-003, NFR-007)
- **PEP 8**: Enforced via black formatter
- **Type Hints**: Required for all public functions
- **Docstrings**: Google style for all modules/classes/functions
- **Linting**: pylint ≥8.0/10
- **Type Checking**: mypy with zero errors
- **Verification**: CI checks (to be set up) or manual pre-commit

### Testing (NFR-005)
- **Coverage Target**: ≥80%
- **Framework**: pytest
- **Execution**: `pytest --cov=src --cov-report=term-missing`
- **Quality**: All tests must pass before considering feature complete

### Structure (NFR-004)
- **Package Layout**: Proper Python package with `__init__.py`
- **Separation**: Models / Services / CLI clearly delineated
- **Discoverability**: Logical module naming and organization

## Risk Analysis

### Risk 1: Test Coverage Not Meeting 80% Threshold
- **Probability**: Low
- **Impact**: High (blocks Phase I completion per SC-006)
- **Mitigation**:
  - Start with TDD from first task
  - Monitor coverage throughout development
  - Focus on business logic (models, services) for highest value coverage
- **Contingency**: Add tests for edge cases if falling short

### Risk 2: Performance Degradation with Large Task Lists
- **Probability**: Low
- **Impact**: Medium (violates NFR-008)
- **Mitigation**:
  - Use efficient data structures (dict for O(1) access)
  - Performance test with 1000+ tasks
  - Profile if issues arise
- **Contingency**: Optimize algorithms, consider indexing strategies

### Risk 3: Type Checking Errors with mypy
- **Probability**: Medium
- **Impact**: Medium (blocks quality gates)
- **Mitigation**:
  - Use type hints from start
  - Run mypy incrementally during development
  - Reference mypy docs for complex typing scenarios
- **Contingency**: Use `# type: ignore` sparingly with justification

## Success Criteria Mapping

| Success Criterion | Verification Method | Target |
|-------------------|---------------------|--------|
| SC-001: Add task in <3s | Manual testing + integration test | <3s end-to-end |
| SC-002: All 5 operations work | Integration tests covering all ops | 100% pass |
| SC-003: 1000 tasks <100ms | Performance test with timer | <100ms p95 |
| SC-004: Input validation <1s | Unit tests + integration tests | <1s response |
| SC-005: Code quality | pylint + mypy automated checks | ≥8.0/10, 0 errors |
| SC-006: Test coverage | pytest-cov report | ≥80% |
| SC-007: Menu navigation | Manual usability testing | No doc required |
| SC-008: 10 operations no errors | Integration test sequence | 100% success |

## Dependencies and Prerequisites

### Runtime Dependencies
- Python 3.10 or higher (required)

### Development Dependencies
- pytest ≥7.0 (testing framework)
- pytest-cov (coverage reporting)
- pylint ≥2.0 (code linting)
- mypy ≥1.0 (type checking)
- black (code formatting - optional but recommended)

### External Dependencies
- None (per constitutional constraint C-001)

## Migration Considerations (Phase I → Phase II)

### Data Export Functionality
At the end of Phase I implementation, add JSON export feature:
```python
def export_to_json(filename: str) -> None:
    """Export all tasks to JSON file for Phase II migration."""
```

### Expected JSON Format
```json
{
  "version": "1.0",
  "exported_at": "2026-01-10T12:00:00Z",
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "completed": false,
      "created_at": "2026-01-10T11:00:00Z"
    }
  ]
}
```

### Phase II Integration Points
- JSON export → Phase II migration script
- Task model → Shared SQLModel schema
- Business logic → FastAPI endpoints

## Appendix: Constitutional Alignment

This plan fully complies with all constitutional requirements:

- ✅ **Phase I Technology Stack**: Python 3.10+, in-memory, pytest
- ✅ **Basic Tier Features Only**: 5 core operations, no intermediate/advanced
- ✅ **Clean Code Principles**: PEP 8, type hints, docstrings, <50 LOC functions
- ✅ **TDD Workflow**: Tests before implementation, ≥80% coverage
- ✅ **No Premature Optimization**: Simple dict-based storage, YAGNI principle
- ✅ **Proper Structure**: Clear separation of models/services/cli
- ✅ **Migration Planning**: JSON export for Phase II transition

**Next Step**: Generate Phase 0 research.md and Phase 1 artifacts (data-model.md, contracts/, quickstart.md)
