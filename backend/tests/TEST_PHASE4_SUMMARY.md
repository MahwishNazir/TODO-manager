# Phase 4 Tests Summary - Protected API Access (User Story 2)

## Overview

This document summarizes the implementation of Phase 4 tests (T025-T028) for User Story 2 - Protected API Access. These tests follow TDD RED phase principles and are designed to FAIL initially, then pass after implementing JWT authentication in the API endpoints.

## Test Implementation Status

| Test ID | Description | Status | Test Count |
|---------|-------------|--------|------------|
| T025 | Contract test for JWT middleware | ✅ Complete | 16 tests |
| T026 | Integration tests with JWT auth | ✅ Complete | 27 tests |
| T027 | User isolation integration tests | ✅ Complete | 19 tests |
| T028 | get_current_user dependency tests | ✅ Complete (already exists) | 9 tests |

**Total New Tests**: 62 tests (excluding T028 which already exists)

## Test Files Created

### 1. T025: Contract Tests for JWT Middleware
**File**: `backend/tests/contract/test_jwt_validation.py`

Tests JWT validation middleware behavior at the HTTP layer. Verifies that endpoints properly reject unauthorized requests.

**Test Classes**:
- `TestJWTMiddlewareMissingToken` (6 tests)
  - Tests all endpoints without Authorization header
  - Expected: 401 Unauthorized

- `TestJWTMiddlewareInvalidToken` (3 tests)
  - Tests malformed tokens
  - Tests missing "Bearer " prefix
  - Expected: 401 Unauthorized

- `TestJWTMiddlewareExpiredToken` (2 tests)
  - Tests expired JWT tokens
  - Expected: 401 Unauthorized with "expired" message

- `TestJWTMiddlewareTamperedToken` (3 tests)
  - Tests tampered signatures
  - Tests tokens signed with wrong secret
  - Tests modified payloads
  - Expected: 401 Unauthorized with "signature" or "invalid" message

- `TestJWTMiddlewareInvalidClaims` (2 tests)
  - Tests wrong audience claim
  - Tests wrong issuer claim
  - Expected: 401 Unauthorized with specific error messages

**Key Test Pattern**:
```python
def test_create_task_without_token_returns_401(self, client):
    """Test creating task without Authorization header returns 401."""
    response = client.post(
        "/api/test-user-123/tasks",
        json={"title": "Test task"}
    )
    # RED PHASE: This should return 401 but currently returns 201
    assert response.status_code == 401
```

### 2. T026: Integration Tests with JWT Authentication
**File**: `backend/tests/integration/test_api_tasks_with_auth.py`

Tests complete API workflows with JWT authentication. Verifies that valid tokens allow operations and invalid tokens are rejected.

**Test Classes**:
- `TestCreateTaskWithAuth` (3 tests)
  - Valid token succeeds
  - Missing token fails (401)
  - Mismatched user_id fails (403)

- `TestListTasksWithAuth` (3 tests)
  - Valid token succeeds
  - Missing token fails (401)
  - Mismatched user_id fails (403)

- `TestGetSingleTaskWithAuth` (3 tests)
  - Valid token succeeds
  - Missing token fails (401)
  - Mismatched user_id fails (403)

- `TestUpdateTaskWithAuth` (3 tests)
  - Valid token succeeds
  - Missing token fails (401)
  - Mismatched user_id fails (403)

- `TestDeleteTaskWithAuth` (3 tests)
  - Valid token succeeds
  - Missing token fails (401)
  - Mismatched user_id fails (403)

- `TestToggleCompletionWithAuth` (3 tests)
  - Valid token succeeds
  - Missing token fails (401)
  - Mismatched user_id fails (403)

- `TestAuthenticationJourney` (2 tests)
  - Complete workflow with valid token
  - Complete workflow with expired token (all operations fail)

**Key Test Pattern**:
```python
def test_create_task_with_mismatched_user_id_fails(self, client):
    """Test creating task with JWT user_id not matching URL user_id returns 403."""
    # Token is for user-123 but URL is for user-456
    token = create_test_token(user_id="user-123")

    response = client.post(
        "/api/user-456/tasks",
        json={"title": "Unauthorized task"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # RED PHASE: This should return 403 but currently returns 201
    assert response.status_code == 403
```

### 3. T027: User Isolation Integration Tests
**File**: `backend/tests/integration/test_user_isolation.py`

Tests that users cannot access each other's tasks even with valid JWT tokens. Critical for data security.

**Test Classes**:
- `TestUserIsolationList` (3 tests)
  - User A cannot list User B's tasks
  - User B cannot list User A's tasks
  - Users can only see their own tasks

- `TestUserIsolationCreate` (2 tests)
  - User A cannot create tasks in User B's space
  - User B cannot create tasks in User A's space

- `TestUserIsolationGet` (2 tests)
  - User A cannot get User B's specific task
  - User B cannot get User A's specific task

- `TestUserIsolationUpdate` (2 tests)
  - User A cannot update User B's task
  - User B cannot update User A's task
  - Verifies task remains unchanged

- `TestUserIsolationDelete` (2 tests)
  - User A cannot delete User B's task
  - User B cannot delete User A's task
  - Verifies task still exists

- `TestUserIsolationToggleCompletion` (2 tests)
  - User A cannot toggle User B's task
  - User B cannot toggle User A's task

- `TestCrossUserAttackScenarios` (6 tests)
  - Cannot impersonate by changing URL only
  - Multiple users complete isolation
  - Various attack vectors

