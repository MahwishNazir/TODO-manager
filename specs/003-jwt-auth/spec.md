# Feature Specification: JWT Authentication with Better Auth

**Feature Branch**: `003-jwt-auth`
**Created**: 2026-01-12
**Status**: Draft
**Input**: User description: "Secure the existing REST API so that only authenticated users can access and manipulate their own tasks, using JWT-based authentication issued by Better Auth on the frontend and verified by FastAPI on the backend. Integrate Better Auth in a Next.js App Router frontend, enable JWT issuance via Better Auth, implement JWT verification in FastAPI, enforce strict user isolation across all endpoints, maintain stateless backend authentication, and reuse all step-1 REST endpoints (no breaking changes)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration and Login (Priority: P1)

Users must be able to create accounts and log in to access the task management system. Without authentication, no user can access any task data, ensuring security from the start.

**Why this priority**: This is foundational - without user accounts and login, authentication cannot function. This story delivers the core security mechanism and enables all other protected features.

**Independent Test**: Can be fully tested by registering a new account, logging in, receiving a JWT token, and verifying the token contains correct user information. Delivers immediate value by establishing user identity and security.

**Acceptance Scenarios**:

1. **Given** no existing account, **When** user provides valid email and password on registration form, **Then** account is created and user receives confirmation
2. **Given** registered account exists, **When** user provides correct email and password on login form, **Then** user receives JWT token containing user ID
3. **Given** registered account exists, **When** user provides incorrect password on login form, **Then** login is rejected with appropriate error message
4. **Given** user is already logged in, **When** user navigates to protected pages, **Then** existing valid JWT token is used without requiring re-login

---

### User Story 2 - Protected API Access (Priority: P1)

All existing task management API endpoints must require valid JWT authentication. Unauthenticated requests are rejected, and the JWT's user ID automatically determines which tasks the user can access.

**Why this priority**: This is the core security requirement - protecting the REST API endpoints. Without this, authentication serves no purpose. This story delivers immediate security value by blocking unauthorized access.

**Independent Test**: Can be fully tested by attempting API calls with no token (rejected), invalid token (rejected), and valid token (accepted). Delivers security enforcement across all existing endpoints without breaking current functionality.

**Acceptance Scenarios**:

1. **Given** no JWT token provided, **When** user calls any task API endpoint, **Then** request is rejected with 401 Unauthorized
2. **Given** valid JWT token in Authorization header, **When** user calls any task API endpoint, **Then** request is processed and user_id is automatically extracted from token
3. **Given** expired JWT token, **When** user calls any task API endpoint, **Then** request is rejected with 401 Unauthorized and clear expiration message
4. **Given** tampered/invalid JWT token, **When** user calls any task API endpoint, **Then** request is rejected with 401 Unauthorized
5. **Given** valid JWT token for user A, **When** user A calls task endpoints, **Then** only user A's tasks are accessible (user isolation enforced automatically)

---

### User Story 3 - Token Refresh and Session Management (Priority: P2)

Users with expiring tokens can refresh them without re-entering credentials. Long sessions remain uninterrupted while maintaining security through limited token lifetimes.

**Why this priority**: This enables smooth user experience for longer sessions while maintaining security. Users remain logged in across multiple work sessions without annoying re-logins, but tokens still expire for security.

**Independent Test**: Can be fully tested by logging in, waiting until near token expiration, requesting token refresh, and verifying new valid token is issued. Delivers better user experience by eliminating unnecessary re-authentication.

**Acceptance Scenarios**:

1. **Given** user has valid but expiring JWT token, **When** user requests token refresh, **Then** new JWT token with extended expiration is issued
2. **Given** user has expired JWT token, **When** user requests token refresh, **Then** refresh is rejected and user must re-login
3. **Given** user refreshes token, **When** frontend receives new token, **Then** frontend automatically uses new token for subsequent API calls

---

### User Story 4 - Logout and Token Invalidation (Priority: P3)

