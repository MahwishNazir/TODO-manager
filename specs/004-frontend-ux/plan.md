# Implementation Plan: Frontend Application & UX (Production-Ready)

**Branch**: `004-frontend-ux` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/004-frontend-ux/spec.md`

## Summary

Build a production-ready Next.js 16 frontend application for the multi-user Todo system with full JWT authentication, all 5 CRUD operations, and responsive mobile-first design. The frontend integrates with existing FastAPI backend REST endpoints (Phase II Steps 1 & 2), uses Better Auth for JWT token management with shared secret validation, and provides an intuitive shadcn/ui component-based interface styled with Tailwind CSS. This completes Phase II Step 3, delivering a fully functional web-based task management system with authentication, user isolation, and professional UX.

## Technical Context

**Language/Version**: TypeScript 5+, JavaScript ES2020+
**Primary Dependencies**: Next.js 16+ (App Router), React 19+, Better Auth (JWT), shadcn/ui, Tailwind CSS 4+, React Hook Form, Zod, Sonner
**Storage**: HttpOnly cookies (JWT tokens), LocalStorage (theme preference)
**Testing**: Jest + React Testing Library (frontend unit tests), Playwright (E2E tests - future)
**Target Platform**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+), responsive viewports (320px - 1920px)
**Project Type**: Web application (frontend/backend separation)
**Performance Goals**:
- Initial page load: < 2s on broadband
- API response with UI update: < 500ms
- Interaction feedback: < 100ms perceived latency
- Lighthouse score: ≥ 90 (Performance, Accessibility, Best Practices)
**Constraints**:
- No backend API changes (reuse existing 6 endpoints)
- JWT authentication required for all task operations
- User isolation enforced (user_id in URL must match JWT user_id)
- HTTPS in production, HTTP acceptable for local development
- No offline mode or service worker in Phase II Step 3
**Scale/Scope**:
- MVP: Single-user task list (< 1000 tasks per user)
- 5 CRUD operations (Create, Read, Update, Delete, Toggle Complete)
- 4 pages (/signup, /signin, /tasks, /tasks/[id])
- Responsive design (3 breakpoints: mobile, tablet, desktop)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Phased Development Approach (Phase II Step 3)**:
- Builds on Phase II Steps 1 (REST API) and 2 (JWT Auth)
- All backend functionality from previous steps preserved
- Frontend implements Basic tier features (5 CRUD operations) first
- Data structures match backend TaskResponse schema
- Fully tested and verified before Phase III

✅ **Spec-Driven Development**:
- Specification: `specs/004-frontend-ux/spec.md` (approved)
- Planning: This file (`plan.md`) with architecture decisions
- Tasks: Will be generated via `/sp.tasks` after plan approval
- PHRs created for all user interactions
- ADRs required for significant decisions (JWT storage, form patterns, state management)

✅ **Test-First Development**:
- Component unit tests with Jest + React Testing Library
- Integration tests for API client with mocked endpoints
- E2E tests for critical user workflows (signup, login, task CRUD)
- Target: ≥ 80% code coverage for components and services
- TDD cycle: Write test → User approval → Red → Green → Refactor

✅ **Separation of Concerns**:
- Frontend in `frontend/` directory (independent deployment)
- Backend in `backend/` directory (already implemented)
- API contracts defined in `specs/004-frontend-ux/contracts/` with TypeScript interfaces
- Clear interface boundaries: REST API with JSON payloads
- No direct database access from frontend (API only)

✅ **Feature Tiering and Progressive Enhancement**:
- **Basic Level** (Phase II Step 3): All 5 CRUD operations
  - Add Task
  - Delete Task
  - Update Task (title only)
  - View Task List
  - Mark as Complete/Incomplete
- **Intermediate Level** (Future - Phase III+): Out of scope for Step 3
- **Advanced Level** (Future - Phase III+): Out of scope for Step 3

✅ **Technology Stack Discipline (Phase II)**:
- Frontend: Next.js 16+ (TypeScript, React 19+) ✅
- Backend: FastAPI (Python 3.10+) - already implemented ✅
- ORM: SQLModel - already implemented ✅
- Database: Neon DB (PostgreSQL) - already implemented ✅
- Authentication: Better Auth + JWT with shared secret ✅
- Testing: Jest/Vitest (frontend) ✅

✅ **Data Integrity and Migration**:
- No data migration needed (frontend reads from existing backend)
- Backend preserves all Phase I data structures
- JWT tokens secure user data access
- User isolation enforced at API and service layers
- Backup strategy handled by backend/database layer

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-ux/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (Next.js 16, Better Auth, shadcn/ui, Tailwind)
├── data-model.md        # Phase 1 output (User Session, Task UI Model, Form State, API Client)
├── quickstart.md        # Phase 1 output (Environment setup, installation, dev server)
├── contracts/           # Phase 1 output (API contracts with TypeScript interfaces)
│   ├── auth.ts          # Authentication endpoints and session types
│   ├── tasks.ts         # Task CRUD endpoints and response types
│   └── errors.ts        # Error response types and status codes
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/                      # Next.js 16 App Router
│   ├── (auth)/               # Route group for auth pages
│   │   ├── signin/
│   │   │   └── page.tsx      # Sign in page (Better Auth integration)
│   │   └── signup/
│   │       └── page.tsx      # Sign up page (Better Auth integration)
│   ├── tasks/                # Protected task pages
│   │   ├── [id]/
│   │   │   └── page.tsx      # Task detail page (Server Component with async params)
│   │   └── page.tsx          # Task dashboard (Server Component with async params)
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts  # Better Auth route handler (catchall)
│   ├── layout.tsx            # Root layout (providers, theme, fonts)
│   ├── page.tsx              # Home/landing page (redirects to /tasks if authenticated)
│   ├── not-found.tsx         # Custom 404 page
│   ├── error.tsx             # Global error boundary
│   ├── loading.tsx           # Global loading state
│   └── globals.css           # Global styles (Tailwind imports, CSS variables)
│
├── components/               # React components
│   ├── ui/                   # shadcn/ui components (installed via CLI)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── checkbox.tsx
│   │   ├── dialog.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── skeleton.tsx
│   │   ├── toast.tsx
│   │   └── ... (other shadcn components)
│   ├── tasks/                # Task-specific components
│   │   ├── task-list.tsx     # Task list container (Client Component)
│   │   ├── task-item.tsx     # Individual task card (Client Component)
│   │   ├── task-form.tsx     # Task creation/edit form (Client Component)
│   │   ├── task-actions.tsx  # Edit/Delete/Complete buttons (Client Component)
│   │   ├── task-skeleton.tsx # Loading skeleton for tasks
│   │   └── empty-state.tsx   # Empty state when no tasks
│   ├── auth/                 # Auth-specific components
│   │   ├── signin-form.tsx   # Sign in form (Client Component)
│   │   ├── signup-form.tsx   # Sign up form (Client Component)
│   │   └── auth-guard.tsx    # Protected route wrapper (Client Component)
│   ├── layout/               # Layout components
│   │   ├── header.tsx        # App header with navigation (Client Component)
│   │   ├── sidebar.tsx       # Desktop sidebar navigation (Client Component)
│   │   ├── mobile-nav.tsx    # Mobile hamburger menu (Client Component)
│   │   └── theme-toggle.tsx  # Dark/light mode toggle (Client Component)
│   └── providers/            # Context providers
│       ├── auth-provider.tsx # Better Auth session provider (Client Component)
│       └── theme-provider.tsx # next-themes provider (Client Component)
│
├── lib/                      # Utility libraries
│   ├── auth.ts               # Better Auth server configuration
│   ├── auth-client.ts        # Better Auth client utilities
│   ├── api-client.ts         # API client with JWT injection
│   ├── utils.ts              # shadcn/ui utilities (cn function)
│   ├── validations.ts        # Zod schemas for form validation
│   └── constants.ts          # App constants (API URLs, limits)
│
├── types/                    # TypeScript type definitions
│   ├── task.ts               # Task types (matching backend TaskResponse)
│   ├── user.ts               # User session types
│   ├── api.ts                # API request/response types
│   └── form.ts               # Form state types
│
├── hooks/                    # Custom React hooks
│   ├── use-tasks.ts          # Task data fetching and mutations
│   ├── use-auth.ts           # Auth session management
│   └── use-toast.ts          # Toast notification wrapper
│
├── public/                   # Static assets
│   ├── favicon.ico
│   └── images/
│
├── tests/                    # Frontend tests
│   ├── unit/                 # Component unit tests
│   │   ├── components/
│   │   │   ├── tasks/
│   │   │   │   ├── task-list.test.tsx
│   │   │   │   ├── task-item.test.tsx
│   │   │   │   └── task-form.test.tsx
│   │   │   └── auth/
│   │   │       ├── signin-form.test.tsx
│   │   │       └── signup-form.test.tsx
│   │   └── lib/
│   │       ├── api-client.test.ts
│   │       └── validations.test.ts
│   ├── integration/          # Integration tests
│   │   ├── auth-flow.test.tsx
│   │   └── task-crud.test.tsx
│   └── e2e/                  # End-to-end tests (future)
│       └── task-workflow.spec.ts
│
├── .env.local                # Environment variables (not in git)
├── .env.example              # Environment variable template
├── components.json           # shadcn/ui configuration
├── next.config.ts            # Next.js configuration (TypeScript)
├── tailwind.config.ts        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
├── postcss.config.js         # PostCSS configuration
├── package.json              # Node.js dependencies
├── package-lock.json         # Locked dependency versions
├── jest.config.js            # Jest testing configuration
├── .eslintrc.json            # ESLint configuration
└── README.md                 # Frontend documentation
```

