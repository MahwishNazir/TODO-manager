# Tasks: Phase II Step 1 - REST API with Persistent Storage

**Input**: Design documents from `/specs/002-rest-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/task_interface.py, quickstart.md

**Tests**: Following TDD approach per constitution - all test tasks included and MUST be written FIRST (Red-Green-Refactor cycle)

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions

## Path Conventions

**Web app structure** (from plan.md):
- Backend: `backend/src/`, `backend/tests/`
- Paths shown below use backend/ prefix as per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure with src/ and tests/ directories per plan.md
- [ ] T002 Initialize Python virtual environment and install core dependencies (FastAPI, SQLModel, Uvicorn)
- [ ] T003 [P] Install development dependencies (pytest, httpx, pylint, mypy, black) in backend/requirements-dev.txt
- [ ] T004 [P] Configure linting tools (pylint in backend/.pylintrc, mypy in backend/mypy.ini)
- [ ] T005 [P] Configure code formatting (black) and Git hooks
- [ ] T006 Create .env.example file with DATABASE_URL, LOG_LEVEL, CORS_ORIGINS placeholders
- [ ] T007 [P] Update backend/README.md with setup instructions from quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Setup Neon PostgreSQL database and obtain connection string
- [ ] T009 Create database configuration module in backend/src/database.py with SQLModel engine and connection pooling (pool_size=5, pool_pre_ping=True)
- [ ] T010 [P] Initialize Alembic for database migrations in backend/alembic/
- [ ] T011 [P] Create FastAPI application entry point in backend/src/main.py with CORS middleware
- [ ] T012 [P] Implement logging middleware in backend/src/api/middleware.py
- [ ] T013 [P] Create FastAPI dependency for database sessions in backend/src/api/dependencies.py (get_db with yield pattern)
- [ ] T014 [P] Implement global exception handlers in backend/src/main.py (SQLAlchemyError → 500, ValueError → 422)
- [ ] T015 Create base Task SQLModel in backend/src/models/task.py with all fields (id, user_id, title, is_completed, created_at, updated_at)
- [ ] T016 Create Pydantic schemas in backend/src/models/schemas.py (TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, ErrorResponse)
- [ ] T017 Generate initial Alembic migration for tasks table with indexes
- [ ] T018 Apply migrations to Neon database (alembic upgrade head)
- [ ] T019 [P] Create pytest conftest.py with test database fixtures (in-memory SQLite) and TestClient
- [ ] T020 [P] Setup test environment configuration in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Retrieve Tasks via API (Priority: P1) 🎯 MVP

**Goal**: Enable API consumers to create tasks and retrieve them via HTTP endpoints with persistent storage across sessions

**Independent Test**: Make POST request to create task, then GET request to retrieve it; restart API server and verify task persists

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T021 [P] [US1] Unit test for TaskCreate schema validation in backend/tests/unit/test_schemas.py
- [ ] T022 [P] [US1] Unit test for Task model in backend/tests/unit/test_task.py (field validation, defaults)
- [ ] T023 [P] [US1] Contract test for POST /api/{user_id}/tasks endpoint in backend/tests/contract/test_openapi.py
- [ ] T024 [P] [US1] Contract test for GET /api/{user_id}/tasks endpoint in backend/tests/contract/test_openapi.py
- [ ] T025 [P] [US1] Contract test for GET /api/{user_id}/tasks/{id} endpoint in backend/tests/contract/test_openapi.py
- [ ] T026 [P] [US1] Integration test for create task journey in backend/tests/integration/test_api_tasks.py (POST returns 201, task has ID)
- [ ] T027 [P] [US1] Integration test for list tasks journey in backend/tests/integration/test_api_tasks.py (empty list, then list with tasks)
- [ ] T028 [P] [US1] Integration test for get single task in backend/tests/integration/test_api_tasks.py
- [ ] T029 [P] [US1] Integration test for user isolation in backend/tests/integration/test_api_tasks.py (user123 can't see user456 tasks)
- [ ] T030 [P] [US1] Integration test for validation errors in backend/tests/integration/test_api_tasks.py (empty title → 422)

**Verify all tests FAIL** before proceeding to implementation

### Implementation for User Story 1

- [ ] T031 [US1] Implement create_task service function in backend/src/services/task_service.py
- [ ] T032 [US1] Implement get_all_tasks service function in backend/src/services/task_service.py (filter by user_id)
- [ ] T033 [US1] Implement get_task_by_id service function in backend/src/services/task_service.py (enforce user isolation)
- [ ] T034 [US1] Create API router in backend/src/api/routes/tasks.py with route definitions
- [ ] T035 [US1] Implement POST /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py
- [ ] T036 [US1] Implement GET /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py
- [ ] T037 [US1] Implement GET /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [ ] T038 [US1] Add user_id validation helper in backend/src/api/routes/tasks.py (alphanumeric + hyphens/underscores, max 50 chars)
- [ ] T039 [US1] Register tasks router in backend/src/main.py
- [ ] T040 [US1] Add error handling for 404 (task not found or wrong user) in service layer
- [ ] T041 [US1] Add logging for task creation and retrieval operations

**Verify all User Story 1 tests PASS** (Red → Green)

**Checkpoint**: At this point, User Story 1 should be fully functional - can create and retrieve tasks via API with database persistence

---

## Phase 4: User Story 2 - Mark Tasks Complete via API (Priority: P2)

**Goal**: Enable API consumers to toggle task completion status via HTTP endpoint

**Independent Test**: Create task via POST, mark complete via PATCH, verify is_completed=true; toggle again, verify is_completed=false

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL)

- [ ] T042 [P] [US2] Contract test for PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/tests/contract/test_openapi.py
- [ ] T043 [P] [US2] Integration test for toggle completion journey in backend/tests/integration/test_api_tasks.py (false→true→false)
- [ ] T044 [P] [US2] Integration test for complete non-existent task in backend/tests/integration/test_api_tasks.py (404 error)
- [ ] T045 [P] [US2] Integration test for user isolation on complete in backend/tests/integration/test_api_tasks.py (user123 can't complete user456 task → 404)

**Verify all tests FAIL** before proceeding to implementation

### Implementation for User Story 2

- [ ] T046 [US2] Implement toggle_completion service function in backend/src/services/task_service.py
- [ ] T047 [US2] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/api/routes/tasks.py
- [ ] T048 [US2] Update updated_at timestamp on completion toggle in service function
- [ ] T049 [US2] Add logging for completion toggle operations

**Verify all User Story 2 tests PASS**

**Checkpoint**: At this point, User Stories 1 AND 2 work independently - can create, retrieve, and complete tasks

---

## Phase 5: User Story 3 - Update Task Details via API (Priority: P3)

**Goal**: Enable API consumers to update task titles via HTTP endpoint

**Independent Test**: Create task, update title via PUT, verify new title in response and updated_at changed

### Tests for User Story 3 (TDD - Write FIRST, ensure FAIL)

- [ ] T050 [P] [US3] Unit test for TaskUpdate schema validation in backend/tests/unit/test_schemas.py
- [ ] T051 [P] [US3] Contract test for PUT /api/{user_id}/tasks/{id} endpoint in backend/tests/contract/test_openapi.py
- [ ] T052 [P] [US3] Integration test for update task journey in backend/tests/integration/test_api_tasks.py (title changes, updated_at changes)
- [ ] T053 [P] [US3] Integration test for update with empty title in backend/tests/integration/test_api_tasks.py (422 error)
- [ ] T054 [P] [US3] Integration test for update non-existent task in backend/tests/integration/test_api_tasks.py (404 error)
- [ ] T055 [P] [US3] Integration test for user isolation on update in backend/tests/integration/test_api_tasks.py

**Verify all tests FAIL** before proceeding to implementation

### Implementation for User Story 3

- [ ] T056 [US3] Implement update_task service function in backend/src/services/task_service.py
- [ ] T057 [US3] Implement PUT /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [ ] T058 [US3] Ensure updated_at timestamp is auto-updated via SQLModel/database trigger
- [ ] T059 [US3] Add logging for update operations

**Verify all User Story 3 tests PASS**

**Checkpoint**: All user stories 1-3 work independently - full CRUD except delete

---

## Phase 6: User Story 4 - Delete Tasks via API (Priority: P4)

**Goal**: Enable API consumers to permanently delete tasks via HTTP endpoint

**Independent Test**: Create task, delete via DELETE, verify 204 response; attempt GET on deleted task, verify 404

### Tests for User Story 4 (TDD - Write FIRST, ensure FAIL)

- [ ] T060 [P] [US4] Contract test for DELETE /api/{user_id}/tasks/{id} endpoint in backend/tests/contract/test_openapi.py
- [ ] T061 [P] [US4] Integration test for delete task journey in backend/tests/integration/test_api_tasks.py (204 response, task removed)
- [ ] T062 [P] [US4] Integration test for delete non-existent task in backend/tests/integration/test_api_tasks.py (404 error)
- [ ] T063 [P] [US4] Integration test for user isolation on delete in backend/tests/integration/test_api_tasks.py
- [ ] T064 [P] [US4] Integration test for idempotent delete in backend/tests/integration/test_api_tasks.py (delete twice → both 404)

**Verify all tests FAIL** before proceeding to implementation

### Implementation for User Story 4

- [ ] T065 [US4] Implement delete_task service function in backend/src/services/task_service.py (hard delete)
- [ ] T066 [US4] Implement DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py (return 204)
- [ ] T067 [US4] Add logging for delete operations

**Verify all User Story 4 tests PASS**

**Checkpoint**: Full CRUD operations complete - create, read, update, delete, complete

---

## Phase 7: User Story 5 - Database Persistence Across Sessions (Priority: P1)

**Goal**: Verify tasks persist in database across FastAPI application restarts

**Independent Test**: Create 5 tasks, restart uvicorn server, verify all 5 tasks still retrievable via GET

### Tests for User Story 5 (TDD - Write FIRST, ensure FAIL)

- [ ] T068 [P] [US5] Integration test for database persistence in backend/tests/integration/test_database.py (create tasks, close session, reopen, verify exists)
- [ ] T069 [P] [US5] Integration test for task ID continuity in backend/tests/integration/test_database.py (create, restart DB connection, create again, verify ID increments correctly)

**Verify all tests FAIL** before proceeding to implementation

### Implementation for User Story 5

- [ ] T070 [US5] Verify SQLModel engine configuration includes autocommit=False for transactions
- [ ] T071 [US5] Verify database session commits on successful operations in service layer
- [ ] T072 [US5] Add database connection health check endpoint GET /health in backend/src/api/routes/tasks.py
- [ ] T073 [US5] Test manual restart: Create tasks via API, stop uvicorn, start uvicorn, verify tasks persist

**Verify all User Story 5 tests PASS**

**Checkpoint**: Database persistence confirmed - no data loss on restart

---

## Phase 8: User Story 6 - User Isolation Without Authentication (Priority: P1)

**Goal**: Enforce data isolation by user_id so different users' tasks don't mix

**Independent Test**: Create tasks for user123 and user456, verify each GET /api/{user_id}/tasks returns only that user's tasks

### Tests for User Story 6 (TDD - Write FIRST, ensure FAIL)

- [ ] T074 [P] [US6] Integration test for user data isolation in backend/tests/integration/test_api_tasks.py (user123 tasks != user456 tasks)
- [ ] T075 [P] [US6] Integration test for cross-user access prevention in backend/tests/integration/test_api_tasks.py (user123 can't GET user456's task by ID → 404)
- [ ] T076 [P] [US6] Integration test for cross-user update prevention in backend/tests/integration/test_api_tasks.py (user123 can't PUT user456's task → 404)
- [ ] T077 [P] [US6] Integration test for cross-user delete prevention in backend/tests/integration/test_api_tasks.py
- [ ] T078 [P] [US6] Integration test for cross-user complete prevention in backend/tests/integration/test_api_tasks.py

**Verify all tests FAIL** before proceeding to implementation

### Implementation for User Story 6

- [ ] T079 [US6] Review all service functions ensure user_id filtering on database queries
- [ ] T080 [US6] Ensure 404 (not 403) returned for wrong user access (don't reveal task existence)
- [ ] T081 [US6] Add database index on (user_id, is_completed) for filtered queries in Alembic migration
- [ ] T082 [US6] Add logging for user isolation enforcement

**Verify all User Story 6 tests PASS**

**Checkpoint**: User isolation confirmed - 0% cross-user data leakage

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T083 [P] Export OpenAPI schema to backend/specs/002-rest-api/contracts/openapi.yaml for version control
- [ ] T084 [P] Validate OpenAPI schema matches spec.md requirements in backend/tests/contract/test_openapi.py
- [ ] T085 [P] Run black formatter on all Python files in backend/src/ and backend/tests/
- [ ] T086 [P] Run pylint on backend/src/ and verify score ≥8.0/10
- [ ] T087 [P] Run mypy on backend/src/ and verify zero errors
- [ ] T088 [P] Run pytest with coverage report and verify ≥80% coverage
- [ ] T089 [P] Update backend/README.md with API usage examples from quickstart.md
- [ ] T090 [P] Create .env file with actual Neon DATABASE_URL (do not commit to git)
- [ ] T091 [P] Test all 6 endpoints via Swagger UI at http://localhost:8000/docs
- [ ] T092 [P] Test all 6 endpoints via curl commands from quickstart.md
- [ ] T093 Performance test: Create 1000 tasks for single user, verify GET /tasks completes in <50ms
- [ ] T094 Concurrency test: Send 100 concurrent requests, verify no errors and response time <500ms
- [ ] T095 [P] Document edge cases handling (malformed JSON, SQL injection attempts) in backend/README.md
- [ ] T096 Security audit: Verify no secrets in code, all DATABASE_URL in .env, .env in .gitignore
- [ ] T097 Run full quickstart.md validation: Follow guide from scratch, verify API running in <15 minutes
- [ ] T098 Create sample Postman collection in backend/specs/002-rest-api/contracts/postman_collection.json (optional)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if team capacity allows)
  - Or sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3) → US4 (P4) → US5 (P1) → US6 (P1)
  - **Note**: US1, US5, US6 are all P1 priority - critical path for MVP
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (US1 - P1)**: Can start after Foundational (Phase 2) - **NO dependencies** on other stories
- **User Story 2 (US2 - P2)**: Can start after Foundational (Phase 2) - **NO dependencies** (uses existing Task model and service layer)
- **User Story 3 (US3 - P3)**: Can start after Foundational (Phase 2) - **NO dependencies** (uses existing Task model and service layer)
- **User Story 4 (US4 - P4)**: Can start after Foundational (Phase 2) - **NO dependencies** (uses existing Task model and service layer)
- **User Story 5 (US5 - P1)**: Can start after US1 (needs create functionality to test persistence)
- **User Story 6 (US6 - P1)**: Can start after US1 (needs create functionality to test isolation)

**All user stories are independently testable** once foundational phase is complete.

### Within Each User Story

**TDD Cycle (Red-Green-Refactor)**:
1. Tests FIRST - Write all tests for story, **verify they FAIL** (Red)
2. Implementation - Minimal code to pass tests (Green)
3. Refactor - Clean up code while keeping tests green
4. Story complete - All tests pass before moving to next priority

**Execution within story**:
- All tests marked [P] can run in parallel (different test files)
- Implementation: Models → Services → Endpoints → Error handling → Logging
- Core implementation before integration
- Story fully tested before moving to next

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005, T007 can run in parallel
- **Foundational Phase**: T010, T011, T012, T013, T014, T019, T020 can run in parallel after T008-T009
- **User Story Tests**: All tests within a story marked [P] can run in parallel
- **Cross-Story Parallelization**: After Foundational complete, US1-US4 can be developed in parallel by different developers
- **Polish Phase**: T083-T098 (almost all) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Step 1: Launch all tests for User Story 1 together (write first, verify FAIL):
Task T021: "Unit test for TaskCreate schema validation in backend/tests/unit/test_schemas.py"
Task T022: "Unit test for Task model in backend/tests/unit/test_task.py"
Task T023: "Contract test for POST endpoint in backend/tests/contract/test_openapi.py"
Task T024: "Contract test for GET all endpoint in backend/tests/contract/test_openapi.py"
Task T025: "Contract test for GET one endpoint in backend/tests/contract/test_openapi.py"
Task T026: "Integration test for create task journey in backend/tests/integration/test_api_tasks.py"
Task T027: "Integration test for list tasks journey in backend/tests/integration/test_api_tasks.py"
Task T028: "Integration test for get single task in backend/tests/integration/test_api_tasks.py"
Task T029: "Integration test for user isolation in backend/tests/integration/test_api_tasks.py"
Task T030: "Integration test for validation errors in backend/tests/integration/test_api_tasks.py"

# Verify all tests FAIL (Red state)

# Step 2: Implement service functions (sequential - depend on each other):
Task T031: "Implement create_task in backend/src/services/task_service.py"
Task T032: "Implement get_all_tasks in backend/src/services/task_service.py"
Task T033: "Implement get_task_by_id in backend/src/services/task_service.py"

# Step 3: Implement endpoints (sequential - depend on services):
Task T034: "Create API router in backend/src/api/routes/tasks.py"
Task T035-T037: "Implement POST, GET all, GET one endpoints"
Task T038-T041: "Add validation, error handling, logging"

# Verify all tests PASS (Green state)
```

