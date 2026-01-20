# Feature Specification: Frontend Application & UX (Production-Ready)

**Feature Branch**: `004-frontend-ux`
**Created**: 2026-01-14
**Status**: Draft
**Input**: User description: "Build a modern, responsive multi-user Todo application UI with all 5 basic CRUD features: Add Task, Delete Task, Update Task, View Task List, and Mark as Complete. Use Next.js 16+ App Router with TypeScript, shadcn/ui components, and Tailwind CSS. Create pages for /signup, /signin, /tasks (protected), and /tasks/[id]. Integrate with existing JWT authentication and REST API endpoints. Focus on stylish, user-friendly UI with responsive mobile-first design."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Onboarding and Authentication (Priority: P1)

New users must be able to create accounts and existing users must be able to log in to access their personalized task management dashboard. This is the gateway to all other features and ensures security from the first interaction.

**Why this priority**: Without user authentication, the multi-user task system cannot function. This story delivers the foundational security mechanism and enables all protected features. Every other user story depends on this capability.

**Independent Test**: Can be fully tested by visiting the app, clicking signup, creating an account with email/password, then logging in and seeing the authenticated dashboard. Delivers immediate value by establishing secure user identity and enabling personalized task management.

**Acceptance Scenarios**:

1. **Given** user visits app for first time, **When** user navigates to /signup page, **Then** user sees attractive signup form with email, password fields and validation messages
2. **Given** user fills valid email and password (8+ characters), **When** user submits signup form, **Then** account is created and user is redirected to /tasks dashboard with welcome message
3. **Given** registered user visits /signin page, **When** user enters correct credentials, **Then** JWT token is issued and user is redirected to /tasks dashboard
4. **Given** user enters incorrect password on /signin, **When** user submits login form, **Then** user sees clear error message "Invalid credentials" without revealing which field is wrong
5. **Given** user is not logged in, **When** user attempts to access /tasks or /tasks/[id], **Then** user is redirected to /signin with message "Please log in to continue"
6. **Given** user is logged in with valid JWT, **When** user navigates between protected pages, **Then** user remains authenticated without re-login until token expires

---

### User Story 2 - View Task Dashboard (Priority: P1)

Authenticated users must be able to view all their tasks in a clean, organized dashboard. The dashboard is the central hub where users understand their workload at a glance and access all task management features.

**Why this priority**: This is the primary interface for task management and delivers immediate value by showing users their task data. Without this view, users cannot interact with their tasks. This story enables users to see the current state of their work.

**Independent Test**: Can be fully tested by logging in, navigating to /tasks, and verifying all user's tasks are displayed with title, completion status, and timestamps. Delivers core value of visualizing task data in an attractive, responsive layout.

**Acceptance Scenarios**:

1. **Given** user is logged in, **When** user navigates to /tasks dashboard, **Then** user sees list of all their tasks with title, completion checkbox, and action buttons
2. **Given** user has no tasks, **When** user visits /tasks dashboard, **Then** user sees empty state with message "No tasks yet" and prominent "Add Task" button
3. **Given** user has 10+ tasks, **When** dashboard loads, **Then** tasks are displayed in cards/list items with proper spacing, scrollable if needed, and loading states during fetch
4. **Given** user is on mobile device, **When** viewing /tasks dashboard, **Then** layout adapts to mobile screen with full-width cards and touch-friendly buttons
5. **Given** tasks are loading from API, **When** user visits /tasks, **Then** user sees skeleton loaders or spinner with "Loading tasks..." message
6. **Given** API returns error (401, 403, 500), **When** dashboard attempts to load tasks, **Then** user sees error message with retry button or redirect to login for auth errors

---

### User Story 3 - Create New Task (Priority: P1)

Users must be able to quickly add new tasks to their list. This is the primary action for getting work into the system and must be intuitive, fast, and accessible from the main dashboard.

**Why this priority**: Task creation is a fundamental CRUD operation and one of the most frequent user actions. Without this, users cannot populate their task list. This story delivers immediate productivity value.