**Structure Decision**: Selected **Option 2: Web application** structure with separate `frontend/` and `backend/` directories. Frontend uses Next.js 16 App Router with TypeScript for type-safe development. Backend already implemented in Phase II Steps 1 & 2. Clear separation enables independent deployment, parallel development, and technology-specific tooling.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution requirements satisfied:
- Phase II Step 3 follows sequential phased development
- Spec-driven workflow followed (spec → plan → tasks → implementation)
- TDD will be enforced during implementation
- Frontend/backend separation maintained
- Basic tier features implemented first
- Technology stack matches Phase II requirements

## Phase 0: Research

**Objective**: Investigate Next.js 16 App Router patterns, Better Auth JWT integration with shared secrets, shadcn/ui component library, Tailwind CSS responsive design, form validation with React Hook Form + Zod, and API client architecture.

**Output**: `research.md` with findings on:
1. Next.js 16 App Router (Server Components vs Client Components, async params)
2. Better Auth configuration (JWT plugin, shared secret with FastAPI)
3. shadcn/ui component selection (Button, Card, Form, Dialog, Checkbox, Input, Label, Toast)
4. Tailwind CSS dual-theme system (LinkedIn Wrapped light, Regulatis AI dark)
5. Form validation patterns (React Hook Form + Zod schemas)
6. API client design (JWT token injection, error handling, retry logic)
7. Toast notifications (Sonner integration)
8. Theme management (next-themes for dark/light mode persistence)

