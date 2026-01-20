# Implementation Plan: JWT Authentication with Better Auth

**Branch**: `003-jwt-auth` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-jwt-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Secure the existing REST API with JWT-based authentication issued by Better Auth on the Next.js frontend and verified by the FastAPI backend. All 6 existing task management endpoints will require valid JWT tokens in the Authorization header. User isolation will be enforced automatically by extracting user_id from the JWT token's `sub` claim. The backend remains completely stateless (no session storage), and all existing API contracts (paths, request/response schemas) remain unchanged to ensure zero breaking changes.

**Technical Approach**:
- **Frontend**: Better Auth library with JWT plugin integrated into Next.js App Router
- **Backend**: PyJWT library with FastAPI HTTPBearer dependency injection for JWT verification
- **Shared Secret**: HS256 algorithm using BETTER_AUTH_SECRET environment variable synchronized between frontend and backend
- **Token Storage**: HttpOnly cookies with sessionStorage cache for optimal security
- **Token Lifecycle**: 1-hour expiration with proactive refresh at 50 minutes
- **User Isolation**: Automatic filtering of database queries by JWT user_id (no path parameter changes required)

## Technical Context

**Language/Version**:
- Python 3.11+ (backend)
- TypeScript 5.x with Node.js 18+ (frontend)

**Primary Dependencies**:
- **Backend**: FastAPI 0.115+, PyJWT 2.10+, SQLModel 0.0.22+, Pydantic 2.x
- **Frontend**: Next.js 14+ (App Router), Better Auth (latest), React 18+
- **Shared**: PostgreSQL client libraries (asyncpg for backend, pg for frontend)

**Storage**:
- **Database**: Neon PostgreSQL (serverless) - existing from Step 1
- **Tables**:
  - `users` (Better Auth managed - new for Step 2)
  - `tasks` (existing from Step 1, no schema changes)
- **Indexes**: `ix_tasks_user_id` (existing)

**Testing**:
- **Backend**: pytest with pytest-asyncio for async tests, httpx for API testing
- **Frontend**: Jest with React Testing Library, Playwright for E2E tests
- **Contract Testing**: OpenAPI validation using schemas in `contracts/` directory

**Target Platform**:
- **Backend**: Linux server (containerized FastAPI with uvicorn)
- **Frontend**: Next.js SSR/SSG deployed on Vercel or similar platform
- **Database**: Neon PostgreSQL (cloud-native, serverless)
- **Production**: HTTPS required for secure cookie transmission

**Project Type**: Web application (Next.js frontend + FastAPI backend)

**Performance Goals**:
- JWT verification: <5ms average per request (PyJWT synchronous validation)
- Authentication flow: <30 seconds from landing to authenticated dashboard
- Unauthorized request rejection: <10ms (fast-fail on missing/invalid token)
- Token refresh: <200ms end-to-end
- Concurrent authenticated users: 1000+ (stateless backend enables horizontal scaling)

**Constraints**:
- **Zero Breaking Changes**: All Step 1 API contracts (paths, schemas, status codes) must remain unchanged
- **Stateless Backend**: No session storage, no in-memory state, no JWT revocation lists
- **Backward Compatibility**: Existing API consumers can migrate by only adding Authorization header
- **User Isolation**: Users can NEVER access other users' tasks (enforced at middleware level)
- **Token Size**: JWT payload <1KB for HTTP header compatibility
- **Clock Skew Tolerance**: ±10 seconds for exp/iat validation

**Scale/Scope**:
- **User Accounts**: Unlimited (Better Auth handles user management)
- **Concurrent Sessions**: 1000+ authenticated users simultaneously
- **API Endpoints**: 6 existing task endpoints + 4 new auth endpoints
- **JWT Claims**: 6 required claims (sub, email, exp, iat, iss, aud)
- **Token Expiration**: 1 hour for access tokens
- **Frontend Routes**: 2 new pages (login, register) + protected task pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Single Source of Truth
- **Status**: PASS
- Constitution location: `.specify/memory/constitution.md`
- Phase II technologies defined: FastAPI + Next.js + SQLModel + Neon DB + JWT authentication
- This feature implements JWT authentication as specified in Phase II requirements

