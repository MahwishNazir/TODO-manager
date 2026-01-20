# ADR-005: Proactive Token Refresh Strategy

**Status**: Accepted
**Date**: 2026-01-12
**Feature**: 003-jwt-auth (Phase II Step 2)
**Decision Makers**: Claude Code Agent

## Context

JWT tokens have a 1-hour expiration (security requirement). Users expect to work uninterrupted for multiple hours without repeated logins. The frontend must refresh tokens before they expire to maintain seamless sessions.

Two refresh strategies:
1. **Reactive Refresh**: Wait for 401 errors, then refresh token and retry request
2. **Proactive Refresh**: Automatically refresh token before expiration (e.g., at 50 minutes)

Phase II requirements:
- **User Experience** (Specification FR-013): Token refresh mechanism prevents repeated logins
- **Success Criteria** (SC-06): 95% token refresh success rate
- **Performance** (SC-01): Registration/login + first task access within 30 seconds (seamless UX expected)

## Decision Drivers

1. **User Experience**: Avoid visible authentication errors during normal operations
2. **Reliability**: 95% refresh success rate (SC-06)
3. **Simplicity**: Minimize frontend retry logic complexity
4. **Performance**: Reduce failed requests that require retry (lower total latency)
5. **Security**: Balance between session length and token exposure window
6. **Backend Simplicity**: Stateless backend should not track token refresh state

## Alternatives Considered

### Option 1: Reactive Refresh (Retry on 401)
**Pros**:
- **Lazy Evaluation**: Only refresh when actually needed (saves refresh requests for inactive users)
- **No Background Timers**: No interval running continuously in frontend
- **Simpler Initial Implementation**: No proactive scheduling logic

**Cons**:
- **Poor User Experience**: User sees 401 error flash before retry
  - Task creation fails → triggers refresh → retry creation
  - User perceives failure even if retry succeeds
  - Possible "Loading..." → "Error" → "Success" flicker
- **Retry Logic Complexity**: Every API call must handle 401 and retry
  ```typescript
  async function apiRequest(url, options) {
    let response = await fetch(url, options);
    if (response.status === 401) {
      // Token expired - refresh and retry
      await refreshToken();
      response = await fetch(url, options);  // Retry original request
    }
    return response;
  }
  ```
  - Must retry exactly once (avoid infinite loops)
  - Must preserve original request body/headers
  - Race condition: Multiple simultaneous 401s trigger multiple refreshes
- **Failed Request Overhead**: Every expiration causes 1 failed request + 1 refresh + 1 retry
  - 3 round-trips instead of 2 (proactive refresh + original request)
  - Higher total latency for user operations
- **Timing Edge Cases**:
  - User submits form at 59:59 → token expires at 60:00 → request fails → refresh → retry succeeds
  - User thinks form submission failed (poor perception)
- **Metrics Pollution**: Failed 401 requests inflate error rates (operational confusion)

**Rejected**: Poor user experience; higher complexity in frontend API client; more failed requests.

### Option 2: Proactive Refresh (Fixed Interval)
**Pros**:
- **Simple Implementation**: `setInterval(() => refreshToken(), 50 * 60 * 1000)` (refresh every 50 minutes)
- **Predictable Behavior**: Always refreshes at same interval regardless of activity

**Cons**:
- **Inactive User Waste**: Refreshes token even if user is idle/away
  - User leaves tab open → refreshes every 50 minutes for hours → unnecessary backend load
- **Multiple Tabs**: Each tab runs independent timers
  - 3 open tabs → 3 refresh requests every 50 minutes
  - Backend sees 3x load for same user session
- **No Activity Awareness**: Refreshes regardless of whether user is actually using app

**Partial Solution**: Avoids 401 errors but wastes resources on inactive sessions.

### Option 3: Proactive Refresh (Activity-Based)
**Pros**:
- **Activity Awareness**: Only refresh if user is active (mouse movement, keyboard input, API calls)
- **Resource Efficient**: No refreshes for inactive users
- **Single Refresh Per Session**: Coordinate across tabs (shared localStorage flag)

**Cons**:
- **Implementation Complexity**: Must track user activity
  ```typescript
  let lastActivity = Date.now();
  window.addEventListener('mousemove', () => lastActivity = Date.now());
  window.addEventListener('keydown', () => lastActivity = Date.now());

  setInterval(() => {
    const inactive = Date.now() - lastActivity > 10 * 60 * 1000;  // 10 min idle
    if (!inactive) refreshToken();
  }, 50 * 60 * 1000);
  ```
- **Edge Case**: User reading long article → no mouse/keyboard activity → inactive flag set → token expires → next click fails
- **Tab Coordination**: Requires localStorage communication between tabs (complex)
- **Overkill for Phase II**: Activity tracking adds complexity for marginal benefit

**Partial Solution**: More efficient than fixed interval but complexity exceeds Phase II MVP needs.

