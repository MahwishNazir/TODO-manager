# Feature Specification: Phase II Step 1 - REST API with Persistent Storage

**Feature Branch**: `002-rest-api`
**Created**: 2026-01-12
**Status**: Draft
**Phase**: Phase II Step 1 - Web API Foundation (No Authentication)
**Tier**: Basic Level Features via REST API
**Input**: User description: "Convert console app logic into a web-based REST API with persistent storage, while keeping things simple (no authentication yet). Implement all 5 Basic Level features as REST APIs. Persist data in Neon Serverless PostgreSQL. Use FastAPI + SQLModel. Assume user_id is passed but not verified yet."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Retrieve Tasks via API (Priority: P1)

As an API consumer, I want to create tasks and retrieve them via HTTP endpoints so I can build applications that persist todo data across sessions.

**Why this priority**: This is the foundational capability - creating and reading data via REST API. Without this, no other API operations have value. This enables the transition from in-memory console app to persistent web-based system.

**Independent Test**: Can be fully tested by making POST requests to create tasks and GET requests to retrieve them. Delivers immediate value as a persistent task storage API.

**Acceptance Scenarios**:

1. **Given** no tasks exist for user "user123", **When** I POST to `/api/user123/tasks` with JSON `{"title": "Buy groceries"}`, **Then** I receive HTTP 201 with the created task including an ID, title, completion status (false), and timestamps
2. **Given** I have created 3 tasks for user "user123", **When** I GET `/api/user123/tasks`, **Then** I receive HTTP 200 with JSON array containing all 3 tasks with their full details
3. **Given** no tasks exist for user "user123", **When** I GET `/api/user123/tasks`, **Then** I receive HTTP 200 with an empty JSON array `[]`
4. **Given** I am creating a task, **When** I POST to `/api/user123/tasks` with empty title `{"title": ""}`, **Then** I receive HTTP 422 (Unprocessable Entity) with validation error details
5. **Given** I have a task with ID 1 for user "user123", **When** I GET `/api/user123/tasks/1`, **Then** I receive HTTP 200 with the complete task object
6. **Given** I request a non-existent task, **When** I GET `/api/user123/tasks/999`, **Then** I receive HTTP 404 with error message

---

### User Story 2 - Mark Tasks Complete via API (Priority: P2)

As an API consumer, I want to mark tasks as complete or incomplete via HTTP endpoints so I can track task progress in my applications.

**Why this priority**: Completion tracking is the core value proposition of a todo system. This enables full task lifecycle management via API.

**Independent Test**: Can be tested by creating tasks via POST and toggling their completion status via PATCH. Delivers task management value.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task with ID 1 for user "user123", **When** I PATCH `/api/user123/tasks/1/complete`, **Then** I receive HTTP 200 with the updated task showing `is_completed: true`
2. **Given** I have a complete task with ID 2 for user "user123", **When** I PATCH `/api/user123/tasks/2/complete` (toggle operation), **Then** I receive HTTP 200 with the task showing `is_completed: false`
3. **Given** I try to complete a non-existent task, **When** I PATCH `/api/user123/tasks/999/complete`, **Then** I receive HTTP 404 with error message
4. **Given** I try to complete a task belonging to a different user, **When** I PATCH `/api/user123/tasks/5/complete` (where task 5 belongs to "user456"), **Then** I receive HTTP 404 with error message (user isolation enforced)

---

### User Story 3 - Update Task Details via API (Priority: P3)

As an API consumer, I want to update task titles and properties via HTTP endpoints so I can modify task details in my applications.

**Why this priority**: Editing capability is important for usability but not critical for MVP. Core create/read/complete operations provide more immediate value.

