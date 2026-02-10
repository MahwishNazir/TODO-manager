# AI Agent API

OpenAI Agents SDK-based todo chatbot with MCP tool integration.

## API Endpoints

Base URL: `http://localhost:8002/api/agent`

### Sessions

#### Create Session
```http
POST /sessions
Authorization: Bearer <jwt_token>
```

Response:
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-02-03T12:00:00Z",
    "expires_at": "2026-02-03T12:30:00Z"
  }
}
```

#### Get Session
```http
GET /sessions/{session_id}
Authorization: Bearer <jwt_token>
```

#### Delete Session
```http
DELETE /sessions/{session_id}
Authorization: Bearer <jwt_token>
```

### Messages

#### Send Message
```http
POST /sessions/{session_id}/messages
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "content": "Add a task to buy groceries tomorrow"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "message_id": "...",
    "content": "I've added 'buy groceries' due tomorrow to your todo list.",
    "tool_calls": [
      {
        "tool_name": "add_task",
        "status": "SUCCESS",
        "duration_ms": 150
      }
    ],
    "confirmation_required": false
  }
}
```

#### Stream Message (SSE)
```http
POST /sessions/{session_id}/messages/stream
Authorization: Bearer <jwt_token>
Accept: text/event-stream
Content-Type: application/json

{
  "content": "List my tasks"
}
```

SSE Events:
```
event: message
data: {"type": "thinking", "content": "Looking up your tasks..."}

event: message
data: {"type": "tool_call", "tool": "list_tasks", "status": "started"}

event: message
data: {"type": "tool_call", "tool": "list_tasks", "status": "completed"}

event: message
data: {"type": "response", "content": "You have 3 tasks..."}

event: done
data: {"message_id": "..."}
```

### Confirmation

#### Process Confirmation
```http
POST /sessions/{session_id}/confirm
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "response": "yes"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "confirmed": true,
    "action": "DELETE_TASK",
    "affected_ids": ["task-123"],
    "message": "Task deleted successfully."
  }
}
```

#### Get Confirmation Status
```http
GET /sessions/{session_id}/confirm/status
Authorization: Bearer <jwt_token>
```

### Execution Plans

#### Get Current Plan
```http
GET /sessions/{session_id}/plan
Authorization: Bearer <jwt_token>
```

#### Approve Plan
```http
POST /sessions/{session_id}/plan/approve
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "approve": true
}
```

#### Cancel Plan
```http
DELETE /sessions/{session_id}/plan
Authorization: Bearer <jwt_token>
```

### Audit

#### List Invocations
```http
GET /audit/invocations?session_id={uuid}&tool_name={name}&limit={n}
Authorization: Bearer <jwt_token>
```

#### Get Invocation Details
```http
GET /audit/invocations/{invocation_id}
Authorization: Bearer <jwt_token>
```

#### Get Statistics
```http
GET /audit/stats?session_id={uuid}
Authorization: Bearer <jwt_token>
```

## Example Flows

### Create Task
```bash
# 1. Create session
SESSION=$(curl -s -X POST http://localhost:8002/api/agent/sessions \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data.session_id')

# 2. Send message
curl -X POST "http://localhost:8002/api/agent/sessions/$SESSION/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Add a task to finish the report by Friday"}'
```

### Delete with Confirmation
```bash
# 1. Request delete (triggers confirmation)
curl -X POST ".../messages" \
  -d '{"content": "Delete the report task"}'
# Response: confirmation_required: true

# 2. Confirm
curl -X POST ".../confirm" \
  -d '{"response": "yes"}'
# Response: confirmed: true, task deleted
```

### Multi-Step Request
```bash
# Request multiple operations at once
curl -X POST ".../messages" \
  -d '{"content": "Create a task for groceries and mark the dishes task as done"}'
# Agent builds and executes plan automatically
```

## Error Responses

All errors follow this format:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "category": "USER_CORRECTABLE|SYSTEM_TEMPORARY|SYSTEM_PERMANENT"
  }
}
```

Error Codes:
| Code | Category | Description |
|------|----------|-------------|
| `VALIDATION_ERROR` | USER_CORRECTABLE | Invalid request format |
| `TASK_NOT_FOUND` | USER_CORRECTABLE | Referenced task doesn't exist |
| `AMBIGUOUS_REFERENCE` | USER_CORRECTABLE | Multiple tasks match reference |
| `SESSION_EXPIRED` | SYSTEM_TEMPORARY | Session timed out (30min) |
| `MCP_TIMEOUT` | SYSTEM_TEMPORARY | Tool invocation timed out |
| `INTERNAL_ERROR` | SYSTEM_PERMANENT | Unexpected error |

## Authentication

All endpoints require JWT authentication with the `Authorization: Bearer <token>` header.

The JWT must be signed with the same `BETTER_AUTH_SECRET` configured in the backend.

Expected claims:
- `sub`: User ID
- `iss`: "todo-app"
- `aud`: "todo-api"

## Configuration

Environment variables:
```env
OPENAI_API_KEY=sk-...          # Required: OpenAI API key
MCP_SERVER_URL=http://localhost:8001  # MCP server URL
BETTER_AUTH_SECRET=...         # JWT shared secret
DATABASE_URL=postgresql://...  # Optional: audit storage
```

## Running

```bash
# Development
uvicorn chatbot.api.main:app --reload --port 8002

# Production
uvicorn chatbot.api.main:app --host 0.0.0.0 --port 8002 --workers 4
```

## Testing

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v --no-cov

# Contract tests
pytest tests/contract/ -v
```