**Independent Test**: Can be fully tested by clicking "Add Task" button, entering a task title, submitting the form, and verifying the new task appears in the list immediately. Delivers core productivity feature independently.

**Acceptance Scenarios**:

1. **Given** user is on /tasks dashboard, **When** user clicks "Add Task" button, **Then** task creation form appears (modal or inline) with title input field and submit button
2. **Given** task form is open, **When** user enters task title (1-500 characters) and submits, **Then** task is created via POST /api/{user_id}/tasks and appears in dashboard immediately with success toast
3. **Given** user submits empty or whitespace-only title, **When** user clicks submit, **Then** form shows validation error "Task title is required" and prevents submission
4. **Given** user enters title over 500 characters, **When** user types, **Then** form shows character counter and validation error "Title must be 500 characters or less"
5. **Given** task creation API fails (network error, 500), **When** user submits form, **Then** user sees error message "Failed to create task. Please try again" with retry button
6. **Given** task is being created, **When** API call is in progress, **Then** submit button shows loading state "Creating..." and is disabled to prevent duplicate submissions

---

### User Story 4 - Update Existing Task (Priority: P2)

Users must be able to edit task titles to correct mistakes or update information. This allows users to maintain accurate task descriptions as their work evolves.

**Why this priority**: Task updates are important for maintaining data accuracy but less critical than viewing and creating tasks. Users can still be productive without editing, but it significantly improves usability. This story enhances core functionality.

**Independent Test**: Can be fully tested by clicking edit button on a task, changing the title, saving, and verifying the updated title appears in the list. Delivers independent value for task maintenance.

**Acceptance Scenarios**:

1. **Given** user sees a task in /tasks dashboard, **When** user clicks "Edit" button, **Then** task title becomes editable (inline or modal) with current title pre-filled
2. **Given** task edit mode is active, **When** user changes title and clicks "Save", **Then** task is updated via PUT /api/{user_id}/tasks/{task_id} and new title displays immediately
3. **Given** user updates task title to empty string, **When** user tries to save, **Then** form shows validation error "Task title cannot be empty" and prevents save
4. **Given** user is editing a task, **When** user clicks "Cancel", **Then** edit mode closes and original title is preserved without API call
5. **Given** task update API fails, **When** user submits edited title, **Then** user sees error toast "Failed to update task" and form remains in edit mode for retry
6. **Given** user clicks edit on task, **When** edit form opens, **Then** input field is focused automatically for immediate typing

---

### User Story 5 - Mark Task as Complete/Incomplete (Priority: P2)

Users must be able to toggle task completion status with a single click. This provides immediate feedback on progress and helps users track what's done versus pending.

**Why this priority**: Completion toggling is a frequent action and core to task management workflow. It's slightly lower priority than create/view since users need tasks in the system first. This story delivers satisfaction of marking work complete.

**Independent Test**: Can be fully tested by clicking the checkbox next to a task, verifying the task updates to completed state with visual indicator (strikethrough/checkmark), then clicking again to mark incomplete. Delivers independent progress tracking feature.

**Acceptance Scenarios**:

1. **Given** user sees uncompleted task with empty checkbox, **When** user clicks checkbox, **Then** task is marked complete via PATCH /api/{user_id}/tasks/{task_id}/complete with visual confirmation (checkmark, strikethrough text)
2. **Given** task is marked complete with checked checkbox, **When** user clicks checkbox again, **Then** task is marked incomplete and visual indicators are removed
3. **Given** completion toggle API call succeeds, **When** task status updates, **Then** checkbox state changes immediately with success toast "Task marked complete" or "Task marked incomplete"
4. **Given** completion toggle API fails, **When** user clicks checkbox, **Then** checkbox reverts to original state and user sees error toast "Failed to update task status"
5. **Given** user toggles task completion, **When** API call is in progress, **Then** checkbox shows loading state (spinner or disabled) to prevent double-clicks
6. **Given** user has mix of complete and incomplete tasks, **When** viewing dashboard, **Then** completed tasks show strikethrough text and muted styling for clear visual distinction