**Independent Test**: Can be tested by creating a task and modifying it via PUT. Delivers editing convenience value.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 1 titled "Buy milk" for user "user123", **When** I PUT `/api/user123/tasks/1` with JSON `{"title": "Buy organic milk"}`, **Then** I receive HTTP 200 with the updated task reflecting the new title
2. **Given** I try to update a task with empty title, **When** I PUT `/api/user123/tasks/1` with `{"title": ""}`, **Then** I receive HTTP 422 with validation error
3. **Given** I try to update a non-existent task, **When** I PUT `/api/user123/tasks/999` with valid data, **Then** I receive HTTP 404 with error message
4. **Given** I try to update a task belonging to a different user, **When** I PUT `/api/user123/tasks/5` (where task 5 belongs to "user456"), **Then** I receive HTTP 404 with error message (user isolation enforced)

---

### User Story 4 - Delete Tasks via API (Priority: P4)

As an API consumer, I want to delete tasks via HTTP endpoints so I can remove tasks in my applications.

**Why this priority**: Deletion is useful for cleanup but less critical than creation, reading, and completion. Users can tolerate leaving completed tasks in the database temporarily.

**Independent Test**: Can be tested by creating tasks and removing them via DELETE. Delivers list management value.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 1 for user "user123", **When** I DELETE `/api/user123/tasks/1`, **Then** I receive HTTP 204 (No Content) and the task is removed from the database
2. **Given** I try to delete a non-existent task, **When** I DELETE `/api/user123/tasks/999`, **Then** I receive HTTP 404 with error message
3. **Given** I have 5 tasks and delete task ID 3, **When** I GET `/api/user123/tasks`, **Then** I see 4 tasks remaining with their original IDs (IDs are not renumbered)
4. **Given** I try to delete a task belonging to a different user, **When** I DELETE `/api/user123/tasks/5` (where task 5 belongs to "user456"), **Then** I receive HTTP 404 with error message (user isolation enforced)

---

### User Story 5 - Database Persistence Across Sessions (Priority: P1)

As an API consumer, I want tasks to persist in the database across application restarts so data is never lost.

**Why this priority**: Persistent storage is the primary advancement over Phase I. Without this, the REST API provides no advantage over the console app.

**Independent Test**: Can be tested by creating tasks, restarting the FastAPI server, and verifying data remains accessible.

**Acceptance Scenarios**:

1. **Given** I have created 5 tasks for user "user123", **When** the FastAPI application restarts, **Then** all 5 tasks remain in the database and are retrievable via GET requests
2. **Given** I have tasks stored in the database, **When** I create new tasks after a restart, **Then** task IDs continue incrementing from the last used ID (no ID collision)
3. **Given** multiple users have tasks in the database, **When** I query for user "user123" tasks, **Then** I only receive tasks belonging to "user123" (data isolation verified)

---

### User Story 6 - User Isolation Without Authentication (Priority: P1)

As an API consumer, I want tasks to be isolated by user_id so different users' data doesn't mix, even though authentication is not yet enforced.

**Why this priority**: Data isolation is critical for preparing for authentication in future steps. This establishes the architectural pattern that will support proper auth later.

**Independent Test**: Can be tested by creating tasks for different user_ids and verifying each user only sees their own tasks.

**Acceptance Scenarios**:

1. **Given** user "user123" has 3 tasks and user "user456" has 2 tasks, **When** I GET `/api/user123/tasks`, **Then** I receive only the 3 tasks belonging to "user123"
2. **Given** I try to access task ID 1 belonging to "user456", **When** I GET `/api/user123/tasks/1`, **Then** I receive HTTP 404 (task exists but belongs to different user)
3. **Given** I create a task for user "user123", **When** I GET `/api/user456/tasks`, **Then** the new task does not appear in user456's task list

---

### Edge Cases

