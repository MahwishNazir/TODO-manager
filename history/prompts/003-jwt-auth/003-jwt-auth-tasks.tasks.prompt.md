---
id: 003
title: JWT Auth Task Generation
stage: tasks
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5
feature: 003-jwt-auth
branch: 003-jwt-auth
user: User
command: /sp.tasks
labels: ["authentication", "jwt", "tdd", "tasks", "user-stories", "phase-2"]
links:
  spec: specs/003-jwt-auth/spec.md
  ticket: null
  adr: history/adr/001-better-auth-library.md, history/adr/002-httponly-cookies-token-storage.md, history/adr/003-hs256-jwt-algorithm.md, history/adr/004-stateless-jwt-authentication.md, history/adr/005-proactive-token-refresh.md
  pr: null
files:
  - specs/003-jwt-auth/tasks.md
tests:
  - 19 test tasks defined in tasks.md (TDD RED phase)
---

## Prompt

User command: `/sp.tasks`

Context: Generate testable task breakdown for JWT Authentication (Phase II Step 2) implementation

The `/sp.tasks` command was invoked to generate a comprehensive task breakdown organized by user story with TDD workflow. The command loaded design documents from `specs/003-jwt-auth/`:
- **Required**: plan.md (technical stack, project structure), spec.md (4 user stories with priorities)
- **Optional**: data-model.md (User, JWT, Task entities), contracts/ (authentication-api.yaml, protected-tasks-api.yaml), research.md (8 technical decisions)

The task generation followed these principles:
- **User Story Organization**: Tasks grouped by user story (US1, US2, US3, US4) for independent implementation
- **TDD Workflow**: RED → GREEN → REFACTOR per Constitution Principle III (mandatory)
- **Parallel Opportunities**: 28 tasks marked [P] can run in parallel
- **MVP Scope**: User Story 1 + User Story 2 (22 tasks) delivers core security value
- **Zero Breaking Changes**: All Step 1 API contracts preserved

## Response snapshot

Generated comprehensive `tasks.md` with 56 tasks organized into 7 phases:

**Task Breakdown**:

**Phase 1: Setup (6 tasks)**
- T001-T006: Initialize Next.js frontend, install Better Auth/PyJWT, configure environment variables and CORS

**Phase 2: Foundational (8 tasks) - BLOCKING**
- T007-T014: Create authentication infrastructure (JWT verification, Better Auth config, API client, AuthProvider)
- **CRITICAL**: All user stories blocked until this phase completes

**Phase 3: User Story 1 - Registration & Login (P1) - 10 tasks**
- RED Phase: T015-T019 (5 test tasks - contract tests, integration tests, unit tests)
- GREEN Phase: T020-T024 (5 implementation tasks - registration form, login form, pages, API client error handling)
- **Deliverable**: Users can register accounts and log in to receive JWT tokens

**Phase 4: User Story 2 - Protected API Access (P1) - 12 tasks**
- RED Phase: T025-T028 (4 test tasks - JWT middleware tests, user isolation tests)
- GREEN Phase: T029-T036 (8 implementation tasks - update 6 task endpoints with JWT dependency, TaskService filtering, validation)
- **Deliverable**: All API endpoints require authentication and enforce user isolation

**Phase 5: User Story 3 - Token Refresh (P2) - 6 tasks**
- RED Phase: T037-T039 (3 test tasks - refresh endpoint contract, integration test, hook unit test)
- GREEN Phase: T040-T042 (3 implementation tasks - useTokenRefresh hook, integration in layout, API client refresh logic)
- **Deliverable**: Tokens refresh automatically at 50 minutes, enabling multi-hour sessions

**Phase 6: User Story 4 - Logout (P3) - 5 tasks**
- RED Phase: T043-T044 (2 test tasks - logout endpoint contract, integration test)
- GREEN Phase: T045-T047 (3 implementation tasks - logout function, logout button, route protection middleware)
- **Deliverable**: Users can explicitly log out with tokens cleared and proper redirect

**Phase 7: Polish & Cross-Cutting (9 tasks)**
- T048-T056: Documentation updates, error handling, logging, requirements validation, test coverage verification, quickstart validation, code cleanup, zero breaking changes verification

**Task Organization Features**:
- **Checklist Format**: All tasks follow `- [ ] [ID] [P?] [Story?] Description with file path`
- **Task IDs**: Sequential T001-T056
- **Story Labels**: US1, US2, US3, US4 map tasks to user stories
- **Parallel Markers**: [P] identifies 28 parallelizable tasks
- **File Paths**: Specific paths for all implementation tasks (backend/src/, frontend/src/, tests/)

**TDD Compliance**:
- 19 test tasks in RED phase (must FAIL before implementation)
- 37 implementation tasks in GREEN phase (make tests pass)
- Constitution requirement: >80% backend coverage, >70% frontend coverage

**Dependencies & Execution Order**:
- Setup (Phase 1) → Foundational (Phase 2) → User Stories (Phases 3-6 can run in parallel) → Polish (Phase 7)
- Foundational phase BLOCKS all user stories (must complete T007-T014 first)
- User stories are independent after Foundational completes

**Parallel Opportunities Documented**:
- Within Setup: 5 tasks can run in parallel
- Within Foundational: 4 tasks can run in parallel
- Within User Story 1: 9 tasks can run in parallel (5 tests + 4 UI components)
- Within User Story 2: 9 tasks can run in parallel (4 tests + 5 endpoint updates)
- Across User Stories: All 4 stories can be worked on simultaneously after Foundational phase

**MVP Scope (Recommended)**:
- User Story 1 (P1) + User Story 2 (P1) = 22 tasks
- Delivers: User registration/login + JWT-protected API + user isolation
- Zero breaking changes to existing Step 1 endpoints

**Independent Test Criteria per Story**:
- US1: Register → Login → Receive JWT token → Verify claims ✅
- US2: API without token (401) → API with valid token (200) → User isolation enforced ✅
- US3: Login → Trigger refresh → New token with extended expiration ✅
- US4: Logout → Tokens cleared → Redirect to login ✅

## Outcome

- ✅ **Impact**: Complete task breakdown ready for `/sp.implement` command. 56 tasks organized by user story with TDD workflow, clear dependencies, parallel opportunities, and MVP scope. Each user story is independently implementable and testable.
- 🧪 **Tests**: 19 test tasks defined (RED phase) covering contract tests, integration tests, unit tests, and E2E tests
- 📁 **Files**: 1 file created - `specs/003-jwt-auth/tasks.md` (56 tasks, ~500 lines)
- 🔁 **Next prompts**: `/sp.implement` to execute task breakdown with TDD workflow, or start manual implementation with Setup phase (T001-T006)
- 🧠 **Reflection**: Task breakdown successfully organized by user story to enable independent implementation and testing. TDD workflow enforced with RED → GREEN phases. MVP scope clearly identified (US1 + US2 = 22 tasks). 28 parallel opportunities documented for team collaboration. All tasks follow checklist format with IDs, story labels, parallel markers, and file paths. Constitution compliance verified: >80% backend coverage, >70% frontend coverage required.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation completed successfully with comprehensive organization
- Graders run and results (PASS/FAIL): PASS - All tasks follow checklist format; user stories independently testable; TDD workflow enforced; MVP scope identified; parallel opportunities documented
- Prompt variant (if applicable): Standard `/sp.tasks` workflow with user story organization
- Next experiment (smallest change to try): N/A - task breakdown meets all quality criteria and is ready for implementation
