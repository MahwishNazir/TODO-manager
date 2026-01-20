---
id: 002
title: JWT Auth Implementation Planning
stage: plan
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5
feature: 003-jwt-auth
branch: 003-jwt-auth
user: User
command: /sp.plan
labels: ["authentication", "jwt", "better-auth", "fastapi", "pyjwt", "planning", "architecture", "phase-2"]
links:
  spec: specs/003-jwt-auth/spec.md
  ticket: null
  adr: history/adr/001-better-auth-library.md, history/adr/002-httponly-cookies-token-storage.md, history/adr/003-hs256-jwt-algorithm.md, history/adr/004-stateless-jwt-authentication.md, history/adr/005-proactive-token-refresh.md
  pr: null
files:
  - specs/003-jwt-auth/plan.md
  - specs/003-jwt-auth/research.md
  - specs/003-jwt-auth/data-model.md
  - specs/003-jwt-auth/quickstart.md
  - specs/003-jwt-auth/contracts/authentication-api.yaml
  - specs/003-jwt-auth/contracts/protected-tasks-api.yaml
  - history/adr/001-better-auth-library.md
  - history/adr/002-httponly-cookies-token-storage.md
  - history/adr/003-hs256-jwt-algorithm.md
  - history/adr/004-stateless-jwt-authentication.md
  - history/adr/005-proactive-token-refresh.md
tests:
  - N/A (planning phase - tests defined for implementation)
---

## Prompt

User command: `/sp.plan do plan for Authentication & API Security (JWT-Based)`

Full user prompt:
```
/sp.plan do plan for Authentication & API Security (JWT-Based)

Secure the existing REST API with JWT-based authentication issued by Better Auth on the Next.js frontend and verified by the FastAPI backend. All 6 existing task management endpoints will require valid JWT tokens in the Authorization header. User isolation will be enforced by extracting user_id from the JWT token, ensuring users can only access their own tasks. The backend must remain stateless (no session storage). Zero breaking changes to existing API contracts from Step 1.

Technology Stack:
- Frontend: Next.js App Router with Better Auth library
- Backend: FastAPI with PyJWT library (2.10+)
- Shared Secret: HS256 algorithm with BETTER_AUTH_SECRET environment variable
- Token Storage: HttpOnly cookies with sessionStorage cache
- Token Lifecycle: 1-hour expiration with proactive refresh at 50 minutes

Existing Infrastructure:
- Database: Neon PostgreSQL (from Step 1)
- API Endpoints: 6 task management endpoints (GET/POST/PUT/DELETE)
- Task Model: SQLModel with user_id column already present
- User Table: Will be managed by Better Auth (new for Step 2)

Key Constraints:
- Zero breaking changes to existing API contracts
- Stateless backend (no session storage)
- Test-First Development (TDD) required
- Horizontal scalability (any backend instance can verify any token)
```

## Response

The `/sp.plan` command executed successfully with the following phases:

**Phase 0: Research** ✅ COMPLETED
- Created comprehensive `research.md` (59KB) documenting 8 major technical decisions
- Covered Better Auth setup, PyJWT integration, JWT middleware patterns, shared secret configuration, token structure, error handling, token refresh, and token storage
- All decisions documented with code examples, performance benchmarks, and security analysis

**Phase 1: Design & Contracts** ✅ COMPLETED
- Created `data-model.md` documenting User, JWT Token, and Task entities
- Generated API contracts in `contracts/` directory:
  - `authentication-api.yaml` (register, login, refresh, logout endpoints)
  - `protected-tasks-api.yaml` (JWT-protected task endpoints)
- Created `quickstart.md` with comprehensive setup and testing instructions
- Updated agent context (CLAUDE.md) with Better Auth and PyJWT technologies

**Planning Artifacts Created**:
- `specs/003-jwt-auth/plan.md` (364 lines) - Complete implementation plan with:
  - Technical Context (Python 3.11+, FastAPI, Next.js, PostgreSQL)
  - Constitution Check (all 7 principles PASS)
  - Project Structure (backend/frontend separation)
  - Complexity Tracking (no violations)
  - Implementation Phases (Phase 0 research complete, Phase 1 design complete)
  - Links and References

