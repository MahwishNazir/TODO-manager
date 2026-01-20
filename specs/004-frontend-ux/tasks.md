# Tasks: Frontend Application & UX (Production-Ready)

**Input**: Design documents from `/specs/004-frontend-ux/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are optional for this feature (spec states "focus on functional testing in Phase II Step 3"). Test tasks are NOT included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` directory at repository root
- All frontend code in `frontend/app/`, `frontend/components/`, `frontend/lib/`, `frontend/types/`, `frontend/hooks/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic configuration

- [X] T001 Initialize Next.js 16 project with TypeScript and App Router in frontend/
- [X] T002 Install core dependencies (react, react-dom, next, typescript) in frontend/package.json
- [X] T003 [P] Install Better Auth dependencies (better-auth, @better-auth/react) in frontend/package.json
- [X] T004 [P] Install shadcn/ui dependencies and initialize with `npx shadcn@latest init` in frontend/
- [X] T005 [P] Install form dependencies (react-hook-form, @hookform/resolvers, zod) in frontend/package.json
- [X] T006 [P] Install UI dependencies (sonner, next-themes, lucide-react) in frontend/package.json
- [X] T007 Configure TypeScript strict mode in frontend/tsconfig.json
- [X] T008 Configure Tailwind CSS with custom theme colors in frontend/tailwind.config.ts
- [X] T009 [P] Create .env.example with required environment variables in frontend/.env.example
- [X] T010 Create global styles with CSS variables for dual themes in frontend/app/globals.css

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create TypeScript types for Task matching backend schema in frontend/types/task.ts
- [X] T012 [P] Create TypeScript types for User session in frontend/types/user.ts
- [X] T013 [P] Create TypeScript types for API responses and errors in frontend/types/api.ts
- [X] T014 [P] Create TypeScript types for form state in frontend/types/form.ts
- [X] T015 Create Zod validation schemas for forms in frontend/lib/validations.ts
- [X] T016 Create app constants (API URLs, limits, routes) in frontend/lib/constants.ts
- [X] T017 Create shadcn/ui utility function (cn) in frontend/lib/utils.ts
- [X] T018 Configure Better Auth server instance in frontend/lib/auth.ts
- [X] T019 Create Better Auth client utilities in frontend/lib/auth-client.ts
- [X] T020 Create API client with JWT cookie support in frontend/lib/api-client.ts
- [X] T021 Implement task API methods (create, list, get, update, toggle, delete) in frontend/lib/api-client.ts
- [X] T022 Create ApiError class with status helpers in frontend/lib/api-client.ts
- [X] T023 Install shadcn/ui Button component via `npx shadcn@latest add button`
- [X] T024 [P] Install shadcn/ui Card component via `npx shadcn@latest add card`
- [X] T025 [P] Install shadcn/ui Input component via `npx shadcn@latest add input`
- [X] T026 [P] Install shadcn/ui Label component via `npx shadcn@latest add label`
- [X] T027 [P] Install shadcn/ui Form component via `npx shadcn@latest add form`
- [X] T028 [P] Install shadcn/ui Dialog component via `npx shadcn@latest add dialog`
- [X] T029 [P] Install shadcn/ui Checkbox component via `npx shadcn@latest add checkbox`
- [X] T030 [P] Install shadcn/ui Skeleton component via `npx shadcn@latest add skeleton`
- [X] T031 [P] Install shadcn/ui Alert Dialog component via `npx shadcn@latest add alert-dialog`
- [X] T032 [P] Install shadcn/ui Dropdown Menu component via `npx shadcn@latest add dropdown-menu`
- [X] T033 Create ThemeProvider component with next-themes in frontend/components/providers/theme-provider.tsx
- [X] T034 Create root layout with providers and Toaster in frontend/app/layout.tsx
- [X] T035 Create custom 404 page in frontend/app/not-found.tsx
- [X] T036 [P] Create global error boundary in frontend/app/error.tsx
- [X] T037 [P] Create global loading state in frontend/app/loading.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Onboarding and Authentication (Priority: P1) MVP

**Goal**: Enable user registration and login with JWT authentication

**Independent Test**: Visit /signup, create account with email/password, login at /signin, verify redirect to /tasks dashboard with authenticated session

### Implementation for User Story 1

- [X] T038 [US1] Create Better Auth route handler for authentication in frontend/app/api/auth/[...all]/route.ts
- [X] T039 [US1] Create AuthProvider context component in frontend/components/providers/auth-provider.tsx
- [X] T040 [US1] Create useAuth hook for session management in frontend/hooks/use-auth.ts
- [X] T041 [US1] Create signup form component with React Hook Form + Zod in frontend/components/auth/signup-form.tsx
- [X] T042 [US1] Create signin form component with React Hook Form + Zod in frontend/components/auth/signin-form.tsx
- [X] T043 [US1] Create auth route group layout in frontend/app/(auth)/layout.tsx
- [X] T044 [US1] Create signup page at /signup in frontend/app/(auth)/signup/page.tsx
- [X] T045 [US1] Create signin page at /signin in frontend/app/(auth)/signin/page.tsx
- [X] T046 [US1] Implement form validation with error messages for email and password fields
- [X] T047 [US1] Add loading states to auth forms during submission
- [X] T048 [US1] Implement redirect to /tasks on successful authentication
- [X] T049 [US1] Implement redirect from auth pages if already authenticated
- [X] T050 [US1] Create auth-guard component for protected routes in frontend/components/auth/auth-guard.tsx
- [X] T051 [US1] Add logout functionality to clear session and redirect to /signin
- [X] T052 [US1] Handle 401 responses by redirecting to /signin with "Session expired" message

**Checkpoint**: Users can signup, signin, and maintain authenticated sessions

---

## Phase 4: User Story 2 - View Task Dashboard (Priority: P1) MVP

**Goal**: Display all user tasks in an organized dashboard layout

**Independent Test**: Login, navigate to /tasks, verify all tasks display with title, checkbox, timestamps, and action buttons; verify empty state shows when no tasks exist

### Implementation for User Story 2

- [X] T053 [US2] Create useTasks hook for fetching and managing tasks in frontend/hooks/use-tasks.ts
- [X] T054 [US2] Create task skeleton loading component in frontend/components/tasks/task-skeleton.tsx
- [X] T055 [US2] Create empty state component for zero tasks in frontend/components/tasks/empty-state.tsx
- [X] T056 [US2] Create task item component displaying title, checkbox, date in frontend/components/tasks/task-item.tsx
- [X] T057 [US2] Create task list container component in frontend/components/tasks/task-list.tsx
- [X] T058 [US2] Create header component with navigation and logout in frontend/components/layout/header.tsx
- [X] T059 [US2] Create tasks page layout with header in frontend/app/tasks/layout.tsx
- [X] T060 [US2] Create tasks dashboard page at /tasks in frontend/app/tasks/page.tsx
- [X] T061 [US2] Implement loading skeleton while fetching tasks from API
- [X] T062 [US2] Implement error state with retry button for failed API calls
- [X] T063 [US2] Display "No tasks yet" empty state with prominent Add Task button
- [X] T064 [US2] Style task cards with proper spacing and visual hierarchy

**Checkpoint**: Authenticated users can view their task dashboard with loading/error/empty states

---

## Phase 5: User Story 3 - Create New Task (Priority: P1) MVP

**Goal**: Allow users to quickly add new tasks via modal dialog

**Independent Test**: Click "Add Task" button, enter task title, submit form, verify new task appears in list immediately with success toast

### Implementation for User Story 3

- [X] T065 [US3] Create task form component with title input and validation in frontend/components/tasks/task-form.tsx
- [X] T066 [US3] Create task creation dialog component in frontend/components/tasks/create-task-dialog.tsx
- [X] T067 [US3] Add character counter showing remaining characters (max 500)
- [X] T068 [US3] Implement form validation preventing empty or whitespace-only titles
- [X] T069 [US3] Connect task form to API client POST /api/{user_id}/tasks
- [X] T070 [US3] Add loading state on submit button during API call ("Creating...")
- [X] T071 [US3] Disable submit button during API call to prevent duplicate submissions
- [X] T072 [US3] Show success toast "Task created successfully" on creation
- [X] T073 [US3] Clear form and close dialog on successful creation
- [X] T074 [US3] Show error toast and keep form open on API failure
- [X] T075 [US3] Refresh task list after successful task creation
- [X] T076 [US3] Add "Add Task" button to dashboard header and empty state

**Checkpoint**: Users can create tasks with validation and immediate feedback

---

## Phase 6: User Story 4 - Update Existing Task (Priority: P2)

**Goal**: Allow users to edit task titles inline or via modal

**Independent Test**: Click edit button on task, modify title, save changes, verify updated title displays immediately with success toast

### Implementation for User Story 4

- [X] T077 [US4] Create task edit form component with pre-filled title in frontend/components/tasks/edit-task-form.tsx
- [X] T078 [US4] Create edit task dialog component in frontend/components/tasks/edit-task-dialog.tsx
- [X] T079 [US4] Add edit button to task item actions
- [X] T080 [US4] Pre-fill edit form with current task title
- [X] T081 [US4] Auto-focus input field when edit form opens
- [X] T082 [US4] Implement validation preventing empty titles
- [X] T083 [US4] Connect edit form to API client PUT /api/{user_id}/tasks/{task_id}
- [X] T084 [US4] Add loading state during save operation
- [X] T085 [US4] Implement cancel button to exit edit mode without saving
- [X] T086 [US4] Show success toast on successful update
- [X] T087 [US4] Show error toast and remain in edit mode on API failure
- [X] T088 [US4] Update task in list immediately after successful save

**Checkpoint**: Users can edit task titles with validation and proper feedback

---

## Phase 7: User Story 5 - Mark Task as Complete/Incomplete (Priority: P2)

**Goal**: Toggle task completion status with single click

**Independent Test**: Click checkbox on incomplete task, verify checkmark appears and text shows strikethrough; click again to mark incomplete

### Implementation for User Story 5

- [X] T089 [US5] Create task checkbox component with loading state in frontend/components/tasks/task-checkbox.tsx
- [X] T090 [US5] Implement visual feedback for completed tasks (strikethrough, muted color)
- [X] T091 [US5] Connect checkbox to API client PATCH /api/{user_id}/tasks/{task_id}/complete
- [X] T092 [US5] Show loading spinner on checkbox during API call
- [X] T093 [US5] Disable checkbox during API call to prevent rapid clicks
- [X] T094 [US5] Show success toast "Task marked complete" or "Task marked incomplete"
- [X] T095 [US5] Revert checkbox state and show error toast on API failure
- [X] T096 [US5] Update task item styling based on is_completed status

**Checkpoint**: Users can toggle task completion with immediate visual feedback

---

## Phase 8: User Story 8 - Responsive Mobile Experience (Priority: P2)

**Goal**: Optimize UI for mobile and tablet devices

**Independent Test**: Access app on mobile device or DevTools mobile view, verify all features work with touch, layouts adapt to screen size

### Implementation for User Story 8

- [X] T097 [US8] Create mobile navigation component with hamburger menu in frontend/components/layout/mobile-nav.tsx
- [X] T098 [US8] Implement mobile-first responsive styles for task cards (full-width on mobile)
- [X] T099 [US8] Ensure all buttons have minimum 44x44px touch targets
- [X] T100 [US8] Implement responsive grid: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)
- [X] T101 [US8] Optimize dialogs for mobile viewport (full-screen on small screens)
- [X] T102 [US8] Prevent horizontal scrolling on all screen sizes
- [X] T103 [US8] Test and fix keyboard visibility issues on mobile form inputs
- [X] T104 [US8] Add responsive header that collapses to hamburger menu on mobile

**Checkpoint**: App is fully functional and touch-optimized on mobile devices

---

## Phase 9: User Story 6 - Delete Task (Priority: P3)

**Goal**: Allow users to permanently remove tasks with confirmation

**Independent Test**: Click delete button on task, confirm in dialog, verify task removed from list with success toast

### Implementation for User Story 6

- [X] T105 [US6] Create delete confirmation dialog component in frontend/components/tasks/delete-task-dialog.tsx
- [X] T106 [US6] Add delete button to task item actions
- [X] T107 [US6] Implement confirmation dialog with "Are you sure?" message
- [X] T108 [US6] Provide cancel option to abort deletion
- [X] T109 [US6] Connect delete to API client DELETE /api/{user_id}/tasks/{task_id}
- [X] T110 [US6] Add loading state during deletion
- [X] T111 [US6] Remove task from list with fade-out animation on success
- [X] T112 [US6] Show success toast "Task deleted successfully"
- [X] T113 [US6] Show error toast and keep task in list on API failure

**Checkpoint**: Users can delete tasks with confirmation to prevent accidents

---

## Phase 10: User Story 7 - View Task Details (Priority: P3)

**Goal**: Provide dedicated detail page for individual tasks

**Independent Test**: Click on task card, navigate to /tasks/[id], verify full task details display with edit/complete/delete actions

### Implementation for User Story 7

- [X] T114 [US7] Create task detail component displaying full information in frontend/components/tasks/task-detail.tsx
- [X] T115 [US7] Create task detail page with async params in frontend/app/tasks/[id]/page.tsx
- [X] T116 [US7] Fetch single task from API GET /api/{user_id}/tasks/{task_id}
- [X] T117 [US7] Display task title, completion status, created_at, updated_at
- [X] T118 [US7] Add "Back to Tasks" navigation button
- [X] T119 [US7] Include Edit, Complete, Delete action buttons on detail page
- [X] T120 [US7] Show skeleton loader while fetching task details
- [X] T121 [US7] Handle 404 for non-existent or unauthorized tasks
- [X] T122 [US7] Create custom 404 page for task not found in frontend/app/tasks/[id]/not-found.tsx
- [X] T123 [US7] Make task title/card clickable to navigate to detail page from dashboard

**Checkpoint**: Users can view and manage individual tasks from dedicated detail page

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [X] T124 Create theme toggle component for dark/light mode in frontend/components/layout/theme-toggle.tsx
- [X] T125 [P] Add theme toggle to header navigation
- [X] T126 Implement proper focus management and keyboard navigation
- [X] T127 [P] Add ARIA labels for accessibility compliance
- [X] T128 Ensure color contrast meets WCAG 2.1 AA standards
- [X] T129 [P] Add hover effects and transitions to interactive elements
- [X] T130 Create home page with redirect logic in frontend/app/page.tsx
- [ ] T131 [P] Create README.md with setup and usage instructions in frontend/README.md
- [ ] T132 Run Lighthouse audit and fix any issues
- [X] T133 Final review of all toast messages for consistency
- [X] T134 Verify all loading states match final content dimensions (zero CLS)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-10)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Start After |
|-------|----------|--------------|-----------------|
| US1: Authentication | P1 | None | Phase 2 complete |
| US2: View Dashboard | P1 | US1 (auth required) | US1 complete |
| US3: Create Task | P1 | US2 (needs dashboard) | US2 complete |
| US4: Update Task | P2 | US2 (needs task item) | US2 complete |
| US5: Toggle Complete | P2 | US2 (needs task item) | US2 complete |
| US8: Responsive | P2 | US2 (needs components) | US2 complete |
| US6: Delete Task | P3 | US2 (needs task item) | US2 complete |
| US7: Task Details | P3 | US2 (needs task list) | US2 complete |

### Parallel Opportunities per Phase

**Phase 1 (Setup)**: T003, T004, T005, T006 can run in parallel
**Phase 2 (Foundational)**: T012-T014, T024-T032, T036-T037 can run in parallel
**Phase 8 (Responsive)**: Most tasks can run in parallel with minor dependencies
**Phase 11 (Polish)**: T125, T127, T129, T131 can run in parallel

---

## Parallel Example: User Stories 4, 5, 6 (After US2)

Once User Story 2 (View Dashboard) is complete, these stories can be developed in parallel:

```bash
# Developer A: User Story 4 (Update Task)
Task: "Create task edit form component in frontend/components/tasks/edit-task-form.tsx"
Task: "Create edit task dialog component in frontend/components/tasks/edit-task-dialog.tsx"