### ✅ Principle II: Spec-Driven Development
- **Status**: PASS
- Specification created: `specs/003-jwt-auth/spec.md` (193 lines, 4 user stories, 18 functional requirements)
- Planning artifacts: `research.md`, `data-model.md`, `quickstart.md`, `contracts/`
- Next phase: `/sp.tasks` will create tasks.md with testable task breakdown

### ✅ Principle III: Test-First Development (TDD)
- **Status**: PASS (will be enforced in tasks.md)
- TDD workflow: RED → GREEN → REFACTOR
- Test types planned:
  - Contract tests: JWT signature verification, claim validation
  - Integration tests: Authentication flow end-to-end
  - Unit tests: JWT parsing, user extraction, error handling
- Coverage target: Backend >80%, Frontend >70%

### ✅ Principle IV: Code Organization by Feature
- **Status**: PASS
- Feature isolation maintained:
  - Authentication code: `backend/src/auth/`, `frontend/src/lib/auth.ts`
  - Task endpoints: Existing `backend/src/api/tasks.py` (updated with JWT dependency)
  - No cross-feature coupling (task service remains independent of auth implementation)

### ✅ Principle V: Immutability and State Management
- **Status**: PASS
- JWT tokens are immutable (signed, stateless)
- Backend remains stateless (no session mutation)
- Frontend state: Better Auth manages session state reactively
- Database: Task records have updated_at timestamps for change tracking

### ✅ Principle VI: Technology Stack Discipline
- **Status**: PASS
- Phase II Stack: FastAPI ✓, Next.js ✓, SQLModel ✓, Neon PostgreSQL ✓
- Authentication: JWT-based ✓ (as specified in constitution)
- Password Hashing: Better Auth uses bcrypt by default ✓
- No new technologies beyond Better Auth (npm library) and PyJWT (Python library)

### ✅ Principle VII: Resource Optimization
- **Status**: PASS
- JWT verification: <5ms (synchronous, no external calls)
- Stateless backend: Horizontal scalability without session synchronization
- HttpOnly cookies: Minimal bandwidth overhead
- Token size: <1KB (6 claims only)
- Auto-refresh: Proactive (reduces failed requests)

**Overall Constitution Compliance**: ✅ ALL 7 PRINCIPLES PASS

## Project Structure

### Documentation (this feature)