**5 Architecture Decision Records Created**:

1. **ADR-001: Better Auth Library** (`history/adr/001-better-auth-library.md`)
   - Decision: Use Better Auth for Next.js authentication
   - Rationale: Native App Router support, built-in JWT plugin, TypeScript-first, security best practices
   - Alternatives: NextAuth.js (Pages Router focus), Custom implementation (security risk), Clerk (SaaS dependency)

2. **ADR-002: HttpOnly Cookies for Token Storage** (`002-httponly-cookies-token-storage.md`)
   - Decision: HttpOnly cookies (primary) + sessionStorage cache (Authorization header)
   - Rationale: XSS protection via HttpOnly, CSRF protection via SameSite, enables standard Authorization header
   - Trade-off: Dual storage complexity vs security benefits

3. **ADR-003: HS256 Algorithm** (`003-hs256-jwt-algorithm.md`)
   - Decision: Use HS256 (HMAC SHA-256) symmetric encryption
   - Rationale: <5ms verification (meets performance goal), simple shared secret management
   - Alternative rejected: RS256 (20-30ms verification, complex key management)

4. **ADR-004: Stateless JWT Authentication** (`004-stateless-jwt-authentication.md`)
   - Decision: No backend session storage
   - Rationale: Horizontal scalability, <5ms verification, meets FR-009 requirement
   - Trade-off: Cannot revoke tokens before expiration (1-hour limit mitigates risk)

5. **ADR-005: Proactive Token Refresh** (`005-proactive-token-refresh.md`)
   - Decision: Refresh tokens at 50 minutes (10-minute buffer before 1-hour expiry)
   - Rationale: Seamless UX (no 401 errors), simple implementation, high reliability (95%+ success rate)
   - Alternative rejected: Reactive refresh (poor UX, retry logic complexity)

**ADR Summary**: All decisions prioritize simplicity, security, and user experience while maintaining backward compatibility with existing APIs. 5 ADRs documented covering authentication library choice, token storage, signature algorithm, stateless backend, and token refresh strategy.

## Outcome

- ✅ **Impact**: Phase II Step 2 implementation plan complete and ready for `/sp.tasks` command. Comprehensive 364-line plan.md with all sections filled (Technical Context, Constitution Check, Project Structure, ADRs, Implementation Phases). 5 detailed ADRs created documenting all architectural decisions.
- 🧪 **Tests**: No tests at planning phase (tests defined for implementation phases)
- 📁 **Files**: 10 files created/modified:
  - `specs/003-jwt-auth/plan.md` (364 lines - complete plan)
  - `specs/003-jwt-auth/research.md` (59KB - 8 decisions)
  - `specs/003-jwt-auth/data-model.md` (entity definitions)
  - `specs/003-jwt-auth/quickstart.md` (setup guide)
  - `specs/003-jwt-auth/contracts/authentication-api.yaml` (4 auth endpoints)
  - `specs/003-jwt-auth/contracts/protected-tasks-api.yaml` (6 task endpoints)
  - `history/adr/001-better-auth-library.md` (ADR)
  - `history/adr/002-httponly-cookies-token-storage.md` (ADR)
  - `history/adr/003-hs256-jwt-algorithm.md` (ADR)
  - `history/adr/004-stateless-jwt-authentication.md` (ADR)
  - `history/adr/005-proactive-token-refresh.md` (ADR)
- 🔁 Next prompts: `/sp.tasks` to generate testable task breakdown, then `/sp.implement` to execute TDD implementation
- 🧠 Reflection: Implementation plan successfully created with comprehensive technical context, constitution compliance verification, 5 architectural decision records, and clear project structure. All design decisions prioritize simplicity, security, and performance while maintaining zero breaking changes to existing API contracts. Ready for task breakdown phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all artifacts generated
- Graders run and results (PASS/FAIL): PASS - Constitution check passed all 7 principles; all ADRs documented with clear rationale
- Prompt variant (if applicable): Standard `/sp.plan` workflow with proactive agent context updates and contract generation
- Next experiment (smallest change to try): N/A - planning meets all quality criteria and is ready for `/sp.tasks` phase