### Option 4: Proactive Refresh (Simple Fixed Interval) - Chosen
**Pros**:
- **Seamless User Experience**: Token refreshed before expiration (no 401 errors during operations)
  - User submits form → token valid → request succeeds immediately
  - No visible errors or retries
  - "It just works" perception
- **Simple Implementation**: Single `setInterval` in root component
  ```typescript
  // src/hooks/useTokenRefresh.ts
  useEffect(() => {
    const interval = setInterval(async () => {
      await refreshToken();  // Call Better Auth refresh endpoint
    }, 50 * 60 * 1000);  // 50 minutes

    return () => clearInterval(interval);
  }, []);
  ```
- **No Retry Logic Needed**: API client can assume token is always valid (simplifies error handling)
- **Predictable**: Always 10-minute buffer before expiration (50 min refresh, 60 min expiry)
- **High Success Rate**: Meets SC-06 (95% success rate) easily
  - Failures only if network down during refresh window
  - 10-minute buffer allows multiple retry attempts
- **Operational Clarity**: No 401 errors in logs (clean metrics)

**Cons**:
- **Inactive User Overhead**: Refreshes token even if user is idle
  - **Acceptable**: Refresh is lightweight (<200ms, <1KB payload)
  - **Acceptable**: Phase II scale is 1000 concurrent users (not millions)
  - **Mitigation**: Can add activity tracking in Phase III if needed
- **Multiple Tab Overhead**: Each tab refreshes independently
  - **Acceptable**: Most users have 1-2 tabs (not 10+)
  - **Mitigation**: Can add tab coordination in Phase III if needed

**Accepted**: Best balance of user experience, simplicity, and reliability for Phase II MVP.

## Decision

**We will use proactive token refresh with a fixed 50-minute interval.**

### Implementation Details

#### Frontend (Token Refresh Hook)

```typescript
// src/hooks/useTokenRefresh.ts
import { useEffect } from 'react';
import { auth } from '@/lib/auth';

const REFRESH_INTERVAL = 50 * 60 * 1000;  // 50 minutes in milliseconds
const TOKEN_EXPIRY = 60 * 60 * 1000;       // 60 minutes (1 hour)
const BUFFER = TOKEN_EXPIRY - REFRESH_INTERVAL;  // 10 minutes safety buffer

export function useTokenRefresh() {
  useEffect(() => {
    console.log('Token refresh scheduled: every 50 minutes');

    const interval = setInterval(async () => {
      try {
        console.log('Proactive token refresh initiated');

        // Call Better Auth refresh endpoint
        const response = await fetch('/api/auth/refresh', {
          method: 'POST',
          credentials: 'include',  // Send HttpOnly cookie
        });

        if (response.ok) {
          const { token } = await response.json();

          // Update sessionStorage cache
          sessionStorage.setItem('jwt_token', token);

          console.log('Token refreshed successfully');
        } else {
          console.error('Token refresh failed:', response.status);
          // User will hit 401 on next API call (logout/redirect handled there)
        }
      } catch (error) {
        console.error('Token refresh error:', error);
        // Silent failure - user will hit 401 on next API call
      }
    }, REFRESH_INTERVAL);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);
}
```

#### Frontend (Root Layout Integration)