```text
specs/003-jwt-auth/
├── spec.md                             # Feature specification (4 user stories, 18 requirements)
├── plan.md                             # This file (implementation plan)
├── research.md                         # Technical research (Better Auth, PyJWT, architecture)
├── data-model.md                       # Entity definitions (User, JWT, Task)
├── quickstart.md                       # Setup and testing guide
├── contracts/                          # API contracts
│   ├── authentication-api.yaml         # Auth endpoints (register, login, refresh, logout)
│   └── protected-tasks-api.yaml        # JWT-protected task endpoints
├── checklists/
│   └── requirements.md                 # Specification quality validation (all PASS)
└── tasks.md                            # NOT YET CREATED (Phase 2: /sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── auth/                           # NEW: Authentication module
│   │   ├── __init__.py
│   │   └── jwt_handler.py              # JWT verification dependency
│   ├── api/
│   │   └── tasks.py                    # UPDATED: Add CurrentUser dependency
│   ├── models/
│   │   ├── task.py                     # UNCHANGED: Existing SQLModel
│   │   └── schemas.py                  # UNCHANGED: Existing Pydantic schemas
│   ├── services/
│   │   └── task_service.py             # UNCHANGED: Existing business logic
│   ├── config.py                       # UPDATED: Add JWT settings
│   ├── database.py                     # UNCHANGED: Existing DB connection
│   └── main.py                         # UPDATED: CORS allow_credentials=True
├── tests/
│   ├── contract/                       # NEW: JWT contract tests
│   │   └── test_jwt_validation.py
│   ├── integration/
│   │   ├── test_api_tasks.py           # UPDATED: Add JWT authentication
│   │   └── test_auth_flow.py           # NEW: End-to-end auth testing
│   └── unit/
│       ├── test_task.py                # UNCHANGED: Existing unit tests
│       └── test_jwt_handler.py         # NEW: JWT parsing unit tests
├── .env.example                        # UPDATED: Add BETTER_AUTH_SECRET
├── requirements.txt                    # UPDATED: Add PyJWT==2.10.1
└── README.md                           # UPDATED: Auth setup instructions

frontend/                               # NEW: Next.js frontend (not in Step 1)
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts        # Better Auth API routes
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx            # Login form
│   │   │   └── register/
│   │   │       └── page.tsx            # Registration form
│   │   ├── (protected)/
│   │   │   └── tasks/
│   │   │       └── page.tsx            # Task management UI
│   │   └── layout.tsx                  # Root layout with AuthProvider
│   ├── components/
│   │   ├── AuthProvider.tsx            # Better Auth context
│   │   ├── LoginForm.tsx               # Login UI component
│   │   └── RegisterForm.tsx            # Registration UI component
│   ├── hooks/
│   │   └── useTokenRefresh.ts          # Auto-refresh hook
│   ├── lib/
│   │   ├── auth.ts                     # Better Auth configuration
│   │   └── api-client.ts               # Backend API client with JWT injection
│   └── middleware.ts                   # Route protection
├── tests/
│   ├── e2e/
│   │   └── auth-flow.spec.ts           # Playwright E2E tests
│   └── unit/
│       └── api-client.test.ts          # API client unit tests
├── .env.local.example                  # Environment template
├── next.config.js                      # Next.js configuration
├── package.json                        # Dependencies (Better Auth)
└── README.md                           # Frontend setup instructions

shared/                                 # OPTIONAL: Shared TypeScript types
└── types/
    └── api.ts                          # API request/response types (mirrored from backend schemas)
```

**Structure Decision**: Web application structure (Option 2) selected. This is a full-stack web application with:
- **Backend**: FastAPI REST API with JWT verification middleware
- **Frontend**: Next.js App Router with Better Auth for JWT issuance
- **Separation**: Backend and frontend are independent projects with clear API contracts
- **Existing Code**: Backend from Step 1 (minimal updates), frontend is new for Step 2

The structure follows the constitution's Phase II architecture and maintains clear separation of concerns between authentication logic, API endpoints, and business logic.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All 7 constitution principles pass without justification needed.

This table remains empty because:
- Technology stack matches Phase II specification (no additional projects/frameworks)
- Code organization follows feature-based structure (auth module isolated)
- No architectural patterns beyond REST API + JWT (no repository abstraction, no event sourcing)
- Stateless design eliminates session management complexity

## Architecture Decision Records (ADRs)

The following architectural decisions were made during research and design phases. Detailed ADRs will be created in `history/adr/` directory:

### ADR-001: Better Auth vs NextAuth.js vs Custom Auth
- **Decision**: Use Better Auth library for Next.js authentication
- **Context**: Need JWT issuance on Next.js App Router frontend
- **Rationale**:
  - Native App Router support (NextAuth.js primarily Pages Router)
  - Built-in JWT plugin with configurable claims
  - Active maintenance and TypeScript-first design
  - Simpler than custom implementation (security best practices baked in)
- **Consequences**:
  - Dependency on third-party library (acceptable for authentication)
  - Better Auth manages user table schema (reduces custom code)
  - Migration path exists if switching libraries later (JWT tokens are standard)

### ADR-002: HttpOnly Cookies vs localStorage for Token Storage
- **Decision**: Use HttpOnly cookies as primary storage with sessionStorage cache
- **Context**: Need secure client-side JWT token storage
- **Rationale**:
  - HttpOnly flag prevents JavaScript XSS attacks accessing token
  - SameSite=Lax provides CSRF protection
  - Secure flag ensures HTTPS-only transmission in production
  - sessionStorage cache enables Authorization header construction without cookie parsing
- **Consequences**:
  - Requires HTTPS in production (acceptable security requirement)
  - CORS must allow credentials (configured in backend)
  - Token not accessible from JavaScript (trade-off for security)

