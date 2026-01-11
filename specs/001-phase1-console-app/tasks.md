# Tasks: Phase I - Python Console TODO Application

**Input**: Design documents from `/specs/001-phase1-console-app/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Following TDD approach - tests are written FIRST, must FAIL, then implementation makes them pass.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

This project uses **web app structure** with `/backend` directory:
- Source code: `backend/src/`
- Tests: `backend/tests/`
- Config files: `backend/` root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

### Project Structure

- [x] T001 Create backend directory structure (src/, tests/, config files) per plan.md
- [x] T002 [P] Create all `__init__.py` files for Python packages (src/, src/models/, src/services/, src/cli/, tests/, tests/unit/, tests/integration/)
- [x] T003 [P] Create `backend/requirements.txt` (empty - no production dependencies for Phase I)
- [x] T004 [P] Create `backend/requirements-dev.txt` with pytest>=7.0, pytest-cov>=4.0, pytest-mock>=3.10, pylint>=2.15, mypy>=1.0, black>=23.0

### Tool Configuration

- [x] T005 [P] Create `backend/pyproject.toml` with black config (line-length=88, target-version=py310) and pytest config (testpaths, coverage)
- [x] T006 [P] Create `backend/.pylintrc` with max-line-length=88, max-args=5, max-locals=15
- [x] T007 [P] Create `backend/mypy.ini` with python_version=3.10, disallow_untyped_defs=True, strict_optional=True
- [x] T008 [P] Create `backend/README.md` with project description, setup instructions, and usage

### Test Infrastructure

- [x] T009 [P] Create `backend/tests/conftest.py` with pytest fixtures (task_manager fixture, sample_tasks fixture)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and shared exception handling that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Custom Exceptions (Required by All Stories)

- [x] T010 [P] Create custom exception classes in `backend/src/models/task.py`: TodoError (base), TaskNotFoundError, ValidationError, InvalidTaskDataError

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks and view their task list - the core value proposition

**Independent Test**: Launch app, add 3 tasks with different titles, view list showing all tasks with IDs and completion status

**Why MVP**: This is the minimum viable product - delivers immediate value as a basic task tracker. Without create and view, no other features have value.

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **RED PHASE**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T011 [P] [US1] Write unit tests for Task model creation in `backend/tests/unit/test_task.py`: test_task_creation, test_task_default_values, test_task_created_at_set
- [x] T012 [P] [US1] Write unit tests for Task title validation in `backend/tests/unit/test_task.py`: test_empty_title_raises_error, test_whitespace_title_raises_error, test_long_title_raises_error (>500 chars), test_title_trimmed
- [x] T013 [P] [US1] Write unit tests for Task serialization in `backend/tests/unit/test_task.py`: test_to_dict_format, test_to_dict_contains_all_fields
- [x] T014 [P] [US1] Write unit tests for TaskManager.add_task in `backend/tests/unit/test_task_manager.py`: test_add_task_returns_task, test_add_task_assigns_id, test_add_task_increments_id, test_add_task_empty_title_raises_error
- [x] T015 [P] [US1] Write unit tests for TaskManager.get_all_tasks in `backend/tests/unit/test_task_manager.py`: test_get_all_tasks_empty_list, test_get_all_tasks_returns_all, test_get_all_tasks_returns_copy
- [x] T016 [P] [US1] Write unit tests for TaskManager.count in `backend/tests/unit/test_task_manager.py`: test_count_empty, test_count_after_adds
- [x] T017 [US1] Run pytest for US1 tests - verify ALL tests FAIL (RED) before proceeding to implementation

### Implementation for User Story 1 (GREEN PHASE)

- [x] T018 [P] [US1] Implement Task model in `backend/src/models/task.py` with __init__, _validate_title, to_dict, __repr__ methods
- [x] T019 [US1] Implement TaskManager class in `backend/src/services/task_manager.py` with __init__ (initialize _tasks dict and _next_id counter)
- [x] T020 [US1] Implement TaskManager.add_task method in `backend/src/services/task_manager.py` (create task, assign ID, increment counter, add to _tasks)
- [x] T021 [P] [US1] Implement TaskManager.get_all_tasks method in `backend/src/services/task_manager.py` (return list of task values)
- [x] T022 [P] [US1] Implement TaskManager.count method in `backend/src/services/task_manager.py` (return len of _tasks)
- [x] T023 [US1] Run pytest for US1 tests - verify ALL tests PASS (GREEN)

### CLI for User Story 1

- [x] T024 [US1] Write integration test for add task flow in `backend/tests/integration/test_cli_flow.py`: test_add_task_success, test_view_empty_list, test_view_multiple_tasks
- [x] T025 [US1] Implement display_menu function in `backend/src/cli/menu.py` (show 6 menu options)
- [x] T026 [US1] Implement get_user_choice function in `backend/src/cli/menu.py` (input validation for menu choice)
- [x] T027 [US1] Implement view_tasks function in `backend/src/cli/menu.py` (call task_manager.get_all_tasks, display formatted list or empty message)
- [x] T028 [US1] Implement add_task_interactive function in `backend/src/cli/menu.py` (prompt for title, call task_manager.add_task, handle ValidationError)
- [x] T029 [US1] Create main_loop function in `backend/src/cli/menu.py` (menu loop with dispatch for options 1, 2, 6)
- [x] T030 [US1] Create application entry point in `backend/src/main.py` (import and call main_loop)
- [x] T031 [US1] Run integration tests for US1 - verify CLI flows work end-to-end
- [x] T032 [US1] Manual test: Run application, add 3 tasks, view list, verify output format and IDs

**Checkpoint**: User Story 1 complete and independently functional - Users can create and view tasks ✅

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Users can mark tasks as complete/incomplete to track progress

**Independent Test**: Create 3 tasks, mark task 1 complete, verify status shows "complete", mark task 1 incomplete, verify status shows "incomplete"

**Dependency**: Requires US1 (create/view) to be functional

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

> **RED PHASE**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T033 [P] [US2] Write unit tests for TaskManager.get_task in `backend/tests/unit/test_task_manager.py`: test_get_task_success, test_get_task_not_found_raises_error
- [x] T034 [P] [US2] Write unit tests for TaskManager.mark_complete in `backend/tests/unit/test_task_manager.py`: test_mark_complete_true, test_mark_complete_false, test_mark_complete_toggle, test_mark_complete_not_found_raises_error
- [x] T035 [US2] Run pytest for US2 tests - verify ALL tests FAIL (RED)

### Implementation for User Story 2 (GREEN PHASE)

- [x] T036 [P] [US2] Implement TaskManager.get_task method in `backend/src/services/task_manager.py` (lookup task by ID, raise TaskNotFoundError if not found)
- [x] T037 [US2] Implement TaskManager.mark_complete method in `backend/src/services/task_manager.py` (get task, update completed field, return task)
- [x] T038 [US2] Run pytest for US2 tests - verify ALL tests PASS (GREEN)

### CLI for User Story 2

- [x] T039 [US2] Write integration test for mark complete flow in `backend/tests/integration/test_cli_flow.py`: test_mark_complete_success, test_mark_incomplete_success, test_mark_nonexistent_task_error
- [x] T040 [US2] Implement mark_task_interactive function in `backend/src/cli/menu.py` (prompt for ID and status, call mark_complete, handle errors)
- [x] T041 [US2] Update main_loop in `backend/src/cli/menu.py` to dispatch option 3 (mark complete) to mark_task_interactive
- [x] T042 [US2] Run integration tests for US2 - verify mark complete flows work
- [x] T043 [US2] Manual test: Create 3 tasks, mark task 2 complete, view list to verify status, toggle back to incomplete

**Checkpoint**: User Stories 1 AND 2 both work independently - Users can create, view, and mark tasks complete ✅

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Users can update task titles to fix mistakes or refine descriptions

**Independent Test**: Create task "Buy milk", update to "Buy organic milk", view list to verify title changed

**Dependency**: Requires US1 (create/view) to be functional

### Tests for User Story 3 (TDD - Write FIRST) ⚠️

> **RED PHASE**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T044 [P] [US3] Write unit tests for TaskManager.update_task in `backend/tests/unit/test_task_manager.py`: test_update_task_success, test_update_task_empty_title_raises_error, test_update_task_not_found_raises_error, test_update_task_trims_whitespace
- [x] T045 [US3] Run pytest for US3 tests - verify ALL tests FAIL (RED)

### Implementation for User Story 3 (GREEN PHASE)

- [x] T046 [US3] Implement TaskManager.update_task method in `backend/src/services/task_manager.py` (get task, validate new title, update task.title, return task)
- [x] T047 [US3] Run pytest for US3 tests - verify ALL tests PASS (GREEN)

### CLI for User Story 3

- [x] T048 [US3] Write integration test for update task flow in `backend/tests/integration/test_cli_flow.py`: test_update_task_success, test_update_empty_title_rejected, test_update_nonexistent_task_error
- [x] T049 [US3] Implement update_task_interactive function in `backend/src/cli/menu.py` (prompt for ID and new title, call update_task, handle errors)
- [x] T050 [US3] Update main_loop in `backend/src/cli/menu.py` to dispatch option 4 (update) to update_task_interactive
- [x] T051 [US3] Run integration tests for US3 - verify update flows work
- [x] T052 [US3] Manual test: Create task, update title with special characters (unicode, quotes), verify handling

**Checkpoint**: User Stories 1, 2, AND 3 all work independently - Users can create, view, mark complete, and update tasks ✅

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Users can delete tasks they no longer need

**Independent Test**: Create 5 tasks, delete task 3, view list to verify 4 tasks remain with original IDs (no renumbering)

**Dependency**: Requires US1 (create/view) to be functional

### Tests for User Story 4 (TDD - Write FIRST) ⚠️

> **RED PHASE**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T053 [P] [US4] Write unit tests for TaskManager.delete_task in `backend/tests/unit/test_task_manager.py`: test_delete_task_success, test_delete_task_not_found_raises_error, test_delete_task_ids_not_reused, test_delete_reduces_count
- [x] T054 [US4] Run pytest for US4 tests - verify ALL tests FAIL (RED)

### Implementation for User Story 4 (GREEN PHASE)

- [x] T055 [US4] Implement TaskManager.delete_task method in `backend/src/services/task_manager.py` (check task exists, remove from _tasks, do NOT decrement _next_id)
- [x] T056 [US4] Run pytest for US4 tests - verify ALL tests PASS (GREEN)

### CLI for User Story 4

- [x] T057 [US4] Write integration test for delete task flow in `backend/tests/integration/test_cli_flow.py`: test_delete_task_success, test_delete_nonexistent_task_error, test_delete_with_confirmation
- [x] T058 [US4] Implement delete_task_interactive function in `backend/src/cli/menu.py` (prompt for ID with optional confirmation, call delete_task, handle errors)
- [x] T059 [US4] Update main_loop in `backend/src/cli/menu.py` to dispatch option 5 (delete) to delete_task_interactive
- [x] T060 [US4] Run integration tests for US4 - verify delete flows work
- [x] T061 [US4] Manual test: Create 10 tasks, delete tasks 2, 5, 8, verify remaining tasks keep original IDs

**Checkpoint**: User Stories 1, 2, 3, AND 4 all work independently - Full CRUD operations functional ✅

---

## Phase 7: User Story 5 - Session-Based Persistence (Priority: P1)

**Goal**: Tasks persist in memory during session but clear on exit (technical foundation)

**Independent Test**: Add 5 tasks, perform various operations, exit app, restart, verify list is empty

**Note**: This is largely already satisfied by in-memory dict implementation, but needs verification testing

### Tests for User Story 5 (TDD - Write FIRST) ⚠️

> **RED PHASE**: Write these tests FIRST, ensure they FAIL before implementation

- [x] T062 [P] [US5] Write integration test for session persistence in `backend/tests/integration/test_cli_flow.py`: test_tasks_persist_during_session, test_multiple_operations_data_intact
- [x] T063 [P] [US5] Write unit test for memory-only storage in `backend/tests/unit/test_task_manager.py`: test_no_file_persistence, test_fresh_instance_empty
- [x] T064 [US5] Run pytest for US5 tests - verify tests validate current behavior

### Implementation for User Story 5 (GREEN PHASE)

- [x] T065 [US5] Verify TaskManager uses in-memory dict (no file I/O) - already implemented in T019, add comments clarifying session-only persistence
- [x] T066 [US5] Add graceful exit handling in `backend/src/cli/menu.py` main_loop (clear tasks on exit, show goodbye message)
- [x] T067 [US5] Run pytest for US5 tests - verify tests PASS
- [x] T068 [US5] Manual test: Add 5 tasks, perform mix of operations, exit cleanly, restart, verify empty list

**Checkpoint**: All 5 user stories complete and independently functional - Phase I Basic tier features complete ✅

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, testing coverage, documentation, edge case handling

### Code Quality & Type Safety

- [ ] T069 [P] Run black formatter on all source files: `black backend/src/ backend/tests/`
- [ ] T070 [P] Run mypy type checker: `mypy backend/src/` - fix all type errors (target: 0 errors)
- [ ] T071 [P] Run pylint: `pylint backend/src/` - achieve score ≥8.0/10
- [ ] T072 Add docstrings (Google style) to all public functions in Task, TaskManager, and CLI modules

### Test Coverage & Quality

- [ ] T073 Run pytest with coverage: `pytest --cov=backend/src --cov-report=term-missing` - verify ≥80% coverage (NFR-005)
- [ ] T074 Add missing tests for edge cases identified in spec.md (special characters, long titles, high volume)
- [ ] T075 [P] Write performance test in `backend/tests/unit/test_performance.py`: test_1000_tasks_under_100ms (add/get/list 1000 tasks)
- [ ] T076 Run full test suite and verify 100% pass rate

### Error Handling & Edge Cases

- [ ] T077 Add input validation for task IDs in CLI (handle non-numeric input, negative numbers)
- [ ] T078 Add special character handling tests (unicode, quotes, newlines in titles)
- [ ] T079 Test and handle gracefully: Ctrl+C interrupt, invalid menu choices, very long titles
- [ ] T080 Update error messages to be user-friendly and actionable

### Documentation

- [ ] T081 [P] Update `backend/README.md` with installation, usage examples, testing instructions
- [ ] T082 [P] Add inline code comments for complex logic (task ID generation, error handling)
- [ ] T083 Verify all NFRs from spec.md are met (PEP 8, type hints, docstrings, coverage, linting)

### Final Validation

- [ ] T084 Run complete acceptance test suite covering all 16 scenarios from spec.md
- [ ] T085 Verify all 8 success criteria from spec.md are met (SC-001 through SC-008)
- [ ] T086 Verify all 4 quality metrics from spec.md are met (QM-001 through QM-004)
- [ ] T087 Run end-to-end manual test: Perform all 5 operations in sequence without errors

**Checkpoint**: Phase I complete - Ready for production use ✅

---

## Dependencies & Execution Strategy

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation) → User Stories (can run in parallel)

User Story Dependencies:
- US1 (Create/View): No dependencies - can implement first
- US2 (Mark Complete): Depends on US1 (needs tasks to exist)
- US3 (Update): Depends on US1 (needs tasks to exist)
- US4 (Delete): Depends on US1 (needs tasks to exist)
- US5 (Persistence): Cross-cutting, validates US1-4

Recommended Order:
1. US1 (P1) - MVP foundation
2. US2 (P2) or US3 (P3) or US4 (P4) - can do in any order after US1
3. US5 (P1) - validation of session behavior
```