**Success Criteria**:
- Research document covers all technical decisions needed for implementation
- Examples provided for critical patterns (async params, JWT auth, form validation)
- Component library selections justified based on feature requirements
- API integration patterns defined for all 6 backend endpoints

## Phase 1: Design

**Objective**: Define data models, API contracts, and component architecture for the frontend application.

**Output 1**: `data-model.md` defining:
- **User Session Model**: JWT token structure, user_id, email, expiration
- **Task UI Model**: Frontend representation matching backend TaskResponse (id, user_id, title, is_completed, created_at, updated_at)
- **Form State Models**: CreateTaskForm, EditTaskForm with validation rules
- **API Response Models**: TaskResponse, TaskListResponse, ErrorResponse with TypeScript interfaces
- **Loading States**: TasksLoading, TasksError, TasksEmpty with UI state management
- **Theme State**: Light/dark mode preference with persistence strategy

**Output 2**: `contracts/` directory with TypeScript interfaces:
- **auth.ts**: Authentication endpoints (signup, signin, logout), session types, error types
- **tasks.ts**: All 6 task endpoints with request/response types
  - POST /api/{user_id}/tasks → TaskCreate request, TaskResponse response
  - GET /api/{user_id}/tasks → TaskListResponse response
  - GET /api/{user_id}/tasks/{task_id} → TaskResponse response
  - PUT /api/{user_id}/tasks/{task_id} → TaskUpdate request, TaskResponse response
  - PATCH /api/{user_id}/tasks/{task_id}/complete → TaskResponse response
  - DELETE /api/{user_id}/tasks/{task_id} → 204 No Content response