### ADR-003: HS256 vs RS256 for JWT Signatures
- **Decision**: Use HS256 (HMAC SHA-256) symmetric encryption
- **Context**: Need JWT signature algorithm for token validation
- **Rationale**:
  - Simpler key management (single shared secret vs public/private key pair)
  - Faster verification (<5ms vs ~20ms for RS256)
  - Adequate security for monolithic application (backend verifies tokens it trusts frontend to issue)
  - Meets performance goal: <5ms JWT verification
- **Consequences**:
  - Shared secret must be synchronized between frontend and backend (acceptable with environment variables)
  - No public key distribution (not needed for internal verification)
  - Migration to RS256 possible later if microservices require it

### ADR-004: Stateless JWT vs Session-Based Authentication
- **Decision**: Use stateless JWT authentication (no backend session storage)
- **Context**: Need authentication mechanism for REST API
- **Rationale**:
  - Horizontal scalability without session synchronization (any backend instance can validate any token)
  - Simpler backend implementation (no Redis/database session store)
  - Meets "stateless backend" requirement in spec FR-009
  - Aligns with REST API principles
- **Consequences**:
  - Cannot revoke tokens before expiration (mitigated by 1-hour expiration)
  - Token refresh requires valid unexpired token (no refresh tokens in Step 2)
  - Logout is client-side only (acceptable for MVP)

### ADR-005: Proactive Token Refresh vs Reactive Refresh
- **Decision**: Use proactive token refresh (auto-refresh at 50 minutes)
- **Context**: Need token refresh strategy to maintain long sessions
- **Rationale**:
  - Prevents user-facing 401 errors during operations
  - Reduces failed requests requiring retry logic
  - Better user experience (seamless session extension)
  - Frontend can schedule refresh predictably (50 min = 10 min buffer before 1-hour expiry)
- **Consequences**:
  - Frontend runs interval timer (minimal resource impact)
  - Unused sessions still refresh (acceptable trade-off for better UX)
  - Backend receives periodic refresh requests (low overhead)

**ADR Summary**: All decisions prioritize simplicity, security, and performance while maintaining backward compatibility with existing APIs. No decisions violate constitution principles.

## Implementation Phases

### Phase 0: Research ✅ COMPLETED
- **Artifact**: `research.md` (59KB)
- **Decisions Resolved**:
  - Better Auth setup and configuration
  - PyJWT verification patterns
  - JWT structure and claims
  - Token storage strategy
  - Error handling approach
  - Token refresh mechanism
  - Shared secret management
  - Performance optimization techniques

### Phase 1: Design & Contracts ✅ COMPLETED
- **Artifacts**:
  - `data-model.md` - Entity definitions
  - `contracts/authentication-api.yaml` - Auth endpoint contracts
  - `contracts/protected-tasks-api.yaml` - Protected task endpoint contracts
  - `quickstart.md` - Setup and testing guide
- **Agent Context Updated**: CLAUDE.md (technology stack added)

### Phase 2: Tasks Breakdown ⏳ NOT STARTED
- **Command**: `/sp.tasks` (separate command, not part of `/sp.plan`)
- **Output**: `tasks.md` with testable task breakdown
- **Format**: RED-GREEN-REFACTOR phases with acceptance criteria

### Phase 3: Implementation ⏳ NOT STARTED
- **Command**: `/sp.implement` (executes tasks.md)
- **Workflow**: TDD with contract → integration → unit test progression

## Links and References

- **Feature Specification**: [spec.md](./spec.md)
- **Requirements Checklist**: [checklists/requirements.md](./checklists/requirements.md)
- **Research Decisions**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Quickstart Guide**: [quickstart.md](./quickstart.md)
- **API Contracts**: [contracts/](./contracts/)
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)

## Next Steps

1. **Run `/sp.tasks`** to generate testable task breakdown in `tasks.md`
2. **Create ADRs** for the 5 architectural decisions documented above
3. **Run `/sp.implement`** to execute TDD implementation workflow
4. **Test authentication flow** end-to-end using quickstart guide
5. **Verify zero breaking changes** by running existing Step 1 API tests

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks` command to generate implementation tasks.