- What happens when the client sends malformed JSON in the request body?
- How does the API handle very long task titles (e.g., 10,000+ characters)?
- What happens when the database connection is lost during a request?
- How does the system handle concurrent requests trying to modify the same task?
- What happens when invalid user_id formats are provided (e.g., special characters, SQL injection attempts)?
- How does the API respond to requests with missing required fields?
- What happens when the database reaches storage capacity?
- How does the system handle requests with extremely long user_id values?
- What happens when DELETE is called twice on the same task ID?
- How does the API handle requests with extra/unknown fields in the JSON body?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a RESTful HTTP API with endpoints for all 5 basic operations (Create, Read, Update, Delete, Mark Complete)
- **FR-002**: System MUST persist all task data in Neon Serverless PostgreSQL database using SQLModel ORM
- **FR-003**: System MUST assign a unique, auto-incrementing integer ID to each task upon creation
- **FR-004**: System MUST validate that task titles are non-empty strings (minimum 1 character, maximum 500 characters)
- **FR-005**: System MUST store each task with: ID, user_id, title, is_completed (boolean), created_at (timestamp), updated_at (timestamp)
- **FR-006**: System MUST enforce user isolation - users can only access tasks where user_id matches the path parameter
- **FR-007**: System MUST return appropriate HTTP status codes: 200 (OK), 201 (Created), 204 (No Content), 404 (Not Found), 422 (Validation Error), 500 (Server Error)
- **FR-008**: System MUST return JSON responses for all endpoints (except DELETE which returns 204 with no body)
- **FR-009**: System MUST handle database connection errors gracefully with appropriate 500 status codes
- **FR-010**: System MUST validate user_id format (alphanumeric, hyphens, underscores only, max 50 characters)
- **FR-011**: System MUST support CORS headers to allow frontend access from different origins
- **FR-012**: System MUST provide OpenAPI/Swagger documentation at `/docs` endpoint
- **FR-013**: System MUST log all requests with timestamp, method, path, status code, and execution time
- **FR-014**: System MUST return detailed error messages in JSON format with error type and description

### API Contract Specifications

#### Endpoint: GET /api/{user_id}/tasks

**Purpose**: Retrieve all tasks for a specific user

**Request Parameters**:
- Path: `user_id` (string, required) - User identifier (alphanumeric, hyphens, underscores, max 50 chars)

**Request Body**: None

**Response Schema** (HTTP 200):
```json
[
  {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "is_completed": false,
    "created_at": "2026-01-12T10:30:00Z",
    "updated_at": "2026-01-12T10:30:00Z"
  }
]
```

**HTTP Status Codes**:
- 200 OK - Tasks retrieved successfully (empty array if no tasks)
- 422 Unprocessable Entity - Invalid user_id format
- 500 Internal Server Error - Database connection error

**Error Cases**:
- Invalid user_id format → 422 with validation error details
- Database unavailable → 500 with generic error message

---

#### Endpoint: POST /api/{user_id}/tasks

**Purpose**: Create a new task for a specific user

**Request Parameters**:
- Path: `user_id` (string, required) - User identifier

**Request Body Schema**:
```json
{
  "title": "string (required, 1-500 characters)"
}
```

**Response Schema** (HTTP 201):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "is_completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

**HTTP Status Codes**:
- 201 Created - Task created successfully
- 422 Unprocessable Entity - Validation error (empty title, title too long, invalid user_id, malformed JSON)
- 500 Internal Server Error - Database error

**Error Cases**:
- Empty title → 422 with `{"detail": "title cannot be empty"}`
- Title > 500 chars → 422 with `{"detail": "title exceeds maximum length of 500 characters"}`
- Missing title field → 422 with `{"detail": "title is required"}`
- Malformed JSON → 422 with parsing error details
- Database error → 500 with generic message

---

#### Endpoint: GET /api/{user_id}/tasks/{id}

**Purpose**: Retrieve a specific task by ID for a user

**Request Parameters**:
- Path: `user_id` (string, required) - User identifier
- Path: `id` (integer, required) - Task ID

**Request Body**: None

**Response Schema** (HTTP 200):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "is_completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