### Parallel Execution Opportunities

**After Phase 2 (Foundation) is complete, these can run in parallel:**

1. **US1 Team**: T011-T032 (Create and view tasks)
2. **US2 Team** (after US1 implementation): T033-T043 (Mark complete)
3. **US3 Team** (after US1 implementation): T044-T052 (Update tasks)
4. **US4 Team** (after US1 implementation): T053-T061 (Delete tasks)

**Phase 8 (Polish) parallel opportunities:**
- T069, T070, T071, T072 (Code quality tasks)
- T081, T082 (Documentation tasks)

### Independent Testing per Story

Each user story can be tested independently:

- **US1 Test**: Launch app → Add 3 tasks → View list → Verify IDs and titles displayed
- **US2 Test**: Create task → Mark complete → View to verify status → Mark incomplete → Verify toggle
- **US3 Test**: Create task "Buy milk" → Update to "Buy organic milk" → View to verify change
- **US4 Test**: Create 5 tasks → Delete task 3 → View list → Verify 4 remain with original IDs
- **US5 Test**: Add tasks → Perform operations → Exit → Restart → Verify empty

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: Phase 3 (User Story 1) only
- **Tasks**: T001-T032 (32 tasks)
- **Delivers**: Create and view tasks - core value proposition
- **Time Estimate**: Smallest functional increment
- **User Value**: Immediate usable task tracker