---

## Parallel Example: Multiple User Stories

```bash
# After Foundational Phase completes, launch in parallel:

Developer A:
  - Phase 3: User Story 1 (tests → implementation)

Developer B:
  - Phase 4: User Story 2 (tests → implementation)

Developer C:
  - Phase 5: User Story 3 (tests → implementation)

# Each story completes independently and integrates seamlessly
```

---

## Implementation Strategy

### MVP First (User Stories 1, 5, 6 Only - All P1)

1. Complete Phase 1: Setup → Foundation laid
2. Complete Phase 2: Foundational → **CRITICAL** - blocks all stories
3. Complete Phase 3: User Story 1 (Create and Retrieve) → Core CRUD operations
4. Complete Phase 7: User Story 5 (Persistence) → Verify data survives restarts
5. Complete Phase 8: User Story 6 (User Isolation) → Security foundation
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Run quickstart.md validation
8. Deploy/demo if ready → **MVP COMPLETE**

**MVP Scope**: Create tasks, retrieve tasks, data persists, users isolated (no update, delete, or complete yet)

### Incremental Delivery (Add P2-P4 Features)

1. Complete MVP (Setup + Foundational + US1 + US5 + US6) → Test independently
2. Add Phase 4: User Story 2 (Mark Complete) → Test independently → Deploy/Demo
3. Add Phase 5: User Story 3 (Update) → Test independently → Deploy/Demo
4. Add Phase 6: User Story 4 (Delete) → Test independently → Deploy/Demo
5. Complete Phase 9: Polish → Final quality checks
6. **FULL FEATURE SET COMPLETE**

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers (after Foundational Phase complete):