**HTTP Status Codes**:
- 200 OK - Task retrieved successfully
- 404 Not Found - Task not found or belongs to different user
- 422 Unprocessable Entity - Invalid id format (non-integer)
- 500 Internal Server Error - Database error

**Error Cases**:
- Task doesn't exist → 404 with `{"detail": "Task not found"}`
- Task belongs to different user → 404 with `{"detail": "Task not found"}` (don't reveal existence)
- Invalid id (e.g., "abc") → 422 with validation error
- Database error → 500

---

#### Endpoint: PUT /api/{user_id}/tasks/{id}

**Purpose**: Update a task's title

**Request Parameters**:
- Path: `user_id` (string, required) - User identifier
- Path: `id` (integer, required) - Task ID

**Request Body Schema**:
```json
{
  "title": "string (required, 1-500 characters)"
}
```

**Response Schema** (HTTP 200):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy organic groceries",
  "is_completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T11:45:00Z"
}
```

**HTTP Status Codes**:
- 200 OK - Task updated successfully
- 404 Not Found - Task not found or belongs to different user
- 422 Unprocessable Entity - Validation error (empty title, title too long, malformed JSON, invalid id)
- 500 Internal Server Error - Database error

**Error Cases**:
- Task not found → 404 with `{"detail": "Task not found"}`
- Task belongs to different user → 404 with `{"detail": "Task not found"}`
- Empty title → 422 with validation error
- Title > 500 chars → 422 with validation error
- Database error → 500

---

#### Endpoint: DELETE /api/{user_id}/tasks/{id}

**Purpose**: Delete a task permanently

**Request Parameters**:
- Path: `user_id` (string, required) - User identifier
- Path: `id` (integer, required) - Task ID

**Request Body**: None

**Response Schema** (HTTP 204): No content (empty response body)

**HTTP Status Codes**:
- 204 No Content - Task deleted successfully
- 404 Not Found - Task not found or belongs to different user
- 422 Unprocessable Entity - Invalid id format
- 500 Internal Server Error - Database error

**Error Cases**:
- Task not found → 404 with `{"detail": "Task not found"}`
- Task belongs to different user → 404 with `{"detail": "Task not found"}`
- Invalid id → 422 with validation error
- Database error → 500

---

#### Endpoint: PATCH /api/{user_id}/tasks/{id}/complete

**Purpose**: Toggle task completion status (or set to completed if implementing as non-toggle)

**Request Parameters**:
- Path: `user_id` (string, required) - User identifier
- Path: `id` (integer, required) - Task ID

**Request Body**: None (completion status is toggled)

**Response Schema** (HTTP 200):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "is_completed": true,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T12:00:00Z"
}
```

**HTTP Status Codes**:
- 200 OK - Task completion status toggled successfully
- 404 Not Found - Task not found or belongs to different user
- 422 Unprocessable Entity - Invalid id format
- 500 Internal Server Error - Database error

**Error Cases**:
- Task not found → 404 with `{"detail": "Task not found"}`
- Task belongs to different user → 404 with `{"detail": "Task not found"}`
- Invalid id → 422 with validation error
- Database error → 500

**Implementation Note**: This endpoint toggles the completion status (if currently false, set to true; if currently true, set to false). Alternative: Accept optional request body `{"is_completed": true/false}` for explicit setting.

---

### Non-Functional Requirements

- **NFR-001**: API MUST respond to all requests within 200ms under normal load (< 100 concurrent requests)
- **NFR-002**: Database connection pool MUST support at least 20 concurrent connections
- **NFR-003**: Code MUST follow PEP 8 Python style guidelines
- **NFR-004**: Code MUST use type hints for all FastAPI route handlers and service functions
- **NFR-005**: Code MUST include docstrings for all modules, classes, and public functions
- **NFR-006**: API MUST use SQLModel for ORM with proper model definitions
- **NFR-007**: Database schema MUST include indexes on user_id and id columns for performance
- **NFR-008**: API MUST validate all input data using Pydantic models
- **NFR-009**: API MUST implement proper error handling with try-except blocks for database operations
- **NFR-010**: API MUST log all errors with stack traces for debugging
- **NFR-011**: Code MUST be linted with pylint and type-checked with mypy without errors
- **NFR-012**: Test coverage MUST be at least 80% for all business logic
- **NFR-013**: API MUST support graceful shutdown to close database connections properly
- **NFR-014**: Database migrations MUST be version-controlled and repeatable