- **errors.ts**: Error response types (ValidationError, AuthError, NotFoundError, ServerError) with status codes

**Output 3**: `quickstart.md` with:
- Environment setup instructions (.env.local configuration)
- Installation steps (Node.js version, npm install)
- Development server startup (npm run dev)
- Testing authentication flow (signup → signin → tasks)
- Common troubleshooting (CORS errors, JWT expiration, API connection issues)

**Success Criteria**:
- All data models match backend schemas exactly
- API contracts include request/response types for all endpoints
- TypeScript interfaces provide type safety for API calls
- Quickstart guide enables new developers to run frontend in < 10 minutes
- Component architecture supports all 8 user stories from spec

## Phase 2: Task Breakdown

**Objective**: Generate detailed, testable tasks for implementing the frontend application.

**Output**: `tasks.md` via `/sp.tasks` command (NOT created during `/sp.plan`)

**Task Structure** (preview of expected tasks):
1. **Setup & Configuration** (T001-T005)
   - T001: Initialize Next.js 16 project with TypeScript and App Router
   - T002: Install and configure shadcn/ui with Tailwind CSS
   - T003: Set up Better Auth with JWT plugin and shared secret
   - T004: Configure environment variables and .env.example
   - T005: Create root layout with theme provider and global styles

2. **Authentication Pages** (T006-T010)
   - T006: Implement signup form with email/password validation
   - T007: Implement signin form with Better Auth integration
   - T008: Create auth route handler for Better Auth catchall
   - T009: Implement protected route middleware for /tasks pages
   - T010: Add logout functionality and session management

3. **API Client Layer** (T011-T015)
   - T011: Create API client with JWT token injection
   - T012: Implement task API methods (create, read, update, delete, toggle)
   - T013: Add error handling and retry logic
   - T014: Create TypeScript interfaces for API contracts
   - T015: Add API client tests with mocked responses

4. **Task Dashboard** (T016-T020)
   - T016: Create /tasks page layout with header and sidebar
   - T017: Implement task list component with loading states
   - T018: Create task item component with completion checkbox
   - T019: Add empty state for zero tasks
   - T020: Implement task filtering and display logic

5. **Task Creation** (T021-T025)
   - T021: Create task creation form with React Hook Form + Zod
   - T022: Implement task creation modal dialog
   - T023: Add form validation and error messages
   - T024: Connect form to API client (POST /api/{user_id}/tasks)
   - T025: Add success toast and list refresh on creation

6. **Task Update** (T026-T030)
   - T026: Create task edit form (inline or modal)
   - T027: Pre-fill form with current task title
   - T028: Implement save and cancel actions
   - T029: Connect to API client (PUT /api/{user_id}/tasks/{task_id})
   - T030: Add success/error feedback with toasts

