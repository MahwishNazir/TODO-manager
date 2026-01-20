# ADR-004: Stateless JWT Authentication

**Status**: Accepted
**Date**: 2026-01-12
**Feature**: 003-jwt-auth (Phase II Step 2)
**Decision Makers**: Claude Code Agent

## Context

The FastAPI backend must authenticate users on every API request. The authentication mechanism must:
- Identify the user making the request (extract user_id for database filtering)
- Verify the user has a valid session (not expired, not forged)
- Enforce user isolation (prevent cross-user data access)
- Scale horizontally (multiple backend instances without shared state)
- Meet performance requirements (<10ms for unauthorized request rejection, <5ms for JWT validation)

Two primary authentication paradigms:
1. **Session-Based**: Backend stores session state (in-memory, Redis, database); client sends session ID
2. **Stateless (JWT-Based)**: Backend validates self-contained token; no session storage

Phase II architectural requirements:
- **Stateless Backend** (Specification FR-009): Backend must not maintain session state
- **Horizontal Scalability** (Constitution Principle VII): Backend must scale without session synchronization
- **REST API Principles**: Statelessness is a core REST constraint (each request contains complete authentication context)

## Decision Drivers

1. **Specification Mandate**: FR-009 explicitly requires "Backend MUST remain stateless (no session storage)"
2. **Performance**: <10ms unauthorized rejection (fast-fail), <5ms token validation
3. **Scalability**: Support 1000+ concurrent authenticated users with horizontal scaling
4. **Simplicity**: Avoid session storage infrastructure (Redis, database sessions, in-memory store)
5. **REST Compliance**: Maintain stateless design principle
6. **Development Velocity**: Minimize backend complexity for Phase II MVP

## Alternatives Considered

### Option 1: Session-Based Authentication (Database Sessions)
**Pros**:
- **Token Revocation**: Can invalidate sessions immediately (logout, password change, admin ban)
- **Session Metadata**: Can track last_activity, IP address, user_agent per session
- **Active Session Management**: Can list/revoke all user sessions (security feature)
- **Audit Trail**: Database log of all authentication events

**Cons**:
- **Violates FR-009**: Backend maintains session state (disqualifying)
- **Database Query Per Request**: Every API call requires session lookup
  - Adds 5-20ms latency (database round-trip)
  - Fails <10ms unauthorized rejection goal
  - Scales poorly (database becomes bottleneck)
- **Horizontal Scaling Complexity**: Multiple backend instances need shared session store
  - Requires PostgreSQL session table or external Redis
  - Session synchronization overhead
- **Session Cleanup**: Requires background job to delete expired sessions (cron task)
- **CRUD Overhead**: Create session on login, update on activity, delete on logout

**Rejected**: Violates stateless requirement; performance penalty; complexity exceeds Phase II needs.

### Option 2: Session-Based Authentication (Redis/Memcached)
**Pros**:
- **Faster Than Database**: In-memory lookup (1-5ms vs 5-20ms)
- **Token Revocation**: Can delete sessions from Redis immediately
- **TTL Support**: Redis auto-expires sessions (no cleanup job needed)
- **Popular Pattern**: Widely used in industry (proven at scale)

**Cons**:
- **Violates FR-009**: Backend maintains session state (disqualifying)
- **Infrastructure Dependency**: Requires Redis deployment
  - Additional operational complexity (monitoring, backups, failover)
  - Cost (hosted Redis on Neon/Upstash or self-hosted)
  - Single point of failure (if Redis down, all sessions invalid)
- **Network Latency**: Every API request makes Redis call
  - Adds 1-5ms latency (still measurable overhead)
- **Horizontal Scaling**: Requires Redis cluster for high availability
- **Overkill for Phase II**: Session revocation not in scope (FR out-of-scope list)

**Rejected**: Violates stateless requirement; adds infrastructure complexity; benefits not needed for Phase II.

### Option 3: Session-Based Authentication (In-Memory Sessions)
**Pros**:
- **Fastest Validation**: In-process memory lookup (<1ms)
- **No External Dependencies**: No Redis/database needed
- **Simple Implementation**: Python dictionary with session_id keys

**Cons**:
- **Violates FR-009**: Backend maintains session state (disqualifying)
- **Non-Scalable**: Sessions stored only on single backend instance
  - Load balancer must use sticky sessions (couples client to specific backend)
  - Cannot add/remove backend instances dynamically
  - Server restart wipes all sessions (users logged out)
- **Memory Leak Risk**: Unbounded session growth without cleanup
- **No Persistence**: Sessions lost on backend restart/redeploy