**MVP+1**: Add Phase 4 (User Story 2 - Mark Complete)
- **Additional Tasks**: T033-T043 (11 tasks)
- **Delivers**: Task lifecycle management (complete/incomplete)
- **User Value**: Progress tracking

**Full Phase I**: All user stories (US1-US5) + Polish
- **Total Tasks**: 87 tasks
- **Delivers**: Complete Basic tier feature set per constitution

---

## Task Summary

**Total Tasks**: 87

**By Phase**:
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundation): 1 task
- Phase 3 (US1 - Create/View): 22 tasks
- Phase 4 (US2 - Mark Complete): 11 tasks
- Phase 5 (US3 - Update): 9 tasks
- Phase 6 (US4 - Delete): 9 tasks
- Phase 7 (US5 - Persistence): 7 tasks
- Phase 8 (Polish): 19 tasks

**By User Story**:
- US1: 22 tasks (MVP foundation)
- US2: 11 tasks
- US3: 9 tasks
- US4: 9 tasks
- US5: 7 tasks
- Infrastructure/Polish: 29 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel (40% of total)

**Test Tasks**: 27 tasks (31% of total) - Following strict TDD workflow

**Format Validation**: ✅ All tasks follow required checklist format with IDs, [P] markers where applicable, [Story] labels for user story phases, and exact file paths

---

## Acceptance Criteria

This feature is considered complete when:

1. ✅ All 87 tasks are checked off
2. ✅ All 16 acceptance scenarios from spec.md pass
3. ✅ Test coverage ≥ 80% (NFR-005, SC-006)
4. ✅ Code passes pylint ≥8.0/10 and mypy with 0 errors (SC-005)
5. ✅ All 8 success criteria from spec.md are met
6. ✅ All 4 quality metrics from spec.md are met
7. ✅ Users can perform complete workflow (add → view → mark → update → delete → exit)
8. ✅ Application runs without crashes for 10 consecutive operations (SC-008)

Ready to implement! Start with Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3 (US1 MVP) 🚀