Users can explicitly log out, ending their session. The frontend discards tokens, preventing further API access until user logs in again.

**Why this priority**: Important for security when using shared devices, but lower priority than core authentication flows. Users can still be secure by closing the browser (tokens expire). This adds explicit session control.

**Independent Test**: Can be fully tested by logging in, performing task operations, logging out, and verifying subsequent API calls are rejected. Delivers explicit session termination control.

**Acceptance Scenarios**:

1. **Given** user is logged in with valid JWT, **When** user clicks logout, **Then** frontend discards JWT token from storage
2. **Given** user has logged out, **When** user attempts to access protected pages, **Then** user is redirected to login page
3. **Given** user has logged out, **When** user attempts API calls with old token, **Then** requests continue to fail after frontend-side logout (backend remains stateless)

---

### Edge Cases

- What happens when JWT secret key changes? (All existing tokens become invalid, users must re-login)
- How does system handle concurrent login from multiple devices? (Multiple valid tokens can exist simultaneously, each with own expiration)
- What happens when user deletes account while JWT tokens still valid? (Backend must handle non-existent user_id gracefully with 401/403)
- How does system handle clock skew between frontend, backend, and Better Auth? (Standard JWT exp/iat validation with reasonable tolerance)
- What happens when JWT token is intercepted by malicious actor? (Token is valid until expiration - this is accepted risk of JWT stateless design, mitigated by short expiration times)
- How does frontend handle token expiration during multi-step operation? (Frontend should retry with refreshed token transparently)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide user registration form accepting email and password with validation (email format, password strength minimum 8 characters)
- **FR-002**: System MUST provide user login form accepting email and password credentials
- **FR-003**: System MUST issue JWT tokens upon successful login containing user_id, email, and standard claims (exp, iat, sub)
- **FR-004**: System MUST store JWT tokens securely in frontend (HttpOnly cookies preferred, or secure localStorage with XSS protections)
- **FR-005**: System MUST include JWT token in Authorization header (Bearer scheme) for all task API requests
- **FR-006**: Backend MUST verify JWT signature using shared secret key before processing any task API request
- **FR-007**: Backend MUST extract user_id from verified JWT token and use it for all database queries (removing need for user_id path parameter)
- **FR-008**: Backend MUST reject requests with missing, invalid, expired, or tampered JWT tokens with 401 Unauthorized status
- **FR-009**: Backend MUST remain stateless - no session storage, only JWT validation per request
- **FR-010**: System MUST maintain backward compatibility - existing task API endpoints keep same paths and request/response schemas
- **FR-011**: System MUST provide token refresh endpoint allowing users to obtain new JWT before current token expires
- **FR-012**: Frontend MUST handle 401 Unauthorized responses by redirecting to login page or attempting token refresh
- **FR-013**: System MUST set JWT token expiration time of 1 hour for access tokens
- **FR-014**: System MUST enforce user isolation - users can only access their own tasks through JWT user_id claim
- **FR-015**: Frontend MUST provide logout functionality that clears stored JWT tokens from browser
- **FR-016**: System MUST use Better Auth library for authentication flows on Next.js frontend
- **FR-017**: Backend MUST use shared secret key (BETTER_AUTH_SECRET) configured via environment variable for JWT verification
- **FR-018**: System MUST validate JWT claims: signature, expiration (exp), issued-at (iat), and subject (sub matches user_id)

### Key Entities

