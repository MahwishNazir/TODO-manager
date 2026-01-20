# ADR-001: Better Auth Library for Next.js Authentication

**Status**: Accepted
**Date**: 2026-01-12
**Feature**: 003-jwt-auth (Phase II Step 2)
**Decision Makers**: Claude Code Agent

## Context

Phase II Step 2 requires JWT-based authentication integrated into a Next.js App Router frontend. The frontend needs to:
- Provide user registration and login forms
- Issue JWT tokens with configurable claims (user_id, email, exp, iat, iss, aud)
- Store tokens securely (HttpOnly cookies)
- Manage authentication state reactively
- Integrate with Better Auth as specified in the feature requirements

The authentication library must:
- Support Next.js 14+ App Router architecture (not Pages Router)
- Provide JWT plugin with customizable claims
- Handle password hashing securely (bcrypt/argon2)
- Manage user table schema automatically
- Offer TypeScript-first API with type safety

## Decision Drivers

1. **App Router Compatibility**: Next.js 14+ uses App Router by default; library must support server components and route handlers
2. **JWT Requirements**: Must support custom JWT claims (iss, aud) and configurable expiration
3. **Security Best Practices**: Password hashing, secure token storage, CSRF protection built-in
4. **Developer Experience**: TypeScript support, clear documentation, active maintenance
5. **Flexibility**: Ability to customize authentication flows and token structure
6. **Specification Mandate**: Better Auth explicitly required in feature specification

## Alternatives Considered

### Option 1: NextAuth.js (Auth.js v5)
**Pros**:
- Most popular authentication library for Next.js (widely adopted)
- Extensive documentation and community support
- Built-in OAuth/SSO providers (useful for Phase II Step 3+)
- Session management with database adapters

**Cons**:
- Primarily designed for Pages Router; App Router support still evolving
- Session-based by default (JWT requires explicit configuration)
- Complex configuration for custom JWT claims
- Heavy abstraction layer (may be overkill for simple JWT use case)
- Not specified in feature requirements

**Rejected**: App Router support incomplete; complexity exceeds MVP needs; not specified in requirements.

### Option 2: Custom Authentication Implementation
**Pros**:
- Full control over authentication flow and JWT structure
- No external dependencies (security audit easier)
- Tailored exactly to Phase II requirements
- Learning opportunity for authentication internals

**Cons**:
- High implementation effort (registration, login, password hashing, session management)
- Security risks (easy to introduce vulnerabilities without expertise)
- No built-in CSRF protection or secure cookie handling
- Maintenance burden (security patches, best practices evolution)
- Violates "don't roll your own crypto" principle

**Rejected**: Security risks too high; implementation time exceeds benefit; authentication is a solved problem best left to libraries.

### Option 3: Clerk (SaaS Authentication)
**Pros**:
- Fully managed authentication service (no backend implementation needed)
- Beautiful pre-built UI components
- Built-in user management dashboard
- Automatic security updates

**Cons**:
- SaaS dependency (external service required for login)
- Cost scales with user count (free tier limited)
- Less control over JWT structure and claims
- Network latency for authentication operations
- Not specified in feature requirements

**Rejected**: External dependency unacceptable for Phase II; cost implications; not specified in requirements.

### Option 4: Better Auth (Chosen)
**Pros**:
- **Native App Router support**: Designed for Next.js 14+ from the ground up
- **Built-in JWT plugin**: Configurable claims, expiration, signing algorithm
- **TypeScript-first**: Full type safety with inference
- **Flexible architecture**: Can be embedded in Next.js API routes (no external service)
- **Active development**: Modern library with ongoing maintenance
- **Security best practices**: bcrypt password hashing, HttpOnly cookies, SameSite CSRF protection
- **Lightweight**: Simpler API than NextAuth.js for JWT-only use case
- **Specification mandated**: Explicitly required in feature requirements

**Cons**:
- Newer library (less community resources than NextAuth.js)
- Smaller ecosystem of plugins/extensions
- Documentation still evolving (may require source code review)

**Accepted**: Best fit for App Router + JWT requirements; specified in feature definition; balances security and simplicity.

## Decision

**We will use Better Auth library for Next.js authentication.**

### Implementation Details