---

### User Story 6 - Delete Task (Priority: P3)

Users must be able to permanently remove tasks they no longer need. This keeps the task list clean and focused on relevant work.

**Why this priority**: Deletion is important for maintenance but lower priority than other CRUD operations. Users can still be productive with tasks they don't delete. This story prevents clutter and maintains clean workspace.

**Independent Test**: Can be fully tested by clicking delete button on a task, confirming deletion in dialog, and verifying task is removed from list. Delivers independent cleanup capability.

**Acceptance Scenarios**:

1. **Given** user sees a task in dashboard, **When** user clicks "Delete" button, **Then** confirmation dialog appears asking "Are you sure you want to delete this task? This cannot be undone."
2. **Given** delete confirmation dialog is open, **When** user clicks "Confirm Delete", **Then** task is deleted via DELETE /api/{user_id}/tasks/{task_id} and removed from list immediately
3. **Given** delete confirmation dialog is open, **When** user clicks "Cancel", **Then** dialog closes and task remains in list without API call
4. **Given** task deletion API succeeds, **When** task is deleted, **Then** task fades out of list with success toast "Task deleted successfully"
5. **Given** task deletion API fails, **When** user confirms delete, **Then** task remains in list and user sees error toast "Failed to delete task. Please try again"
6. **Given** user accidentally clicks delete, **When** confirmation dialog appears, **Then** user has clear escape routes (Cancel button, X close button, click outside dialog) to prevent accidental deletion

---

### User Story 7 - View Task Details (Priority: P3)

Users must be able to view full task information on a dedicated detail page. This provides space for potential future features like descriptions, due dates, and notes.

**Why this priority**: Detail view is lower priority for MVP since current tasks only have title and completion status. However, it establishes routing pattern and prepares for future enhancements. This story sets foundation for richer task data.

**Independent Test**: Can be fully tested by clicking on a task card, navigating to /tasks/[id], and viewing task details with options to edit, mark complete, or delete. Delivers independent detail view that complements list view.

**Acceptance Scenarios**:

1. **Given** user is on /tasks dashboard, **When** user clicks on task card/title, **Then** user navigates to /tasks/[id] page showing task details
2. **Given** user is on /tasks/[id] page, **When** page loads, **Then** user sees task title, completion status, created date, updated date, and action buttons (Edit, Complete, Delete)
3. **Given** user is on /tasks/[id] page, **When** user clicks "Back to Tasks" button, **Then** user returns to /tasks dashboard
4. **Given** user navigates to /tasks/[id] for non-existent or other user's task, **When** page loads, **Then** user sees 404 page with "Task not found" message and link to dashboard
5. **Given** user is on /tasks/[id] page, **When** user clicks Edit/Complete/Delete actions, **Then** actions work same as dashboard with confirmation dialogs where appropriate
6. **Given** task detail page loads, **When** API fetch is in progress, **Then** user sees skeleton loader for task details section

---

### User Story 8 - Responsive Mobile Experience (Priority: P2)

Users on mobile devices must have a fully functional, touch-optimized experience. The interface must adapt to small screens without losing functionality or usability.

**Why this priority**: Mobile usage is common for task management apps. This is high priority because many users will access tasks on phones. This story ensures accessibility across all devices and enables on-the-go task management.

**Independent Test**: Can be fully tested by accessing the app on mobile device (or browser DevTools mobile view), verifying all features work with touch, layouts adapt to small screens, and buttons are appropriately sized. Delivers device-agnostic access.

**Acceptance Scenarios**:

1. **Given** user accesses app on mobile device (< 768px width), **When** any page loads, **Then** layout adapts with full-width components, stacked cards, and mobile-optimized navigation
2. **Given** user taps buttons on mobile, **When** interacting with Add Task, Edit, Delete, Complete buttons, **Then** buttons have appropriate touch target size (minimum 44x44px) and provide haptic/visual feedback
3. **Given** user scrolls task list on mobile, **When** viewing long list, **Then** scrolling is smooth with no horizontal overflow and proper touch momentum
4. **Given** user opens modals/dialogs on mobile, **When** task creation or delete confirmation appears, **Then** modal fills mobile viewport appropriately and can be dismissed with swipe or tap
5. **Given** user switches device orientation, **When** rotating phone landscape/portrait, **Then** layout adapts gracefully without losing form data or scroll position
6. **Given** user uses mobile keyboard, **When** typing in task title input, **Then** input field remains visible and viewport scrolls appropriately without elements hiding behind keyboard

---

### Edge Cases

- What happens when user's JWT token expires during session? (Frontend detects 401 response, redirects to /signin with message "Session expired, please log in again")
- How does system handle concurrent edits from multiple devices? (Last write wins - no conflict resolution in Phase II Step 3; potential future enhancement)
- What happens when API is unreachable (network offline)? (UI shows error state "Unable to connect. Check your network connection" with retry button; no offline mode in MVP)
- How does system handle very long task titles (500 characters)? (Title is truncated with ellipsis in list view, full title shown on detail page or hover tooltip)
- What happens when user has 100+ tasks? (All tasks load; pagination/infinite scroll is out of scope for Step 3 but noted as future enhancement)
- How does system handle rapid clicks on action buttons? (Buttons disable during API calls to prevent duplicate requests; optimistic UI updates for better perceived performance)
- What happens when user manually navigates to /tasks/[id] for invalid ID? (404 page with message "Task not found or access denied" and button to return to dashboard)
- How does system handle browser back/forward navigation? (Next.js router handles this automatically; task state re-fetches on navigation)
- What happens when user refreshes page during form submission? (Form data is lost; no form persistence in MVP - future enhancement)

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Authorization

- **FR-001**: System MUST provide user registration page at /signup with email and password fields, validation for email format and password minimum 8 characters
- **FR-002**: System MUST provide user login page at /signin with email and password fields and "Forgot Password?" link (non-functional for Step 3)
- **FR-003**: System MUST store JWT tokens securely after successful login (HttpOnly cookies preferred or secure localStorage)
- **FR-004**: System MUST include JWT token in Authorization header (Bearer scheme) for all API requests to backend
- **FR-005**: System MUST redirect unauthenticated users from protected routes (/tasks, /tasks/[id]) to /signin page
- **FR-006**: System MUST redirect authenticated users from /signup and /signin to /tasks dashboard
- **FR-007**: System MUST provide logout functionality that clears JWT tokens and redirects to /signin

#### Task Dashboard (/tasks)

- **FR-008**: System MUST display all tasks for logged-in user fetched from GET /api/{user_id}/tasks endpoint
- **FR-009**: Dashboard MUST show empty state with "No tasks yet" message and "Add Task" button when user has zero tasks
- **FR-010**: Dashboard MUST display tasks in card layout (desktop) or list layout (mobile) with title, completion checkbox, created date, and action buttons
- **FR-011**: Dashboard MUST show loading state (skeleton loaders or spinner) while fetching tasks from API
- **FR-012**: Dashboard MUST show error state with retry button if API call fails, with appropriate error message based on error type (401: "Session expired", 500: "Server error")
- **FR-013**: Dashboard MUST provide "Add Task" button prominently positioned for easy access (top-right or center for empty state)

#### Task Creation

- **FR-014**: System MUST provide task creation form accessible via "Add Task" button (modal dialog or inline form)
- **FR-015**: Task creation form MUST include title input field (max 500 characters) with character counter
- **FR-016**: Task creation form MUST validate title is non-empty and trim whitespace before submission
- **FR-017**: System MUST call POST /api/{user_id}/tasks with JWT token and display new task immediately on success (optimistic UI update optional)
- **FR-018**: Task creation form MUST show loading state on submit button during API call and disable button to prevent duplicate submissions
- **FR-019**: Task creation form MUST show success toast notification "Task created successfully" and clear form on success
- **FR-020**: Task creation form MUST show error message and keep form open on API failure for user retry