- **User**: Represents authenticated user with unique user_id, email, and password hash. User_id appears in JWT token and links to task ownership.
- **JWT Token**: Contains user_id (subject), email, expiration timestamp, and signature. Issued by Better Auth, verified by FastAPI. Enables stateless authentication.
- **Authentication Session**: Represented only by JWT token existence in frontend. No backend session state. Session ends when token expires or user logs out.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete registration and login flows in under 30 seconds from landing page to authenticated dashboard
- **SC-002**: All existing task API endpoints reject unauthenticated requests with 401 status code within 10ms (fast JWT validation)
- **SC-003**: Authenticated users can perform all task operations (create, read, update, delete) without any breaking changes to API contracts
- **SC-004**: User isolation is enforced - users attempting to access other users' task data receive 404 or 403 errors, never see other users' data
- **SC-005**: Backend remains stateless - can horizontally scale without session synchronization, any backend instance can validate any JWT
- **SC-006**: JWT token refresh succeeds 95% of the time when requested before expiration, enabling uninterrupted multi-hour sessions
- **SC-007**: System handles 1000 concurrent authenticated users with average JWT validation time under 5ms per request
- **SC-008**: Zero existing API integration breaks - all Step 1 API consumers can migrate by only adding Authorization header

## Scope *(mandatory)*

### In Scope

- User registration with email/password via Better Auth on Next.js frontend
- User login flow issuing JWT tokens via Better Auth
- JWT verification middleware in FastAPI backend using shared secret
- Automatic user_id extraction from JWT for all task operations
- Protection of all 6 existing task API endpoints (POST, GET, PUT, PATCH, DELETE)
- Token expiration and validation enforcement
- Token refresh mechanism for session extension
- Frontend logout functionality (token deletion)
- User isolation enforcement via JWT user_id claim
- Maintaining existing API contracts (paths, schemas, status codes)

### Out of Scope (for Phase II Step 2)

- Password reset / forgot password flows (defer to future phase)
- Email verification / account activation (defer to future phase)
- OAuth/SSO integration (Google, GitHub, etc.) - only email/password for Step 2
- Multi-factor authentication (MFA/2FA) - defer to future phase
- Role-based access control (RBAC) or permissions beyond user isolation - defer to future phase
- Account deletion or user profile management - defer to future phase
- Rate limiting or brute-force protection - defer to security hardening phase
- Refresh token rotation or revocation lists (stateless JWT only for Step 2)
- Comprehensive audit logging - basic logging only for Step 2
- Frontend UI redesign or branding - minimal login/register forms only

## Dependencies *(mandatory)*

### External Dependencies

- **Better Auth library**: npm package for Next.js authentication flows and JWT issuance
- **Next.js 14+ App Router**: Frontend framework with App Router architecture required for Better Auth integration
- **PyJWT library**: Python package for JWT encoding/decoding in FastAPI backend
- **Shared secret key (BETTER_AUTH_SECRET)**: Must be identical in both Next.js and FastAPI environments for JWT signature verification

### Internal Dependencies

- **Existing task REST API** (from Phase II Step 1): All 6 endpoints must remain functional after adding authentication layer
- **PostgreSQL database with tasks table**: Schema includes user_id column for user isolation (already implemented in Step 1)
- **FastAPI middleware system**: Used to inject JWT verification before route handlers
- **Next.js API routes**: Used for Better Auth authentication endpoints

### Assumptions

- Next.js frontend and FastAPI backend can share environment variable (BETTER_AUTH_SECRET) securely
- Users have modern browsers supporting cookies or localStorage for token storage
- HTTPS is used in production to protect JWT tokens in transit (development may use HTTP)
- JWT token size under 1KB is acceptable for HTTP headers
- One-hour token expiration provides acceptable balance between security and user experience
- Users tolerate being logged out after 1 hour of inactivity (or will use refresh tokens)
- Email addresses are unique identifiers for users (Better Auth enforces this)
- Password strength validation (minimum 8 characters) provides adequate security for MVP
- Better Auth's default JWT implementation is compatible with PyJWT library
- Backend can verify JWT signatures synchronously without performance degradation (sub-5ms target)

## Open Questions *(optional)*

No critical open questions remaining - feature is well-defined with reasonable defaults applied.

Minor considerations documented for planning phase:
- Should we use HttpOnly cookies or localStorage for JWT storage? (Default: HttpOnly cookies for better XSS protection)
- Should refresh tokens have separate longer expiration than access tokens? (Default: Single token type for Step 2 simplicity)
- Should we implement token revocation for logout? (Default: No - stateless design, client-side token deletion only)