### Key Entities *(include if feature involves data)*

- **Task** (Database Table: `tasks`):
  - `id` (Primary Key, Integer, Auto-increment) - Unique task identifier
  - `user_id` (String, Indexed, Max 50 chars) - User identifier (not verified in Step 1)
  - `title` (String, 1-500 characters) - Task description
  - `is_completed` (Boolean, Default: false) - Completion status
  - `created_at` (Timestamp, Auto-set on creation) - Creation timestamp
  - `updated_at` (Timestamp, Auto-updated on modification) - Last modification timestamp
  - **Constraint**: `user_id` + `id` uniqueness is enforced naturally by primary key on `id`

- **Database Connection**:
  - Neon Serverless PostgreSQL connection string stored in environment variable
  - Connection pooling managed by SQLModel/SQLAlchemy
  - Automatic reconnection on connection loss

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API consumers can create a task and retrieve it via GET request within 2 seconds
- **SC-002**: All 5 basic operations (Create, Read, Update, Delete, Mark Complete) are accessible via documented REST endpoints and return correct status codes
- **SC-003**: Tasks persist in the database across API server restarts with 100% data retention
- **SC-004**: API handles 100 concurrent requests without errors or response time degradation beyond 500ms
- **SC-005**: User isolation is enforced - users can only access their own tasks (0% cross-user data leakage)
- **SC-006**: All input validation errors return HTTP 422 with clear error messages within 100ms
- **SC-007**: Database queries execute in under 50ms for task lists with up to 1000 tasks per user
- **SC-008**: API documentation at `/docs` endpoint accurately describes all endpoints, request/response schemas, and status codes
- **SC-009**: Code passes linting (pylint score ≥ 8.0/10) and type checking (mypy with no errors)
- **SC-010**: Test suite achieves ≥ 80% code coverage and all tests pass

### Quality Metrics

- **QM-001**: Zero unhandled exceptions - all errors return appropriate HTTP status codes with JSON error responses
- **QM-002**: All edge cases documented in spec are handled gracefully with appropriate status codes and error messages
- **QM-003**: Database schema includes proper indexes, constraints, and data types
- **QM-004**: API follows REST conventions (proper HTTP methods, status codes, resource naming)
- **QM-005**: All database operations use parameterized queries (SQL injection prevention)

## Constraints & Assumptions

### Constraints

- **C-001**: No authentication or authorization enforcement in Step 1 (user_id is trusted from URL path)
- **C-002**: No rate limiting or API throttling in Step 1
- **C-003**: No frontend implementation in Step 1 (API only)
- **C-004**: Database must be Neon Serverless PostgreSQL (specified in requirements)
- **C-005**: Backend must use FastAPI framework with SQLModel ORM (specified in requirements)
- **C-006**: Must support Python 3.10 or higher
- **C-007**: No task priority, due dates, or advanced features in Step 1 (Basic Level only)

### Assumptions

- **A-001**: API consumers will be developers testing via curl, Postman, or automated tests
- **A-002**: user_id values are provided by API consumers and are not validated against any user registry (no user table exists yet)
- **A-003**: Neon Serverless PostgreSQL connection string is available via environment variable
- **A-004**: Database has sufficient storage capacity (no quota concerns for Step 1)
- **A-005**: API will be accessed over HTTP (HTTPS/TLS termination handled by reverse proxy if needed)
- **A-006**: Task titles are plain text (no HTML, markdown, or rich formatting)
- **A-007**: Timestamps are stored in UTC timezone
- **A-008**: API consumers accept JSON-only responses (no XML or other formats)

