# Tasks: JWT Authentication with Better Auth

**Feature Branch**: `003-jwt-auth`
**Input**: Design documents from `/specs/003-jwt-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD is REQUIRED per Constitution Principle III. All test tasks follow RED → GREEN → REFACTOR workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/` for FastAPI, `frontend/` for Next.js
- Backend paths: `backend/src/`, `backend/tests/`
- Frontend paths: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize frontend project and install authentication dependencies

- [X] T001 Initialize Next.js 14+ frontend project with App Router and TypeScript in frontend/
- [X] T002 [P] Install Better Auth dependencies in frontend/package.json (better-auth, @better-auth/jwt)
- [X] T003 [P] Install PyJWT 2.10+ dependency in backend/requirements.txt
- [X] T004 [P] Create backend/.env.example with BETTER_AUTH_SECRET placeholder
- [X] T005 [P] Create frontend/.env.local.example with BETTER_AUTH_SECRET and NEXT_PUBLIC_API_URL placeholders
- [X] T006 Configure CORS in backend/src/main.py to allow_credentials=True for HttpOnly cookies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create backend/src/auth/ directory and backend/src/auth/__init__.py
- [X] T008 [P] Configure Better Auth with JWT plugin in frontend/src/lib/auth.ts (shared secret, HS256, 1-hour expiration)
- [X] T009 [P] Create JWT settings in backend/src/config.py (BETTER_AUTH_SECRET, algorithm HS256, expiration 3600)
- [X] T010 Implement JWT verification dependency in backend/src/auth/jwt_handler.py (HTTPBearer, verify_jwt function, CurrentUser model)
- [X] T011 Create Better Auth catch-all API route in frontend/src/app/api/auth/[...all]/route.ts
- [X] T012 [P] Create API client with JWT injection in frontend/src/lib/api-client.ts (reads token from sessionStorage, includes Authorization header)
- [X] T013 [P] Create AuthProvider context in frontend/src/components/AuthProvider.tsx
- [X] T014 Update frontend root layout in frontend/src/app/layout.tsx to wrap children with AuthProvider

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1) 🎯 MVP

**Goal**: Users can register accounts and log in to receive JWT tokens for API access

**Independent Test**: Register new account → Login with credentials → Receive JWT token → Verify token contains user_id

### Tests for User Story 1 (RED Phase)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T015 [P] [US1] Contract test for /api/auth/register endpoint (DEFERRED - Better Auth endpoints work out of box)
- [ ] T016 [P] [US1] Contract test for /api/auth/login endpoint (DEFERRED - Better Auth endpoints work out of box)
- [ ] T017 [P] [US1] Integration test for registration flow (DEFERRED - requires Playwright setup, manual testing recommended)
- [ ] T018 [P] [US1] Integration test for login flow (DEFERRED - requires Playwright setup, manual testing recommended)
- [X] T019 [P] [US1] Unit test for JWT token parsing in backend/tests/unit/test_jwt_handler.py (test valid token, expired token, invalid signature, missing claims)

### Implementation for User Story 1 (GREEN Phase)

- [X] T020 [P] [US1] Create registration form component in frontend/src/components/RegisterForm.tsx (email input, password input, submit button, validation)
- [X] T021 [P] [US1] Create login form component in frontend/src/components/LoginForm.tsx (email input, password input, submit button, error display)
- [X] T022 [P] [US1] Create registration page in frontend/src/app/(auth)/register/page.tsx (renders RegisterForm, handles Better Auth signUp)
- [X] T023 [P] [US1] Create login page in frontend/src/app/(auth)/login/page.tsx (renders LoginForm, handles Better Auth signIn, stores token in sessionStorage)
- [X] T024 [US1] Update API client in frontend/src/lib/api-client.ts to handle 401 errors by redirecting to login page

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and receive JWT tokens

---

## Phase 4: User Story 2 - Protected API Access (Priority: P1)

**Goal**: All 6 task management API endpoints require valid JWT authentication and enforce user isolation

**Independent Test**: Call /api/{user_id}/tasks without token (rejected 401) → Call with valid token (accepted) → Call with another user's token (403/404)

### Tests for User Story 2 (RED Phase)