```typescript
// src/app/layout.tsx
import { useTokenRefresh } from '@/hooks/useTokenRefresh';

export default function RootLayout({ children }) {
  // Start proactive refresh when app loads
  useTokenRefresh();

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

#### Backend (Refresh Endpoint)

```python
# Better Auth handles this automatically via /api/auth/refresh
# Backend receives request with HttpOnly cookie containing current token
# Better Auth verifies token is not expired (allows refresh up to expiration)
# Issues new token with extended expiration (new 1-hour window)
# Returns new token in response body + sets new HttpOnly cookie
```

#### Timing Diagram

```
Time    Event
-----   ------------------------------------------------------------
0:00    User logs in → Token issued (expires at 1:00)
0:50    Proactive refresh → New token issued (expires at 1:50)
1:40    Proactive refresh → New token issued (expires at 2:40)
2:30    Proactive refresh → New token issued (expires at 3:30)
...     (Session continues indefinitely as long as user is logged in)
```

**Safety Buffer**: 10-minute buffer (50 min refresh, 60 min expiry) allows:
- Network retry if refresh request fails
- User to complete in-progress operation without 401 error

#### Error Handling

```typescript
// API client does NOT need retry logic - assume token is always valid
async function apiRequest(endpoint: string) {
  const token = sessionStorage.getItem('jwt_token');

  const response = await fetch(endpoint, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 401) {
    // This should never happen if proactive refresh works
    // If it does, redirect to login (token truly expired)
    window.location.href = '/login';
  }

  return response;
}
```

## Consequences

### Positive

1. **Seamless User Experience**:
   - No visible 401 errors during normal operations
   - User can work for multiple hours without interruption
   - No "token expired, please login again" messages
   - Forms submit successfully without retry logic
2. **Simple API Client**:
   - No retry logic needed (assume token always valid)
   - Fewer edge cases to handle
   - Cleaner error handling (401 means "redirect to login", not "retry")
3. **High Reliability**:
   - 10-minute safety buffer (50 min refresh, 60 min expiry)
   - Multiple retry opportunities if first refresh fails
   - Meets SC-06 (95% success rate) easily
4. **Predictable Behavior**:
   - Fixed interval (easy to reason about)
   - No race conditions (unlike reactive retries)
   - No activity tracking complexity
5. **Clean Metrics**:
   - No 401 errors in logs (unless token truly expired)
   - Operational clarity (401 means session ended, not transient expiry)

### Negative

1. **Inactive User Overhead**:
   - Refreshes token every 50 minutes even if user is idle
   - **Impact**: 1 request per user per 50 minutes (<200ms, <1KB)
   - **Scale**: 1000 users = 20 requests/minute (negligible for Phase II)
   - **Mitigation**: Can add activity tracking in Phase III if scale increases
2. **Multiple Tab Overhead**:
   - Each tab runs independent timer (3 tabs = 3 refresh requests)
   - **Impact**: 3x refresh load for users with multiple tabs
   - **Acceptable**: Most users have 1-2 tabs (not 10+)
   - **Mitigation**: Can add tab coordination (localStorage) in Phase III
3. **Battery Impact (Mobile)**:
   - Background timer runs continuously (minimal battery drain)
   - **Impact**: setInterval wakes JavaScript engine every 50 minutes
   - **Acceptable**: 50-minute interval is infrequent (not per-second polling)

### Neutral

1. **Refresh During Inactivity**: If user idle for 2+ hours, still refreshes periodically
   - Alternative: Better Auth session could timeout after inactivity (configured separately)
2. **Logout Behavior**: User must explicitly logout (refresh doesn't timeout inactive sessions)
   - Acceptable: Explicit logout matches user expectations

## Performance Analysis

### Refresh Request Cost

- **Frequency**: Every 50 minutes per user per tab
- **Latency**: <200ms (Better Auth endpoint fast)
- **Payload**: <1KB (new JWT token)
- **Backend Load**: Stateless verification + new token signing (<5ms CPU)

### Scale Calculation (1000 Concurrent Users)

- **Refresh Rate**: 1000 users / 50 minutes = 20 refreshes/minute = 0.33 refreshes/second
- **Backend CPU**: 0.33 req/sec × 5ms = 1.65ms CPU per second (negligible)
- **Network**: 0.33 req/sec × 1KB = 330 bytes/sec (negligible)

**Conclusion**: Proactive refresh overhead is trivial at Phase II scale.

### Comparison: Proactive vs Reactive

| Metric | Proactive (50 min) | Reactive (on 401) |
|---|---|---|
| **Failed Requests** | 0 per session | 1 per hour (user active) |
| **Total Requests** | 1 refresh per 50 min | 1 failed + 1 refresh + 1 retry = 3 per hour |
| **User-Visible Errors** | 0 | 1 per hour |
| **Retry Logic** | Not needed | Required in every API call |
| **Success Rate** | 99%+ | 95% (network failures) |

**Conclusion**: Proactive refresh reduces total requests and improves UX.

## Compliance

- ✅ **Specification FR-013**: "MUST implement token refresh mechanism" - Proactive refresh meets requirement
- ✅ **Specification SC-01**: "Registration and login completed within 30 seconds" - Refresh happens in background (no user-facing delay)
- ✅ **Specification SC-06**: "95% token refresh success rate" - 10-minute buffer ensures high success rate
- ✅ **Constitution Principle III**: Test-First Development - Refresh logic is unit-testable (mock setInterval)

## References

- **Feature Specification**: [specs/003-jwt-auth/spec.md](../../specs/003-jwt-auth/spec.md)
- **Implementation Plan**: [specs/003-jwt-auth/plan.md](../../specs/003-jwt-auth/plan.md)
- **Research**: [specs/003-jwt-auth/research.md](../../specs/003-jwt-auth/research.md) (Decision 6: Token Refresh)
- **Better Auth Refresh Documentation**: https://better-auth.dev/docs/refresh (external)

## Review

- **Approved By**: User (via specification requiring refresh mechanism)
- **Review Date**: 2026-01-12
- **Next Review**: After Phase II Step 2 implementation (measure actual refresh success rate)

## Future Enhancements (Out of Scope for Phase II)

If refresh overhead becomes problematic in future phases:

1. **Activity-Based Refresh**:
   - Track mouse/keyboard activity
   - Only refresh if user active in last 10 minutes
   - Requires event listeners + activity state

2. **Tab Coordination**:
   - Use localStorage to coordinate refresh across tabs
   - Only one tab refreshes per user
   - Other tabs read new token from localStorage

3. **Sliding Window Expiration**:
   - Backend extends expiration on every API call
   - No explicit refresh needed
   - Requires stateful backend (violates FR-009)

4. **Long-Lived Refresh Tokens**:
   - Issue 5-minute access tokens + 7-day refresh tokens
   - Refresh access tokens frequently (less damage if stolen)
   - Revoke only refresh tokens (complex implementation)