**Rejected**: Violates stateless requirement; catastrophic scalability limitations; unacceptable for production.

### Option 4: Stateless JWT Authentication (Chosen)
**Pros**:
- **Meets FR-009**: Backend is completely stateless (no session storage)
- **Performance**: <5ms JWT verification (meets all performance goals)
  - No database query
  - No Redis lookup
  - No network calls
  - Pure cryptographic operation (HMAC-SHA256)
- **Horizontal Scalability**: Any backend instance can verify any token
  - No session synchronization
  - Load balancer can route to any instance
  - Add/remove instances dynamically (auto-scaling)
- **Simplicity**: No session infrastructure (Redis, database tables, cleanup jobs)
- **REST Compliance**: Stateless design aligns with REST principles
- **Self-Contained**: Token contains all authentication context (user_id, email, expiration)

**Cons**:
- **Cannot Revoke Tokens**: Tokens valid until expiration (no early invalidation)
  - **Mitigation**: Short expiration (1 hour limits damage window)
  - **Acceptable**: Logout is client-side only (clear cookie/sessionStorage)
  - **Future**: Can add token revocation list in Phase II Step 3+ if needed
- **Token Size**: JWT tokens larger than session IDs (500-800 bytes vs 32 bytes)
  - **Acceptable**: <1KB fits in HTTP headers easily
- **Clock Skew**: Backend and frontend clocks must be synchronized (±10 seconds tolerance)
  - **Acceptable**: NTP ensures clock synchronization in production

**Accepted**: Only option that meets FR-009; best performance and scalability; adequate security for Phase II.

## Decision

**We will use stateless JWT authentication with no backend session storage.**

### Implementation Details

#### Backend (FastAPI Middleware)

```python
# backend/src/auth/jwt_handler.py
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel

security = HTTPBearer()

class CurrentUser(BaseModel):
    """User context extracted from JWT token."""
    user_id: str
    email: str

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> CurrentUser:
    """
    Verify JWT token and extract user context.
    No database lookup, no session storage - fully stateless.
    """
    token = credentials.credentials

    try:
        # Verify token signature and claims (stateless operation)
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            audience="todo-api",
            issuer="todo-app",
            leeway=10,  # ±10 seconds clock skew tolerance
        )

        # Extract user context from token claims
        return CurrentUser(
            user_id=payload["sub"],
            email=payload["email"]
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

#### Backend (Protected Endpoints)

```python
# backend/src/api/tasks.py
from fastapi import APIRouter, Depends
from src.auth.jwt_handler import get_current_user, CurrentUser

router = APIRouter()

@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user)  # JWT validation
):
    """
    Get all tasks for authenticated user.
    User isolation enforced by comparing path user_id with JWT user_id.
    """
    # Enforce user isolation (user can only access own tasks)
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Query database filtered by user_id (no session lookup needed)
    tasks = await task_service.get_tasks_by_user(current_user.user_id)
    return tasks
```

#### No Session Storage

```python
# ❌ NO SESSION TABLE IN DATABASE
# No `sessions` table with (session_id, user_id, expires_at) columns

# ❌ NO REDIS/MEMCACHED
# No session store infrastructure

# ❌ NO IN-MEMORY SESSIONS
# No `sessions_dict = {}` in backend code