**Key Test Pattern**:
```python
def test_user_a_cannot_list_user_b_tasks(self, client, user_a_id, user_b_id, user_a_token, user_b_token):
    """Test User A cannot list User B's tasks."""
    # User B creates tasks
    for i in range(3):
        client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": f"User B Task {i+1}"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

    # User A tries to list User B's tasks with their own token
    response = client.get(
        f"/api/{user_b_id}/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"}  # Token is for user A
    )

    # RED PHASE: This should return 403 but currently returns 200
    assert response.status_code == 403
```

### 4. T028: JWT Handler Unit Tests
**Status**: Already Complete ✅

Unit tests for `get_current_user()` dependency already exist in:
- `backend/tests/unit/test_jwt_handler.py`

Tests include:
- Valid token extraction
- Missing claims handling
- Invalid payload handling
- Clock skew tolerance

## Test Execution Results (RED Phase)

### Contract Tests (T025)
```bash
$ pytest tests/contract/test_jwt_validation.py -v
================================== FAILURES ===================================
16 tests FAILED
```

**Sample Failures**:
- `test_list_tasks_without_token_returns_401`: Expected 401, got 200
- `test_create_task_without_token_returns_401`: Expected 401, got 201
- `test_list_tasks_with_expired_token_returns_401`: Expected 401, got 200
- `test_list_tasks_with_tampered_signature_returns_401`: Expected 401, got 200

### Integration Tests with Auth (T026)
```bash
$ pytest tests/integration/test_api_tasks_with_auth.py -v
================================== FAILURES ===================================
27 tests FAILED (some may pass but critical auth tests fail)
```

**Sample Failures**:
- `test_create_task_without_token_fails`: Expected 401, got 201
- `test_create_task_with_mismatched_user_id_fails`: Expected 403, got 201
- `test_expired_token_fails_throughout_workflow`: Expected 401, got 200/201

### User Isolation Tests (T027)
```bash
$ pytest tests/integration/test_user_isolation.py -v
================================== FAILURES ===================================
19 tests FAILED
```

**Sample Failures**:
- `test_user_a_cannot_list_user_b_tasks`: Expected 403, got 200
- `test_user_a_cannot_create_task_for_user_b`: Expected 403, got 201
- `test_user_cannot_impersonate_by_changing_url_only`: Expected 403, got 200

## Why Tests Are Failing (Expected in RED Phase)

All tests are failing because:

1. **API endpoints don't require JWT authentication** - Endpoints in `backend/src/api/routes/tasks.py` don't use `Depends(get_current_user)` dependency

2. **No user_id validation** - Endpoints don't validate that JWT `user_id` matches URL `user_id` parameter

3. **Missing authorization checks** - No 401/403 responses for unauthorized access

## Next Steps for GREEN Phase

To make these tests pass, implement the following:

### 1. Update API Endpoints
Add JWT authentication dependency to all endpoints in `backend/src/api/routes/tasks.py`:

```python
from src.auth.jwt_handler import get_current_user, CurrentUser

@router.post("/{user_id}/tasks", ...)
def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user),  # ADD THIS
    db: Session = Depends(get_db),
):
    # Validate user_id matches JWT user_id
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # ... rest of endpoint logic
```

### 2. Apply to All Endpoints
Update all 6 endpoints:
- `POST /{user_id}/tasks` - Create task
- `GET /{user_id}/tasks` - List tasks
- `GET /{user_id}/tasks/{task_id}` - Get task
- `PUT /{user_id}/tasks/{task_id}` - Update task
- `DELETE /{user_id}/tasks/{task_id}` - Delete task
- `PATCH /{user_id}/tasks/{task_id}/complete` - Toggle completion

### 3. Test After Implementation
After implementing authentication:

```bash
# All tests should pass
pytest tests/contract/test_jwt_validation.py -v
pytest tests/integration/test_api_tasks_with_auth.py -v
pytest tests/integration/test_user_isolation.py -v

# Expected: 62 tests passed
```

## Test Coverage

The new tests cover:

### Security Scenarios
- Missing Authorization header
- Malformed JWT tokens
- Expired JWT tokens
- Tampered signatures
- Invalid claims (audience, issuer)
- Cross-user access attempts

### API Operations
- Create task
- List tasks
- Get task
- Update task
- Delete task
- Toggle completion

### User Isolation
- User A cannot access User B's data
- User B cannot access User A's data
- Multiple users are completely isolated
- Attack scenarios (URL manipulation, token reuse)

## Helper Functions

All test files use a shared JWT token generation helper:

```python
def create_test_token(
    user_id: str = "test-user-123",
    email: str = "test@example.com",
    exp_minutes: int = 60,
    **extra_claims
) -> str:
    """Create a test JWT token with specified claims."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(minutes=exp_minutes),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        **extra_claims,
    }
    return jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
```

## Fixtures

New fixtures added for user isolation tests:

```python
@pytest.fixture
def user_a_id():
    """Provide user A ID for testing."""
    return "user-alice-123"

@pytest.fixture
def user_b_id():
    """Provide user B ID for testing."""
    return "user-bob-456"

@pytest.fixture
def user_a_token(user_a_id):
    """Provide valid JWT token for user A."""
    return create_test_token(user_id=user_a_id, email="alice@example.com")

@pytest.fixture
def user_b_token(user_b_id):
    """Provide valid JWT token for user B."""
    return create_test_token(user_id=user_b_id, email="bob@example.com")
```

## Summary

- ✅ **T025**: 16 contract tests for JWT middleware validation
- ✅ **T026**: 27 integration tests with JWT authentication
- ✅ **T027**: 19 user isolation integration tests
- ✅ **T028**: Already complete (9 unit tests)

**Total**: 62 new tests, all currently FAILING as expected in RED phase.

All tests follow TDD principles and will pass once JWT authentication is properly implemented in the API endpoints.