#### Task Update

- **FR-021**: System MUST provide inline or modal edit functionality for task title via "Edit" button on each task
- **FR-022**: Task edit form MUST pre-fill with current title and allow editing
- **FR-023**: Task edit form MUST validate new title is non-empty and trim whitespace
- **FR-024**: System MUST call PUT /api/{user_id}/tasks/{task_id} with updated title and refresh task display immediately on success
- **FR-025**: Task edit form MUST provide "Cancel" button to exit edit mode without saving
- **FR-026**: Task edit form MUST show error toast on API failure and remain in edit mode for retry

#### Task Completion Toggle

- **FR-027**: System MUST provide checkbox or toggle button for each task to mark complete/incomplete
- **FR-028**: System MUST call PATCH /api/{user_id}/tasks/{task_id}/complete when checkbox is toggled
- **FR-029**: System MUST update task visual state immediately on successful toggle (strikethrough text for completed tasks, checkmark in checkbox)
- **FR-030**: System MUST show loading indicator on checkbox during API call and disable checkbox to prevent rapid clicks
- **FR-031**: System MUST revert checkbox state and show error toast if API call fails

#### Task Deletion

- **FR-032**: System MUST provide "Delete" button for each task
- **FR-033**: System MUST show confirmation dialog before deleting task with message "Are you sure you want to delete this task? This cannot be undone."
- **FR-034**: System MUST call DELETE /api/{user_id}/tasks/{task_id} when user confirms deletion
- **FR-035**: System MUST remove task from UI immediately on successful deletion with fade-out animation
- **FR-036**: System MUST show success toast "Task deleted successfully" on deletion
- **FR-037**: System MUST close dialog and show error toast on API failure, keeping task in list

#### Task Detail Page