1. **Team completes Setup + Foundational together** (T001-T020)
2. **Parallel story development**:
   - Developer A: Phase 3 (US1) + Phase 7 (US5)
   - Developer B: Phase 4 (US2) + Phase 5 (US3)
   - Developer C: Phase 6 (US4) + Phase 8 (US6)
3. Stories integrate and test independently
4. Team completes Polish together (Phase 9)

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- **Each user story should be independently completable and testable**
- **TDD mandatory**: Write tests FIRST, verify FAIL (Red), implement code, verify PASS (Green), refactor
- **Commit strategy**: Commit after each task or logical group (e.g., all tests for a story)
- **Stop at any checkpoint** to validate story independently
- **Avoid**: Vague tasks, same file conflicts, cross-story dependencies that break independence
- **Constitution compliance**: All 7 core principles satisfied (see plan.md Constitution Check section)

---

## Task Summary

**Total Tasks**: 98
- **Setup**: 7 tasks
- **Foundational**: 13 tasks (BLOCKING)
- **User Story 1** (P1 - Create/Retrieve): 21 tasks (11 tests + 10 implementation)
- **User Story 2** (P2 - Complete): 8 tasks (4 tests + 4 implementation)
- **User Story 3** (P3 - Update): 10 tasks (6 tests + 4 implementation)
- **User Story 4** (P4 - Delete): 8 tasks (5 tests + 3 implementation)
- **User Story 5** (P1 - Persistence): 6 tasks (2 tests + 4 implementation)
- **User Story 6** (P1 - User Isolation): 9 tasks (5 tests + 4 implementation)
- **Polish**: 16 tasks

**Parallel Opportunities**: 45+ tasks marked [P] can run in parallel within their phase
**MVP Scope**: 47 tasks (Setup + Foundational + US1 + US5 + US6)
**Full Feature Set**: All 98 tasks

**Test Coverage Strategy**:
- Unit tests: Schema validation, model validation
- Contract tests: OpenAPI schema compliance for all 6 endpoints
- Integration tests: End-to-end journeys, user isolation, error handling
- Target: ≥80% code coverage (per constitution)

---

**Ready to implement**: All tasks are specific, testable, and executable following TDD (Red-Green-Refactor) workflow.

**Next steps**: Begin with Phase 1 (Setup), proceed through Foundational (Phase 2), then tackle user stories in priority order (P1 first for MVP).