7. **Task Completion Toggle** (T031-T035)
   - T031: Implement checkbox component for completion status
   - T032: Add visual feedback (strikethrough, checkmark)
   - T033: Connect to API client (PATCH /api/{user_id}/tasks/{task_id}/complete)
   - T034: Add loading state during API call
   - T035: Handle toggle errors with state revert

8. **Task Deletion** (T036-T040)
   - T036: Create delete confirmation dialog
   - T037: Implement delete button with confirmation flow
   - T038: Connect to API client (DELETE /api/{user_id}/tasks/{task_id})
   - T039: Add fade-out animation on successful deletion
   - T040: Show error message if deletion fails

9. **Task Detail Page** (T041-T045)
   - T041: Create /tasks/[id] page with async params (Next.js 16)
   - T042: Fetch task data from API (GET /api/{user_id}/tasks/{task_id})
   - T043: Display task details with edit/delete/complete actions
   - T044: Handle 404 for non-existent or unauthorized tasks
   - T045: Add "Back to Tasks" navigation

10. **Responsive Design** (T046-T050)
    - T046: Implement mobile layout with hamburger menu
    - T047: Create tablet layout with two-column card grid
    - T048: Optimize desktop layout with sidebar navigation
    - T049: Ensure touch targets meet 44x44px minimum
    - T050: Test all features on mobile/tablet/desktop viewports

11. **Theme & UX Polish** (T051-T055)
    - T051: Implement dark/light theme toggle with next-themes
    - T052: Configure dual-theme colors (LinkedIn Wrapped light, Regulatis AI dark)
    - T053: Add hover effects and transitions to interactive elements
    - T054: Implement toast notifications with Sonner
    - T055: Add loading skeletons for async operations

12. **Testing & Documentation** (T056-T060)
    - T056: Write component unit tests (task-list, task-item, task-form)
    - T057: Write integration tests for auth flow
    - T058: Write integration tests for task CRUD operations
    - T059: Update README.md with setup and usage instructions
    - T060: Verify ≥ 80% code coverage and all tests passing

**Success Criteria**:
- Each task has clear acceptance criteria
- Tasks are ordered with dependencies resolved
- Each task is independently testable
- Task breakdown covers all functional requirements from spec

## Architectural Decisions

### ADR-001: JWT Token Storage Strategy

**Context**: Need to store JWT tokens securely on the client side for authenticated API requests.

**Decision**: Use **HttpOnly cookies** for JWT token storage.

**Rationale**:
- **Security**: HttpOnly cookies not accessible via JavaScript, preventing XSS attacks
- **Automatic handling**: Cookies sent automatically with API requests (no manual header injection)
- **Better Auth support**: Better Auth has built-in HttpOnly cookie support
- **Cross-domain**: Works with CORS when configured properly

**Alternatives Rejected**:
- **localStorage**: More vulnerable to XSS attacks, requires manual token injection in API calls
- **sessionStorage**: Same XSS vulnerability, data lost on tab close
- **In-memory only**: Lost on page refresh, poor UX

**Consequences**:
- Positive: Enhanced security, simpler implementation, better UX
- Negative: Requires backend CORS configuration with credentials support
- Trade-off: Cannot access token from JavaScript (intentional security feature)

---

### ADR-002: Task Creation UI Pattern

**Context**: Need to decide between modal dialog vs inline form for task creation.

**Decision**: Use **modal dialog** for task creation form.

**Rationale**:
- **Focus**: Modal provides distraction-free environment for task input
- **Cleaner UI**: Keeps dashboard uncluttered when not creating tasks
- **Better UX**: Clear entry/exit points (open modal, submit/cancel to close)
- **Mobile-friendly**: Full-screen modal works well on small screens
- **shadcn/ui support**: Dialog component built-in and accessible

**Alternatives Rejected**:
- **Inline form at top of list**: Adds visual clutter, always visible, harder to focus
- **Slide-out panel**: More complex, less mobile-friendly
- **Full-page form**: Overkill for simple title input