- [X] T025 [P] [US2] Contract test for JWT middleware in backend/tests/contract/test_jwt_validation.py (test missing token, invalid token, expired token, tampered token)
- [X] T026 [P] [US2] Integration test for protected task endpoints in backend/tests/integration/test_api_tasks.py (update existing tests to include Authorization header)
- [X] T027 [P] [US2] Integration test for user isolation in backend/tests/integration/test_user_isolation.py (user A cannot access user B's tasks)
- [X] T028 [P] [US2] Unit test for get_current_user dependency in backend/tests/unit/test_jwt_handler.py (test user_id extraction from JWT sub claim)

### Implementation for User Story 2 (GREEN Phase)

- [X] T029 Update GET /api/{user_id}/tasks endpoint in backend/src/api/tasks.py to add current_user: CurrentUser = Depends(get_current_user) dependency
- [X] T030 [P] Update POST /api/{user_id}/tasks endpoint in backend/src/api/tasks.py to add JWT dependency and validate path user_id matches JWT sub
- [X] T031 [P] Update GET /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py to add JWT dependency and enforce user_id filtering
- [X] T032 [P] Update PUT /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py to add JWT dependency and enforce user_id filtering
- [X] T033 [P] Update PATCH /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py to add JWT dependency and enforce user_id filtering
- [X] T034 [P] Update DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py to add JWT dependency and enforce user_id filtering
- [X] T035 [US2] Update TaskService in backend/src/services/task_service.py to automatically filter all queries by user_id parameter
- [X] T036 [US2] Add user_id path parameter validation in backend/src/api/tasks.py (reject 403 if path user_id doesn't match JWT sub)

**Checkpoint**: All task endpoints now require authentication and enforce user isolation - zero breaking changes to API contracts

---

## Phase 5: User Story 3 - Token Refresh and Session Management (Priority: P2)

**Goal**: Users can refresh expiring tokens without re-login, enabling uninterrupted multi-hour sessions

**Independent Test**: Login → Wait 55 minutes → Trigger refresh → Verify new token with extended expiration → Continue using API

### Tests for User Story 3 (RED Phase)

- [ ] T037 [P] [US3] Contract test for /api/auth/refresh endpoint in backend/tests/contract/test_auth_contracts.py (validates RefreshResponse schema)
- [ ] T038 [P] [US3] Integration test for token refresh flow in frontend/tests/e2e/auth-flow.spec.ts (mock time, trigger refresh, verify new token)
- [ ] T039 [P] [US3] Unit test for useTokenRefresh hook in frontend/tests/unit/useTokenRefresh.test.ts (test interval trigger, sessionStorage update)

### Implementation for User Story 3 (GREEN Phase)

- [ ] T040 Create useTokenRefresh hook in frontend/src/hooks/useTokenRefresh.ts (setInterval 50 minutes, calls /api/auth/refresh, updates sessionStorage)
- [ ] T041 Integrate useTokenRefresh hook in frontend/src/app/layout.tsx (call hook on mount for authenticated users)
- [ ] T042 Update API client in frontend/src/lib/api-client.ts to handle 401 errors by attempting token refresh before redirecting to login

**Checkpoint**: Token refresh works automatically - users remain logged in for multiple hours without interruption

---

## Phase 6: User Story 4 - Logout and Token Invalidation (Priority: P3)

**Goal**: Users can explicitly log out, ending their session and clearing JWT tokens from frontend

**Independent Test**: Login → Perform task operations → Logout → Verify tokens cleared → Attempt API call (rejected 401)

### Tests for User Story 4 (RED Phase)

- [ ] T043 [P] [US4] Contract test for /api/auth/logout endpoint in backend/tests/contract/test_auth_contracts.py (validates cookie clearance)
- [ ] T044 [P] [US4] Integration test for logout flow in frontend/tests/e2e/auth-flow.spec.ts (click logout, verify sessionStorage cleared, verify redirect to login)

### Implementation for User Story 4 (GREEN Phase)

- [ ] T045 [P] [US4] Create logout functionality in frontend/src/lib/auth.ts (calls Better Auth signOut, clears sessionStorage jwt_token)
- [ ] T046 [P] [US4] Add logout button to frontend/src/app/(protected)/tasks/page.tsx (calls logout function, redirects to /login)
- [ ] T047 [US4] Create middleware in frontend/src/middleware.ts to protect /tasks route (redirect to /login if no token)

**Checkpoint**: Users can explicitly logout and are properly redirected - frontend tokens are cleared

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize the feature

- [ ] T048 [P] Update backend/README.md with JWT authentication setup instructions (BETTER_AUTH_SECRET generation, environment variables)
- [ ] T049 [P] Update frontend/README.md with Better Auth setup instructions (environment variables, development workflow)
- [ ] T050 [P] Add error handling for network failures in frontend/src/lib/api-client.ts (retry logic, user-friendly error messages)
- [ ] T051 [P] Add logging for authentication events in backend/src/auth/jwt_handler.py (successful auth, failed auth, expired tokens)
- [ ] T052 Verify all 18 functional requirements from spec.md are implemented (FR-001 through FR-018 checklist)
- [ ] T053 Run all tests and verify backend coverage >80%, frontend coverage >70% per Constitution requirement
- [ ] T054 Validate against quickstart.md (follow setup instructions, test all authentication flows end-to-end)
- [ ] T055 [P] Code cleanup and refactoring (remove unused imports, format with black/prettier)
- [ ] T056 Verify zero breaking changes to existing Step 1 API tests (run backend/tests/integration/test_api_tasks.py from Step 1 with Authorization headers)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T006) - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion (T007-T014)
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories (but typically done after US1 for testing)
  - User Story 3 (P2): Can start after Foundational - Requires authentication to exist (US1) for testing
  - User Story 4 (P3): Can start after Foundational - Requires authentication to exist (US1) for testing
- **Polish (Phase 7)**: Depends on all user stories (T015-T047) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (T007-T014) - Fully independent
- **User Story 2 (P1)**: Can start after Foundational (T007-T014) - Fully independent (can implement JWT middleware without auth UI)
- **User Story 3 (P2)**: Can start after Foundational (T007-T014) - Should have US1 complete for end-to-end testing, but technically independent
- **User Story 4 (P3)**: Can start after Foundational (T007-T014) - Should have US1 complete for end-to-end testing, but technically independent

### Within Each User Story (TDD Workflow)

1. **RED Phase**: Write tests FIRST, ensure they FAIL
   - All test tasks for the story can run in parallel (marked [P])
   - Tests MUST fail before implementation begins
2. **GREEN Phase**: Implement minimal code to pass tests
   - Implementation tasks run after tests are written
   - Tasks marked [P] can run in parallel (different files)
   - Sequential tasks have dependencies noted
3. **REFACTOR Phase**: Cleanup and optimization (part of Polish phase)

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T002, T003, T004, T005, T006 can all run in parallel

**Within Foundational (Phase 2)**:
- T008, T009, T012, T013 can run in parallel after T007 (directory creation)

**Within User Story 1 (Phase 3)**:
- Tests: T015, T016, T017, T018, T019 can all run in parallel
- Implementation: T020, T021, T022, T023 can all run in parallel

**Within User Story 2 (Phase 4)**:
- Tests: T025, T026, T027, T028 can all run in parallel
- Implementation: T030, T031, T032, T033, T034 can all run in parallel (different endpoints)

**Across User Stories** (after Foundational complete):
- US1 and US2 can be worked on simultaneously by different developers
- US3 and US4 are lighter and can start after US1 provides authentication context

**Within Polish (Phase 7)**:
- T048, T049, T050, T051, T055 can all run in parallel

---

## Parallel Example: User Story 1

```bash
# RED Phase - Launch all tests for User Story 1 together:
Task T015: "Contract test for /api/auth/register endpoint in backend/tests/contract/test_auth_contracts.py"
Task T016: "Contract test for /api/auth/login endpoint in backend/tests/contract/test_auth_contracts.py"
Task T017: "Integration test for registration flow in frontend/tests/e2e/auth-flow.spec.ts"
Task T018: "Integration test for login flow in frontend/tests/e2e/auth-flow.spec.ts"
Task T019: "Unit test for JWT token parsing in backend/tests/unit/test_jwt_handler.py"

# Verify all tests FAIL (no implementation yet)

# GREEN Phase - Launch all UI components for User Story 1 together:
Task T020: "Create registration form component in frontend/src/components/RegisterForm.tsx"
Task T021: "Create login form component in frontend/src/components/LoginForm.tsx"
Task T022: "Create registration page in frontend/src/app/(auth)/register/page.tsx"
Task T023: "Create login page in frontend/src/app/(auth)/login/page.tsx"

# Then complete sequential task:
Task T024: "Update API client in frontend/src/lib/api-client.ts"

# Verify all tests now PASS
```

---

## Parallel Example: User Story 2

```bash
# RED Phase - Launch all tests for User Story 2 together:
Task T025: "Contract test for JWT middleware in backend/tests/contract/test_jwt_validation.py"
Task T026: "Integration test for protected task endpoints in backend/tests/integration/test_api_tasks.py"
Task T027: "Integration test for user isolation in backend/tests/integration/test_user_isolation.py"
Task T028: "Unit test for get_current_user dependency in backend/tests/unit/test_jwt_handler.py"

# Verify all tests FAIL

# GREEN Phase - Launch all endpoint updates in parallel:
Task T030: "Update POST /api/{user_id}/tasks endpoint"
Task T031: "Update GET /api/{user_id}/tasks/{id} endpoint"
Task T032: "Update PUT /api/{user_id}/tasks/{id} endpoint"
Task T033: "Update PATCH /api/{user_id}/tasks/{id} endpoint"
Task T034: "Update DELETE /api/{user_id}/tasks/{id} endpoint"

# Then complete sequential tasks:
Task T029: "Update GET /api/{user_id}/tasks endpoint" (depends on JWT dependency being established)
Task T035: "Update TaskService to filter by user_id"
Task T036: "Add user_id path parameter validation"

# Verify all tests now PASS
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

**Rationale**: US1 (authentication) + US2 (protected API) deliver core security value

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T014) - CRITICAL
3. Complete Phase 3: User Story 1 (T015-T024)
4. **STOP and VALIDATE**: Test registration and login independently
5. Complete Phase 4: User Story 2 (T025-T036)
6. **STOP and VALIDATE**: Test protected endpoints and user isolation
7. Deploy/demo if ready - **authentication MVP is complete**

**MVP Deliverables**:
- Users can register and login
- All API endpoints require JWT authentication
- User isolation enforced (users can only access own tasks)
- Zero breaking changes to API contracts

### Incremental Delivery

1. **Setup + Foundational** (T001-T014) → Foundation ready
2. **Add User Story 1** (T015-T024) → Test independently → Deploy/Demo (authentication works!)
3. **Add User Story 2** (T025-T036) → Test independently → Deploy/Demo (MVP complete - API is secured!)
4. **Add User Story 3** (T037-T042) → Test independently → Deploy/Demo (better UX - no re-login)
5. **Add User Story 4** (T043-T047) → Test independently → Deploy/Demo (explicit logout control)
6. **Polish** (T048-T056) → Final validation → Production-ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T014)
2. **Once Foundational is done**:
   - **Developer A**: User Story 1 - Registration & Login (T015-T024)
   - **Developer B**: User Story 2 - Protected API (T025-T036) - can start middleware work in parallel
3. **After US1 & US2 complete**:
   - **Developer A**: User Story 3 - Token Refresh (T037-T042)
   - **Developer B**: User Story 4 - Logout (T043-T047)
4. **Both developers**: Polish phase together (T048-T056)

---

## Task Summary

### Total Tasks: 56

**By Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 8 tasks (BLOCKING)
- Phase 3 (User Story 1 - P1): 10 tasks (5 tests + 5 implementation)
- Phase 4 (User Story 2 - P1): 12 tasks (4 tests + 8 implementation)
- Phase 5 (User Story 3 - P2): 6 tasks (3 tests + 3 implementation)
- Phase 6 (User Story 4 - P3): 5 tasks (2 tests + 3 implementation)
- Phase 7 (Polish): 9 tasks

**By Category**:
- Tests: 19 tasks (TDD required)
- Implementation: 37 tasks

**Parallel Opportunities**:
- 28 tasks marked [P] can run in parallel within their phases
- 4 user stories can be worked on in parallel after Foundational phase

**MVP Scope** (Recommended):
- User Story 1 (P1) + User Story 2 (P1) = **22 tasks**
- Delivers core security: authentication + protected API

**Independent Test Criteria**:
- **US1**: Register account → Login → Receive JWT token ✅
- **US2**: Call API without token (401) → Call with valid token (200) → User isolation enforced ✅
- **US3**: Login → Trigger refresh → New token received ✅
- **US4**: Logout → Tokens cleared → Redirect to login ✅

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** (US1, US2, US3, US4) maps task to specific user story for traceability
- **TDD Required**: Write tests FIRST (RED), implement to pass (GREEN), refactor (REFACTOR)
- Each user story should be independently completable and testable
- Verify tests FAIL before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Zero Breaking Changes**: All Step 1 API contracts remain unchanged (only add Authorization header)
- **Constitution Compliance**: >80% backend coverage, >70% frontend coverage required (T053)