# ✅ ONLY JWT VERIFICATION
# Backend trusts JWT signature; no additional state
```

#### Logout (Client-Side Only)

```typescript
// frontend/src/lib/auth.ts
export async function logout() {
  // Clear client-side storage (no backend session to delete)
  sessionStorage.removeItem('jwt_token');
  document.cookie = 'todo-session=; Max-Age=0; path=/';

  // Redirect to login page
  window.location.href = '/login';
}
```

## Consequences

### Positive

1. **Stateless Backend** (FR-009 Compliance):
   - No session storage
   - No database session queries
   - No Redis dependency
   - No session cleanup jobs
2. **Performance**:
   - <5ms JWT verification (cryptographic operation only)
   - <10ms unauthorized rejection (fast-fail if no/invalid token)
   - No database/Redis round-trips on every request
3. **Horizontal Scalability**:
   - Any backend instance can verify any token (no session affinity)
   - Load balancer can use round-robin routing
   - Add/remove instances dynamically (auto-scaling)
   - Server restart has no impact on sessions (tokens remain valid)
4. **Simplicity**:
   - No session infrastructure to deploy/monitor/backup
   - No session synchronization logic
   - Fewer failure modes (no Redis downtime, no database connection pool exhaustion)
5. **REST Compliance**:
   - Stateless design aligns with REST architectural constraints
   - Each request self-contained (no server-side session context)
6. **Development Velocity**:
   - Less code to write (no session CRUD)
   - Easier testing (no session mocking)
   - Faster CI/CD (no Redis in test environment)

### Negative

1. **No Token Revocation**:
   - Cannot invalidate tokens before expiration
   - Logout is client-side only (backend cannot force logout)
   - Compromised tokens valid for full 1-hour lifetime
   - **Mitigation**: Short expiration (1 hour) limits damage window
   - **Future**: Can add token revocation list in Phase II Step 3+ if requirement emerges
2. **No Session Metadata**:
   - Cannot track last_activity, IP address, user_agent per session
   - Cannot implement "last seen" feature without additional database tracking
   - **Acceptable**: Session metadata not in Phase II scope
3. **No Active Session Management**:
   - Users cannot view "active sessions" list (multiple devices)
   - Cannot revoke individual device sessions
   - **Acceptable**: Multi-device session management deferred to future phases
4. **Clock Skew Sensitivity**:
   - Token expiration depends on synchronized clocks
   - If backend clock ahead of frontend by >1 hour, tokens rejected as expired
   - **Mitigation**: NTP synchronization (standard in cloud environments); ±10 seconds leeway

### Neutral

1. **Token Refresh**: Frontend must refresh tokens before expiration (proactive refresh at 50 minutes)
2. **Audit Trail**: Can still log authentication events (login, failed attempts) without session storage
3. **Security Posture**: Stateless JWT is industry-standard pattern (used by GitHub, Stripe, AWS)

## Security Analysis

### Threat Model

| Scenario | Session-Based | Stateless JWT | Winner |
|---|---|---|---|
| **Token Stolen (XSS)** | Revoke session immediately | Token valid until expiry (max 1 hour) | Session |
| **Backend Compromise** | Attacker can query sessions | Attacker can forge tokens (if secret leaked) | Tie |
| **Logout Security** | Backend deletes session (enforced) | Client clears token (voluntary) | Session |
| **Horizontal Scaling** | Requires session store (Redis) | No shared state needed | JWT |
| **Performance** | 1-20ms session lookup | <5ms signature verification | JWT |
| **Availability** | Redis/DB dependency | No external dependencies | JWT |

### Why Stateless is Adequate for Phase II

1. **Threat Prioritization**: XSS is primary threat (mitigated by HttpOnly cookies), not token compromise
2. **Short Expiration**: 1-hour lifetime limits damage window for stolen tokens
3. **User Isolation**: Stolen token only grants access to single user's tasks (no privilege escalation)
4. **Specification Alignment**: FR-009 explicitly mandates stateless backend
5. **Migration Path**: Can add token revocation list in Phase III if threat model changes

### Token Revocation Alternatives (Out of Scope for Phase II)

If token revocation becomes required in future phases:
- **Option A**: Add `revoked_tokens` database table (check on every request)
  - Violates stateless principle but provides revocation
- **Option B**: Use short-lived access tokens (5 min) + long-lived refresh tokens (7 days)
  - Revoke refresh tokens only (access tokens expire quickly)
- **Option C**: Use JWT ID (`jti` claim) + revocation list (Redis cache)
  - Hybrid approach: stateless for most tokens, stateful for revoked subset

## Compliance

- ✅ **Constitution Principle VII**: Resource Optimization - Stateless design enables horizontal scalability
- ✅ **Specification FR-009**: "Backend MUST remain stateless (no session storage)" - Directly mandated
- ✅ **Specification SC-02**: "Unauthorized requests rejected within 10ms" - JWT fast-fail meets goal
- ✅ **Specification SC-05**: "Backend stateless to support horizontal scaling" - Core requirement
- ✅ **Specification SC-08**: "Average JWT validation time <5ms" - Stateless verification is fastest option

## References

- **Feature Specification**: [specs/003-jwt-auth/spec.md](../../specs/003-jwt-auth/spec.md)
- **Implementation Plan**: [specs/003-jwt-auth/plan.md](../../specs/003-jwt-auth/plan.md)
- **Research**: [specs/003-jwt-auth/research.md](../../specs/003-jwt-auth/research.md) (Decision 3: JWT Middleware)
- **REST Architectural Constraints**: https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm (external)
- **JWT Best Practices**: https://datatracker.ietf.org/doc/html/rfc8725 (external)

## Review

- **Approved By**: User (via specification mandating stateless backend)
- **Review Date**: 2026-01-12
- **Next Review**: After Phase II Step 2 implementation (evaluate if token revocation needed)