**Consequences**:
- Positive: Clean UI, better focus, mobile-friendly, accessible
- Negative: Extra click to open modal (vs inline always visible)
- Trade-off: One additional interaction step for faster users

---

### ADR-003: Server State Management Strategy

**Context**: Need to manage server state (tasks data) and decide on caching/revalidation strategy.

**Decision**: Use **plain fetch with React state** (no SWR or React Query for MVP).

**Rationale**:
- **Simplicity**: Fewer dependencies, easier to understand and debug
- **MVP focus**: Phase II Step 3 prioritizes feature completeness over optimization
- **Sufficient for scale**: < 1000 tasks per user doesn't require advanced caching
- **Next.js integration**: Native fetch with Next.js App Router handles basic caching

**Alternatives Rejected**:
- **SWR**: Adds dependency, overkill for MVP, can be added later if needed
- **React Query**: More powerful but adds complexity, deferred to Phase III
- **Redux**: Too heavy for simple task state, unnecessary for MVP

**Consequences**:
- Positive: Simpler implementation, fewer dependencies, easier debugging
- Negative: No automatic background revalidation, manual cache invalidation
- Trade-off: Less sophisticated caching for simpler codebase (can upgrade later)

---

### ADR-004: Optimistic UI Updates

**Context**: Decide whether to update UI immediately before API response (optimistic) or wait for confirmation.

**Decision**: **No optimistic updates** for MVP (wait for API confirmation).

**Rationale**:
- **Simpler state management**: No rollback logic needed for failed requests
- **MVP focus**: Prioritize correctness over perceived performance
- **Reliable feedback**: Users see true state, not speculative state
- **Easier debugging**: Fewer edge cases with failed optimistic updates

**Alternatives Rejected**:
- **Full optimistic updates**: More complex, requires rollback on error, can confuse users if rolled back
- **Partial optimistic (read-only operations)**: Inconsistent UX, still adds complexity

**Consequences**:
- Positive: Simpler implementation, fewer edge cases, reliable user feedback
- Negative: Slightly slower perceived performance (wait for API round-trip)
- Trade-off: Sacrifice ~200ms perceived speed for implementation simplicity

---

### ADR-005: Component Organization Pattern

**Context**: Need to decide on component organization strategy (atomic design vs feature-based).

**Decision**: Use **feature-based** component organization.

**Rationale**:
- **Clearer structure**: Components grouped by feature (tasks, auth, layout)
- **Easier navigation**: Developers find related components together
- **Better scalability**: Adding new features doesn't mix with existing feature components
- **Matches domain**: Component organization mirrors user features

**Alternatives Rejected**:
- **Atomic design**: Over-engineered for MVP, hard to categorize some components
- **Flat structure**: All components in one folder, hard to navigate at scale
- **Page-based**: Duplicates shared components across pages

**Consequences**:
- Positive: Clear organization, easier to find components, scales with features
- Negative: Some components could fit multiple categories (resolved by choosing primary feature)
- Trade-off: Slightly more directory nesting for better long-term organization

---

### ADR-006: Form Validation Strategy

**Context**: Need client-side validation for task forms (title length, required fields).

**Decision**: Use **React Hook Form + Zod** for form validation.

**Rationale**:
- **Type-safe**: Zod provides TypeScript types from schemas
- **Reusable**: Validation schemas shared across forms
- **DX**: React Hook Form has excellent developer experience
- **Performance**: Efficient re-rendering with fine-grained control
- **Better Auth compatibility**: Works well with Better Auth forms

**Alternatives Rejected**:
- **Manual validation**: Error-prone, hard to maintain, no type safety
- **Formik**: More verbose, less TypeScript-friendly than React Hook Form
- **Native HTML validation**: Limited control, inconsistent across browsers