# Developer B: User Story 5 (Toggle Complete)
Task: "Create task checkbox component in frontend/components/tasks/task-checkbox.tsx"
Task: "Implement visual feedback for completed tasks"

# Developer C: User Story 6 (Delete Task)
Task: "Create delete confirmation dialog in frontend/components/tasks/delete-task-dialog.tsx"
Task: "Add delete button to task item actions"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (View Dashboard)
5. Complete Phase 5: User Story 3 (Create Task)
6. **STOP and VALIDATE**: Test auth + view + create independently
7. Deploy/demo MVP with basic task creation

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Auth) → Test independently → Users can sign up/in
3. Add US2 (Dashboard) → Test independently → Users can view tasks
4. Add US3 (Create) → Test independently → Deploy MVP!
5. Add US4 (Update) → Test independently → Users can edit
6. Add US5 (Toggle) → Test independently → Users can complete
7. Add US6 (Delete) → Test independently → Users can delete
8. Add US7 (Details) → Test independently → Full CRUD complete
9. Add US8 (Responsive) → Test independently → Mobile-ready
10. Polish → Production-ready!

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 134 |
| **Setup Phase** | 10 tasks |
| **Foundational Phase** | 27 tasks |
| **US1: Authentication** | 15 tasks |
| **US2: View Dashboard** | 12 tasks |
| **US3: Create Task** | 12 tasks |
| **US4: Update Task** | 12 tasks |
| **US5: Toggle Complete** | 8 tasks |
| **US8: Responsive** | 8 tasks |
| **US6: Delete Task** | 9 tasks |
| **US7: Task Details** | 10 tasks |
| **Polish Phase** | 11 tasks |
| **Parallel Opportunities** | 26 tasks marked [P] |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks in same phase
- [US#] label maps task to specific user story for traceability
- Each user story is independently completable and testable after dependencies met
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP scope: Setup + Foundational + US1 + US2 + US3 (52 tasks)