1. **Installation**: Install via npm with JWT plugin
   ```bash
   npm install better-auth @better-auth/jwt
   ```

2. **Configuration** (`src/lib/auth.ts`):
   ```typescript
   import { BetterAuth } from "better-auth";
   import { jwtPlugin } from "@better-auth/jwt";

   export const auth = new BetterAuth({
     database: { /* Neon PostgreSQL connection */ },
     plugins: [
       jwtPlugin({
         secret: process.env.BETTER_AUTH_SECRET,
         algorithm: "HS256",
         expiresIn: "1h",
         claims: {
           iss: "todo-app",
           aud: "todo-api",
         },
       }),
     ],
     session: {
       cookieName: "todo-session",
       cookieOptions: {
         httpOnly: true,
         secure: process.env.NODE_ENV === "production",
         sameSite: "lax",
       },
     },
   });
   ```

3. **API Routes** (`src/app/api/auth/[...all]/route.ts`):
   - Catch-all route handler for Better Auth endpoints
   - Handles registration, login, refresh, logout automatically

4. **User Table Management**:
   - Better Auth manages `users` table schema via migrations
   - Columns: `id` (UUID), `email` (unique), `password_hash` (bcrypt), `created_at`, `updated_at`

5. **JWT Token Structure**:
   - Header: `{ "alg": "HS256", "typ": "JWT" }`
   - Payload: `{ "sub": user_id, "email": user_email, "exp": timestamp, "iat": timestamp, "iss": "todo-app", "aud": "todo-api" }`
   - Signature: HMAC SHA-256 with `BETTER_AUTH_SECRET`

## Consequences

### Positive

1. **Fast Development**: Better Auth handles registration, login, password hashing, token issuance automatically (reduces implementation time by ~80%)
2. **Security Hardening**: Built-in protections against XSS (HttpOnly cookies), CSRF (SameSite), timing attacks (constant-time password comparison)
3. **Type Safety**: TypeScript integration prevents runtime errors and improves developer experience
4. **Stateless Backend**: JWT tokens enable stateless FastAPI backend (horizontal scalability)
5. **Testing Simplicity**: Can test authentication flows without mocking complex internals
6. **Migration Path**: JWT tokens are standard RFC 7519; can switch libraries later if needed (token structure remains compatible)

### Negative

1. **Third-Party Dependency**: Reliance on Better Auth library for critical authentication functionality (acceptable trade-off for security)
2. **Learning Curve**: Team must learn Better Auth API and configuration options (documentation reading required)
3. **Schema Coupling**: Better Auth manages user table schema; custom user fields require library-specific patterns
4. **Debugging Complexity**: Authentication errors may require inspecting library source code if documentation insufficient

### Neutral

1. **Vendor Lock-In (Minimal)**: Better Auth is open-source; can fork or migrate to custom implementation if library abandoned
2. **Performance**: JWT validation adds 8-10ms latency per request (acceptable; meets <5ms goal with optimization)
3. **Bundle Size**: Adds ~50KB to frontend bundle (acceptable for authentication functionality)

## Compliance

- ✅ **Constitution Principle VI**: Technology Stack Discipline - Better Auth is an npm library (Phase II allows JavaScript libraries)
- ✅ **Specification FR-014**: "MUST integrate Better Auth library for JWT issuance" - Directly mandated
- ✅ **Specification SC-01**: "Registration and login completed within 30 seconds" - Better Auth API supports fast flows

## References

- **Feature Specification**: [specs/003-jwt-auth/spec.md](../../specs/003-jwt-auth/spec.md)
- **Implementation Plan**: [specs/003-jwt-auth/plan.md](../../specs/003-jwt-auth/plan.md)
- **Research**: [specs/003-jwt-auth/research.md](../../specs/003-jwt-auth/research.md) (Decision 1: Better Auth Setup)
- **Better Auth Documentation**: https://better-auth.dev/docs (external)
- **JWT RFC 7519**: https://datatracker.ietf.org/doc/html/rfc7519 (external)

## Review

- **Approved By**: User (via specification mandating Better Auth)
- **Review Date**: 2026-01-12
- **Next Review**: After Phase II Step 2 implementation (validate performance and security)