**Consequences**:
- Positive: Type-safe validation, excellent DX, reusable schemas
- Negative: Additional dependencies (React Hook Form, Zod)
- Trade-off: Two extra dependencies for robust, type-safe validation

---

### ADR-007: Error Handling Pattern

**Context**: Need consistent error handling across API calls and user feedback.

**Decision**: Use **try-catch with toast notifications** for error feedback.

**Rationale**:
- **User-friendly**: Toast notifications are non-intrusive and clear
- **Consistent UX**: Same error pattern across all operations
- **Accessible**: Sonner toast library is screen-reader friendly
- **Actionable**: Can include retry buttons in toasts

**Alternatives Rejected**:
- **Inline error messages only**: Less noticeable, clutters UI
- **Error boundary only**: Too coarse-grained, catches unexpected errors
- **Alert dialogs**: More intrusive, requires dismissal, poor UX

**Consequences**:
- Positive: Consistent, user-friendly error feedback, non-blocking
- Negative: Errors disappear after timeout (intentional for transient errors)
- Trade-off: Transient toasts for better UX (can add error log panel later)

---

### ADR-008: Responsive Breakpoint Strategy

**Context**: Need to define responsive design breakpoints for mobile, tablet, and desktop.

**Decision**: Use **Tailwind CSS default breakpoints** with mobile-first approach.

**Rationale**:
- **Standard breakpoints**: Tailwind defaults (sm: 640px, md: 768px, lg: 1024px, xl: 1280px) match common devices
- **Mobile-first**: Design for smallest screen, enhance for larger screens
- **Less code**: Fewer breakpoint overrides, simpler CSS
- **Best practice**: Industry-standard approach

**Breakpoints**:
- **Mobile**: < 768px (default, no prefix)
- **Tablet**: 768px - 1023px (md: prefix)
- **Desktop**: ≥ 1024px (lg: prefix)

**Alternatives Rejected**:
- **Custom breakpoints**: Unnecessary, Tailwind defaults work well
- **Desktop-first**: More code, harder to simplify, poor mobile UX
- **Single responsive layout**: Doesn't optimize for each device type

**Consequences**:
- Positive: Standard breakpoints, mobile-first best practice, less CSS
- Negative: May need custom breakpoints later (rare, can be added)
- Trade-off: Standard breakpoints for simpler implementation

---

## Risk Analysis

### Risk 1: JWT Token Expiration During Session

**Probability**: Medium | **Impact**: High | **Mitigation**:
- Implement automatic token refresh logic (Better Auth refresh tokens)
- Detect 401 responses and redirect to signin with "Session expired" message
- Store intended destination in session for post-login redirect
- Show countdown warning before token expires (future enhancement)

---

### Risk 2: API Endpoint Changes or Downtime

**Probability**: Low | **Impact**: High | **Mitigation**:
- Use API client abstraction layer (easy to swap endpoints)
- Implement retry logic with exponential backoff
- Show clear error messages with retry buttons
- Add backend health check endpoint (future enhancement)
- Test against mock API during development

---

### Risk 3: Browser Compatibility Issues

**Probability**: Medium | **Impact**: Medium | **Mitigation**:
- Target modern browsers only (Chrome 90+, Firefox 88+, Safari 14+)
- Use Next.js transpilation for ES6+ features
- Test on multiple browsers during development
- Include browser version check on landing page (future enhancement)
- Use Progressive Enhancement for advanced features

---

### Risk 4: Mobile Usability Problems

**Probability**: Medium | **Impact**: High | **Mitigation**:
- Follow mobile-first design approach
- Ensure minimum 44x44px touch targets
- Test on real mobile devices (iOS and Android)
- Use responsive design patterns from shadcn/ui
- Implement swipe gestures where appropriate (future enhancement)

---

### Risk 5: CORS Configuration Errors

**Probability**: Medium | **Impact**: High | **Mitigation**:
- Document CORS requirements in backend README
- Include CORS setup in quickstart.md
- Test with frontend/backend on different ports (3000/8000)
- Provide troubleshooting guide for CORS errors
- Verify CORS headers in API responses