- **FR-038**: System MUST provide task detail page at /tasks/[id] showing full task information (title, status, created date, updated date)
- **FR-039**: Task detail page MUST fetch task via GET /api/{user_id}/tasks/{task_id} with JWT authentication
- **FR-040**: Task detail page MUST show 404 error page if task ID invalid, task not found, or access denied (other user's task)
- **FR-041**: Task detail page MUST provide "Back to Tasks" button to return to dashboard
- **FR-042**: Task detail page MUST provide same edit, complete, and delete actions as dashboard with consistent behavior

#### Responsive Design

- **FR-043**: System MUST implement mobile-first responsive design supporting viewports from 320px to 1920px width
- **FR-044**: Desktop layout (≥ 1024px) MUST display tasks in multi-column card grid with sidebar navigation
- **FR-045**: Tablet layout (768px-1023px) MUST display tasks in two-column layout with collapsible navigation
- **FR-046**: Mobile layout (< 768px) MUST display tasks in single-column list with full-width cards and hamburger menu
- **FR-047**: All interactive elements MUST have minimum touch target size of 44x44px for mobile accessibility
- **FR-048**: System MUST prevent horizontal scrolling on all screen sizes

#### Error Handling & Loading States

- **FR-049**: System MUST show loading skeletons or spinners during all async operations (page loads, API calls)
- **FR-050**: System MUST display user-friendly error messages for all error states (network errors, validation errors, auth errors)
- **FR-051**: System MUST provide retry mechanisms for failed API calls where appropriate
- **FR-052**: System MUST handle 401 Unauthorized responses by redirecting to /signin with "Session expired" message
- **FR-053**: System MUST handle 403 Forbidden responses by redirecting to /signin with "Access denied" message
- **FR-054**: System MUST handle 500 Internal Server Error with generic "Something went wrong" message and retry button

#### User Experience Enhancements

- **FR-055**: System MUST provide toast notifications for all user actions (task created, updated, deleted, error occurred)
- **FR-056**: System MUST show success/error feedback within 100ms of action completion
- **FR-057**: Forms MUST auto-focus first input field when opened for immediate user input
- **FR-058**: System MUST maintain form state during validation errors (don't clear valid fields)
- **FR-059**: System MUST show keyboard shortcuts hints for power users (optional enhancement)
- **FR-060**: System MUST prevent form submission on Enter key in multi-line fields

### Key Entities

- **User Session**: Represents authenticated user state with JWT token, user_id, and email. Stored in frontend (cookies or localStorage) and used for API authorization.
- **Task UI Model**: Frontend representation of task data matching TaskResponse schema (id, user_id, title, is_completed, created_at, updated_at). Fetched from backend API and displayed in UI components.
- **Form State**: Temporary client-side state for task creation and edit forms including field values, validation errors, and submission status.
- **API Client**: Service layer for making authenticated HTTP requests to backend with JWT token injection, error handling, and response parsing.
- **Navigation State**: Next.js router state managing current page, query parameters, and navigation history for seamless user experience.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete signup and login flows in under 30 seconds with clear error messages for validation failures
- **SC-002**: Task dashboard loads and displays tasks within 500ms on broadband connection (including API round-trip)
- **SC-003**: All 5 CRUD operations (Create, Read, Update, Delete, Toggle Complete) work correctly with 100% functional success rate in testing
- **SC-004**: UI is fully responsive - all features work on mobile (320px), tablet (768px), and desktop (1920px) screen sizes
- **SC-005**: User receives immediate visual feedback (loading states, success/error messages) for all actions within 100ms
- **SC-006**: Application passes accessibility audit with WCAG 2.1 Level AA compliance (color contrast, keyboard navigation, screen reader support)
- **SC-007**: Zero layout shift (CLS) on page loads - skeleton loaders match final content dimensions
- **SC-008**: Forms validate input client-side before API submission, preventing unnecessary network calls for invalid data
- **SC-009**: Error states provide actionable guidance - users know what went wrong and how to fix it
- **SC-010**: Authenticated users can navigate entire application without encountering 404 or 403 errors for their own resources
- **SC-011**: JWT authentication works seamlessly - users remain logged in across browser sessions until token expires (typically 1 hour)
- **SC-012**: Task state updates reflect immediately in UI (optimistic updates optional) without requiring page refresh

## Scope *(mandatory)*

### In Scope

- Next.js 16+ App Router frontend with TypeScript
- User authentication pages: /signup and /signin with Better Auth integration
- Protected task dashboard at /tasks displaying all user tasks
- Task detail page at /tasks/[id] with full task information
- Task creation form with validation (modal or inline)
- Task editing functionality (inline or modal)
- Task completion toggle with checkbox UI
- Task deletion with confirmation dialog
- Responsive design: mobile (320px+), tablet (768px+), desktop (1024px+)
- shadcn/ui component library for consistent design system
- Tailwind CSS for styling with custom theme (LinkedIn Wrapped light, Regulatis AI dark)
- JWT token management (storage, injection in API calls, expiration handling)
- API client service integrating with existing backend REST endpoints
- Loading states (skeleton loaders, spinners) for all async operations
- Error handling with user-friendly messages and retry mechanisms
- Toast notifications for user feedback (success, error, info)
- Navigation with Next.js App Router (client-side routing)
- Basic accessibility (WCAG 2.1 AA compliance for color contrast, keyboard navigation)
- Dark/light theme toggle with theme persistence

### Out of Scope (for Phase II Step 3)

- Backend API changes - reuse all existing endpoints from Phase II Steps 1 & 2 without modifications
- Password reset / forgot password functionality (UI link present but non-functional)
- Email verification or account activation
- OAuth/SSO integration (Google, GitHub) - only email/password for Step 3
- Multi-factor authentication (MFA/2FA)
- User profile management or account settings page
- Task description field (only title for Step 3 - description was removed from spec)
- Task due dates, priorities, or categories
- Task filtering, sorting, or search functionality
- Task pagination or infinite scroll (load all tasks for Step 3)
- Recurring tasks or task templates
- Task reminders or notifications
- Task collaboration or sharing with other users
- Bulk task operations (select multiple, bulk delete, bulk complete)
- Drag-and-drop task reordering
- Keyboard shortcuts or command palette
- Offline mode or service worker
- Progressive Web App (PWA) features
- Advanced animations or transitions beyond basic hover/focus states
- Comprehensive unit/integration/E2E tests (focus on functional testing in Phase II Step 3)
- Performance monitoring or analytics integration
- Internationalization (i18n) or localization - English only
- Server-side rendering (SSR) optimization beyond Next.js defaults
- SEO optimization for public pages (app is authentication-gated)

## Dependencies *(mandatory)*

### External Dependencies

- **Next.js 16+**: Frontend framework with App Router for file-based routing, Server Components, and modern React features
- **React 19+**: UI library for component-based development (required by Next.js 16)
- **TypeScript 5+**: Type-safe development with strict mode enabled
- **shadcn/ui**: Component library built on Radix UI primitives for accessible, customizable components
- **Tailwind CSS 4+**: Utility-first CSS framework for styling with JIT compiler
- **Better Auth**: Authentication library for JWT token management, user registration, and login flows
- **Lucide React**: Icon library for UI icons (part of shadcn/ui ecosystem)
- **React Hook Form**: Form state management and validation library
- **Zod**: TypeScript-first schema validation for form inputs
- **Sonner**: Toast notification library for user feedback
- **next-themes**: Theme management for dark/light mode switching

### Internal Dependencies

- **Existing Backend REST API** (Phase II Step 1): All task CRUD endpoints must be operational
  - POST /api/{user_id}/tasks (create task)
  - GET /api/{user_id}/tasks (list all tasks)
  - GET /api/{user_id}/tasks/{task_id} (get single task)
  - PUT /api/{user_id}/tasks/{task_id} (update task title)
  - PATCH /api/{user_id}/tasks/{task_id}/complete (toggle completion)
  - DELETE /api/{user_id}/tasks/{task_id} (delete task)
- **JWT Authentication System** (Phase II Step 2): Better Auth JWT issuance and FastAPI JWT verification must be working
- **Neon PostgreSQL Database**: Backend must have working database connection with tasks table
- **CORS Configuration**: Backend must allow requests from frontend origin (http://localhost:3000 for development)
- **Shared BETTER_AUTH_SECRET**: Frontend and backend must use same secret key for JWT signing/verification

### Technical Stack

**Frontend Framework:**
- Next.js 16+ with App Router (not Pages Router)
- React 19+ with Server Components and Client Components
- TypeScript 5+ with strict mode

**UI Components:**
- shadcn/ui component library
- Radix UI primitives (underlying shadcn/ui)
- Lucide icons

**Styling:**
- Tailwind CSS 4+ with custom theme
- CSS-in-JS via Tailwind (no styled-components or emotion)
- Custom color palette for light/dark themes

**State Management:**
- React Context API for global state (auth context)
- React Hook Form for form state
- SWR or React Query for server state (optional - can use plain fetch)

**Authentication:**
- Better Auth with JWT plugin
- JWT tokens stored in HttpOnly cookies or localStorage
- Protected routes with middleware or HOC

**API Client:**
- Native fetch API with JWT token injection
- API client service layer for type-safe requests
- Error handling and retry logic

## Assumptions *(mandatory)*

- Next.js frontend and FastAPI backend run on separate ports (frontend: 3000, backend: 8000) in development
- HTTPS is used in production but HTTP is acceptable for local development
- Modern browsers supporting ES2020+ features (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Users have JavaScript enabled (no progressive enhancement for JS-disabled browsers)
- Users have stable internet connection for real-time API interactions (no offline mode)
- JWT tokens expire after 1 hour (as configured in Phase II Step 2)
- Task list fits in memory (no pagination needed for MVP with reasonable number of tasks < 1000)
- All users use Gregorian calendar and dates display in ISO format or user's local timezone
- Task titles are plain text without rich formatting (no markdown, HTML, or special characters beyond Unicode)
- English is the only supported language (no i18n/l10n in Phase II Step 3)
- Responsive breakpoints follow Tailwind CSS defaults (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
- Design system colors and spacing follow shadcn/ui conventions with custom theme overrides
- Users tolerate soft-deletes if needed (deletion is immediate in UI but backend can implement soft-delete)
- No real-time collaboration needed (no WebSocket, no live updates from other users)
- Browser localStorage or cookies are available and not blocked by privacy settings
- Users can see task creation/update timestamps but don't need to edit them manually
- Task ordering is backend-controlled (typically by created_at or updated_at descending)
- Users don't need to export/import tasks in Phase II Step 3
- Application works correctly with browser back/forward buttons via Next.js router
- Form validation messages use clear, non-technical language suitable for all users

## Open Questions *(optional)*

No critical open questions remaining - feature is well-defined with reasonable defaults applied.

Minor considerations documented for planning phase:

1. Should we use HttpOnly cookies or localStorage for JWT storage?
   - **Default**: HttpOnly cookies for better XSS protection (requires backend cookie handling)
   - **Alternative**: localStorage for simpler implementation but slightly less secure

2. Should task creation form be a modal dialog or inline in dashboard?
   - **Default**: Modal dialog (cleaner UX, better focus)
   - **Alternative**: Inline form at top of task list (fewer clicks)

3. Should we implement optimistic UI updates for better perceived performance?
   - **Default**: No optimistic updates for MVP (simpler state management)
   - **Alternative**: Optimistic updates with rollback on error (better UX, more complex)

4. Should we use SWR or React Query for server state management?
   - **Default**: Plain fetch with React state (simpler, fewer dependencies)
   - **Alternative**: SWR or React Query (better caching, automatic revalidation)

5. Should completed tasks have different visual treatment beyond strikethrough?
   - **Default**: Strikethrough text + muted color + checkmark
   - **Alternative**: Move to separate "Completed" section with collapse/expand

6. Should we show relative timestamps (e.g., "2 hours ago") or absolute dates?
   - **Default**: Relative for recent (< 24h), absolute for older tasks
   - **Alternative**: Always absolute in consistent format

7. Should mobile navigation use bottom tab bar or hamburger menu?
   - **Default**: Hamburger menu in top-left (simpler for Step 3 with few nav items)
   - **Alternative**: Bottom tab bar (more mobile-native but needs more nav items to justify)

8. Should we implement keyboard shortcuts for power users?
   - **Default**: No keyboard shortcuts for MVP
   - **Alternative**: Basic shortcuts (Ctrl+K to add task, Ctrl+/ for shortcut list)

## Related Documents *(optional)*

- **Phase II Step 1 Specification**: `specs/002-rest-api/spec.md` - Backend REST API endpoints
- **Phase II Step 2 Specification**: `specs/003-jwt-auth/spec.md` - JWT authentication system
- **Project Constitution**: `.specify/memory/constitution.md` - Core principles and phased development approach
- **Backend API Documentation**: `backend/README.md` - API endpoint details and examples
- **Task Service Implementation**: `backend/src/services/task_service.py` - Backend business logic
- **Better Auth Integration Guide**: `.claude/skills/better-auth/skill.md` - JWT authentication patterns
- **Next.js 16 Development Guide**: `.claude/skills/nextjs16-development/skill.md` - Next.js 16 best practices
- **shadcn/ui Development Guide**: `.claude/skills/shadcn-ui-development/skill.md` - Component library usage
- **Tailwind CSS Styling Guide**: `.claude/skills/tailwindcss-styling/skill.md` - Styling patterns and responsive design

---

**Next Steps**: After spec approval, proceed to planning phase (`/sp.plan`) to create detailed implementation plan with architecture decisions, component structure, and task breakdown.