## Out of Scope (for Step 1)

The following features are explicitly excluded from Step 1 and deferred to future steps:

- **Authentication and authorization** - Deferred to Phase II Step 2 (Better Auth integration)
- **JWT token validation** - Deferred to Phase II Step 2
- **User registration and login** - Deferred to Phase II Step 2
- **Frontend Next.js application** - Deferred to Phase II Step 3
- **Task priorities** - Deferred to Intermediate tier
- **Due dates and reminders** - Deferred to Advanced tier
- **Search and filter functionality** - Deferred to Intermediate tier
- **Pagination** - Deferred to Phase II Step 3 or Intermediate tier
- **Task sorting** (custom order) - Deferred to Intermediate tier
- **Recurring tasks** - Deferred to Advanced tier
- **Categories or tags** - Deferred to future phases
- **Task sharing or collaboration** - Deferred to future phases
- **Rate limiting** - Deferred to Phase II Step 2 or production hardening
- **API versioning** - Deferred to future phases
- **Webhooks or notifications** - Deferred to Advanced tier

## Dependencies

### Runtime Dependencies

- **Python 3.10+**: Required runtime environment
- **FastAPI**: Web framework for building REST API
- **SQLModel**: ORM for database interactions (combines SQLAlchemy + Pydantic)
- **Uvicorn**: ASGI server for running FastAPI
- **Psycopg2** or **Asyncpg**: PostgreSQL database driver
- **Pydantic**: Data validation (included with FastAPI)
- **Python-dotenv**: Environment variable management

### Development Dependencies

- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for testing FastAPI endpoints
- **pylint**: Code linting
- **mypy**: Static type checking
- **black**: Code formatting (optional but recommended)

### Infrastructure Dependencies

- **Neon Serverless PostgreSQL**: Database service (cloud-hosted)
- **Environment variables**: `DATABASE_URL` for Neon connection string

## Migration Path

### Phase I → Phase II Step 1 Transition

**Data Migration**:
1. Export Phase I in-memory tasks to JSON file (if Phase I export feature was implemented)
2. Create database schema in Neon PostgreSQL
3. Import JSON data to database via migration script (optional - most users will start fresh)

**Architectural Migration**:
- Console CLI → REST API endpoints
- In-memory storage → PostgreSQL database
- Synchronous operations → Async-capable API (optional for Step 1)

### Step 1 → Step 2 Transition (Future)

**Authentication Preparation**:
- user_id path parameter will be replaced with authenticated user identity from JWT token
- Endpoints will validate JWT tokens using Better Auth shared secret
- User table will be added to database
- Foreign key relationship will be established between tasks.user_id and users.id

**Backwards Compatibility**:
- Database schema supports Step 2 without migration (user_id column already exists)
- API contract remains similar (user_id moves from path to auth token)

## Acceptance Criteria Summary

This feature is considered complete when:

1. All 6 REST API endpoints are implemented and tested (GET /tasks, POST /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}, PATCH /tasks/{id}/complete)
2. All endpoints return correct HTTP status codes as specified in API contract
3. Database persistence is working - tasks survive server restarts
4. User isolation is enforced - users can only access their own tasks
5. All functional requirements (FR-001 through FR-014) are met
6. All success criteria (SC-001 through SC-010) are achieved
7. Test coverage is ≥ 80% with all tests passing
8. Code passes pylint (≥ 8.0/10) and mypy (zero errors)
9. All edge cases are handled with appropriate error responses
10. OpenAPI documentation is generated and accessible at `/docs`
11. Database schema includes proper indexes and constraints
12. All API endpoints handle database connection errors gracefully
13. Input validation is comprehensive with clear error messages
14. Code follows FastAPI and SQLModel best practices