---

### Risk 6: Form Validation Bypass

**Probability**: Low | **Impact**: Medium | **Mitigation**:
- Implement client-side validation with Zod (UX)
- Backend validates all inputs (security)
- Test validation with edge cases (empty strings, max length, special characters)
- Document validation rules in contracts/
- Add E2E tests for validation flows

---

### Risk 7: State Management Complexity

**Probability**: Low | **Impact**: Medium | **Mitigation**:
- Keep state management simple with React state (no Redux for MVP)
- Use React Context for global state (auth session, theme)
- Document state flow in data-model.md
- Consider SWR or React Query if complexity grows (Phase III)

---

### Risk 8: Accessibility Compliance Failures

**Probability**: Medium | **Impact**: Medium | **Mitigation**:
- Use shadcn/ui components (built on accessible Radix UI primitives)
- Follow WCAG 2.1 Level AA guidelines
- Test with keyboard navigation only (no mouse)
- Run Lighthouse accessibility audits
- Use semantic HTML elements
- Include ARIA labels where needed

---

## Implementation Phases

### Phase 0: Research (This phase - already completed in this document)
- **Duration**: 1 day
- **Deliverable**: `research.md` with technical findings
- **Key Activities**: Investigate Next.js 16, Better Auth, shadcn/ui, Tailwind CSS patterns

### Phase 1: Design (Next phase)
- **Duration**: 2 days
- **Deliverables**: `data-model.md`, `contracts/`, `quickstart.md`
- **Key Activities**: Define data models, API contracts, component architecture

### Phase 2: Task Breakdown (After design approval)
- **Duration**: 1 day
- **Deliverable**: `tasks.md` via `/sp.tasks` command
- **Key Activities**: Generate testable tasks with acceptance criteria

### Phase 3: Implementation (After task approval)
- **Duration**: 7-10 days
- **Deliverable**: Working frontend application
- **Key Activities**: Execute tasks following TDD workflow (Red-Green-Refactor)

### Phase 4: Testing & Polish (After implementation)
- **Duration**: 2-3 days
- **Deliverable**: Production-ready frontend with ≥ 80% test coverage
- **Key Activities**: Integration tests, E2E tests, accessibility audit, performance optimization

---

## Success Metrics

1. **Functional Completeness**: All 5 CRUD operations working (Create, Read, Update, Delete, Toggle)
2. **Authentication**: Users can signup, signin, and maintain session across pages
3. **User Isolation**: Users only see/modify their own tasks (JWT validation)
4. **Responsiveness**: All features work on mobile (320px), tablet (768px), desktop (1920px)
5. **Performance**: Dashboard loads in < 500ms, interactions feel instant (< 100ms)
6. **Accessibility**: Passes WCAG 2.1 Level AA audit, keyboard navigable
7. **Code Quality**: ≥ 80% test coverage, TypeScript strict mode with no errors
8. **User Experience**: Clear feedback for all actions, intuitive UI, consistent design

---

## Next Steps

1. ✅ **Spec approved**: `specs/004-frontend-ux/spec.md` (completed)
2. ✅ **Plan created**: This file (completed)
3. ⏳ **Create research.md**: Document Next.js 16, Better Auth, shadcn/ui findings
4. ⏳ **Create data-model.md**: Define User Session, Task UI Model, Form State types
5. ⏳ **Create contracts/**: TypeScript interfaces for auth and task API endpoints
6. ⏳ **Create quickstart.md**: Environment setup and installation guide
7. ⏳ **User approval checkpoint**: Review all planning artifacts before task generation
8. ⏳ **Generate tasks.md**: Run `/sp.tasks` command to create task breakdown
9. ⏳ **Implementation**: Execute tasks following TDD workflow

---

**Plan Status**: ✅ Complete - Ready for Phase 0 (Research) → Phase 1 (Design)
