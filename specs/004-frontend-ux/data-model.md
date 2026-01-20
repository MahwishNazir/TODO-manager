# Data Model: Frontend Application & UX

**Feature**: 004-frontend-ux
**Date**: 2026-01-14
**Status**: Complete

## Overview

This document defines the data models used in the frontend application, including TypeScript interfaces that mirror backend schemas and client-side state management types.

---

## 1. User Session Model

### UserSession

Represents the authenticated user's session state stored in the frontend.

```typescript
// types/user.ts

/**
 * User session data from Better Auth
 * Stored in HttpOnly cookie, accessed via session API
 */
export interface UserSession {
  /** Unique user identifier (UUID) */
  id: string;

  /** User's email address */
  email: string;

  /** User's display name (optional) */
  name?: string;

  /** Session creation timestamp (ISO 8601) */
  createdAt: string;

  /** Session expiration timestamp (ISO 8601) */
  expiresAt: string;
}

/**
 * Authentication state for the frontend
 */
export interface AuthState {
  /** Current user session (null if not authenticated) */
  user: UserSession | null;

  /** Whether authentication state is being loaded */
  isLoading: boolean;

  /** Whether user is authenticated */
  isAuthenticated: boolean;
}

/**
 * JWT token payload structure (for reference - not directly accessed in frontend)
 * Backend validates this structure
 */
export interface JWTPayload {
  /** Subject - User ID */
  sub: string;

  /** User email */
  email: string;

  /** Issued at timestamp (Unix) */
  iat: number;

  /** Expiration timestamp (Unix) */
  exp: number;

  /** Issuer */
  iss: string;

  /** Audience */
  aud: string;
}
```

### Validation Rules

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| id | string | Yes | UUID format |
| email | string | Yes | Valid email format |
| name | string | No | Max 100 characters |
| createdAt | string | Yes | ISO 8601 timestamp |
| expiresAt | string | Yes | ISO 8601 timestamp, > createdAt |

---

## 2. Task UI Model

### TaskResponse

Frontend representation of a task, matching the backend `TaskResponse` schema exactly.

```typescript
// types/task.ts

/**
 * Task response from backend API
 * Matches backend TaskResponse schema exactly
 */
export interface TaskResponse {
  /** Unique task identifier (UUID) */
  id: string;

  /** Owner user ID (UUID) */
  user_id: string;

  /** Task title (1-500 characters) */
  title: string;

  /** Whether task is completed */
  is_completed: boolean;

  /** Task creation timestamp (ISO 8601) */
  created_at: string;

  /** Last update timestamp (ISO 8601) */
  updated_at: string;
}

/**
 * Task list response (array of tasks)
 */
export type TaskListResponse = TaskResponse[];

/**
 * Task with UI-specific state (extends API response)
 */
export interface TaskWithUIState extends TaskResponse {
  /** Whether task is currently being edited */
  isEditing?: boolean;

  /** Whether task operation is in progress */
  isLoading?: boolean;

  /** Optimistic update pending (if enabled) */
  isPending?: boolean;
}
```

### Backend Schema Reference

The frontend `TaskResponse` matches this backend SQLModel:

```python
# backend/src/models/task.py (reference)
class Task(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(min_length=1, max_length=500)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 3. Form State Models

### TaskCreate

Request body for creating a new task.

```typescript
// types/task.ts (continued)

/**
 * Request body for POST /api/{user_id}/tasks
 */
export interface TaskCreate {
  /** Task title (1-500 characters, trimmed) */
  title: string;
}

/**
 * Request body for PUT /api/{user_id}/tasks/{task_id}
 */
export interface TaskUpdate {
  /** Updated task title (1-500 characters, trimmed) */
  title: string;
}
```

### Form State Types

```typescript
// types/form.ts

/**
 * Task creation form state
 */
export interface CreateTaskFormState {
  /** Form field values */
  values: {
    title: string;
  };

  /** Field-level errors */
  errors: {
    title?: string;
  };

  /** Whether form is being submitted */
  isSubmitting: boolean;

  /** Whether form has been submitted successfully */
  isSubmitted: boolean;

  /** Whether form values have been modified */
  isDirty: boolean;
}

/**
 * Task edit form state
 */
export interface EditTaskFormState {
  /** Original task ID being edited */
  taskId: string;

  /** Form field values */
  values: {
    title: string;
  };

  /** Field-level errors */
  errors: {
    title?: string;
  };

  /** Whether form is being submitted */
  isSubmitting: boolean;

  /** Original title for cancel/revert */
  originalTitle: string;
}

/**
 * Authentication form state (signup/signin)
 */
export interface AuthFormState {
  /** Form field values */
  values: {
    email: string;
    password: string;
    name?: string;
  };

  /** Field-level errors */
  errors: {
    email?: string;
    password?: string;
    name?: string;
    form?: string; // General form error
  };

  /** Whether form is being submitted */
  isSubmitting: boolean;
}
```

### Validation Schemas (Zod)

```typescript
// lib/validations.ts

import { z } from "zod";

/**
 * Task title validation schema
 */
export const taskTitleSchema = z
  .string()
  .min(1, "Task title is required")
  .max(500, "Title must be 500 characters or less")
  .transform((val) => val.trim());

/**
 * Task creation form schema
 */
export const createTaskSchema = z.object({
  title: taskTitleSchema,
});

/**
 * Task update form schema
 */
export const updateTaskSchema = z.object({
  title: taskTitleSchema,
});

/**
 * Signup form schema
 */
export const signupSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  name: z.string().optional(),
});

/**
 * Signin form schema
 */
export const signinSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

// Type exports from schemas
export type CreateTaskInput = z.infer<typeof createTaskSchema>;
export type UpdateTaskInput = z.infer<typeof updateTaskSchema>;
export type SignupInput = z.infer<typeof signupSchema>;
export type SigninInput = z.infer<typeof signinSchema>;
```

---

## 4. API Response Models

### Success Responses

```typescript
// types/api.ts

/**
 * Generic API success response wrapper (if backend uses one)
 * Currently backend returns data directly without wrapper
 */
export interface ApiResponse<T> {
  data: T;
  status: "success";
}

/**
 * Paginated response (for future use)
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
```

### Error Responses

```typescript
// types/api.ts (continued)

/**
 * API error response structure
 */
export interface ApiErrorResponse {
  /** Error detail message */
  detail: string;

  /** HTTP status code */
  status?: number;

  /** Validation errors (for 422 responses) */
  errors?: ValidationError[];
}

/**
 * Validation error detail
 */
export interface ValidationError {
  /** Field that failed validation */
  loc: (string | number)[];

  /** Error message */
  msg: string;

  /** Error type */
  type: string;
}

/**
 * Custom API error class for frontend
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public errors?: ValidationError[]
  ) {
    super(detail);
    this.name = "ApiError";
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  get isForbidden(): boolean {
    return this.status === 403;
  }

  get isNotFound(): boolean {
    return this.status === 404;
  }

  get isValidationError(): boolean {
    return this.status === 422;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }
}
```

---

## 5. Loading & UI State Models

### Loading States

```typescript
// types/ui.ts

/**
 * Async operation state
 */
export type AsyncState = "idle" | "loading" | "success" | "error";

/**
 * Task list loading state
 */
export interface TasksLoadingState {
  /** Current async operation state */
  state: AsyncState;

  /** Error message if state is "error" */
  error?: string;

  /** Tasks data if state is "success" */
  data?: TaskResponse[];
}

/**
 * Single task operation state
 */
export interface TaskOperationState {
  /** Operation type */
  operation: "create" | "update" | "delete" | "toggle";

  /** Task ID being operated on (null for create) */
  taskId?: string;

  /** Current state */
  state: AsyncState;

  /** Error message if failed */
  error?: string;
}
```

### Empty State

```typescript
// types/ui.ts (continued)

/**
 * Empty state configuration
 */
export interface EmptyStateConfig {
  /** Heading text */
  title: string;

  /** Description text */
  description: string;

  /** Call-to-action button text */
  actionText?: string;

  /** Action callback */
  onAction?: () => void;

  /** Icon name (Lucide icon) */
  icon?: string;
}

// Default empty state for tasks
export const TASKS_EMPTY_STATE: EmptyStateConfig = {
  title: "No tasks yet",
  description: "Create your first task to get started with your todo list.",
  actionText: "Add Task",
  icon: "ClipboardList",
};
```

---

## 6. Theme State Model

### Theme Configuration

```typescript
// types/theme.ts

/**
 * Available theme options
 */
export type Theme = "light" | "dark" | "system";

/**
 * Resolved theme (after system preference applied)
 */
export type ResolvedTheme = "light" | "dark";

/**
 * Theme state
 */
export interface ThemeState {
  /** User's theme preference */
  theme: Theme;

  /** Resolved theme after system preference */
  resolvedTheme: ResolvedTheme;

  /** Whether theme is being loaded from storage */
  isLoading: boolean;
}

/**
 * Theme context value
 */
export interface ThemeContextValue extends ThemeState {
  /** Set theme preference */
  setTheme: (theme: Theme) => void;

  /** Toggle between light and dark */
  toggleTheme: () => void;
}
```

---

## 7. Navigation State Model

### Route Configuration

```typescript
// types/navigation.ts

/**
 * Application routes
 */
export const ROUTES = {
  HOME: "/",
  SIGNIN: "/signin",
  SIGNUP: "/signup",
  TASKS: "/tasks",
  TASK_DETAIL: (id: string) => `/tasks/${id}`,
} as const;

/**
 * Protected routes that require authentication
 */
export const PROTECTED_ROUTES = ["/tasks", "/tasks/[id]"] as const;

/**
 * Auth routes (redirect to /tasks if already authenticated)
 */
export const AUTH_ROUTES = ["/signin", "/signup"] as const;

/**
 * Navigation item configuration
 */
export interface NavItem {
  /** Display label */
  label: string;

  /** Route path */
  href: string;

  /** Lucide icon name */
  icon?: string;

  /** Whether item is active */
  isActive?: boolean;
}
```

---

## 8. Constants

### API Configuration

```typescript
// lib/constants.ts

/**
 * API base URL
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Task title constraints
 */
export const TASK_TITLE = {
  MIN_LENGTH: 1,
  MAX_LENGTH: 500,
} as const;

/**
 * Password constraints
 */
export const PASSWORD = {
  MIN_LENGTH: 8,
} as const;

/**
 * Toast duration (ms)
 */
export const TOAST_DURATION = {
  SUCCESS: 3000,
  ERROR: 5000,
  INFO: 4000,
} as const;

/**
 * Debounce delays (ms)
 */
export const DEBOUNCE = {
  SEARCH: 300,
  SAVE: 500,
} as const;

/**
 * Animation durations (ms)
 */
export const ANIMATION = {
  FADE_OUT: 300,
  SLIDE_IN: 200,
} as const;
```

---

## Entity Relationship Diagram

```
┌──────────────────┐
│   UserSession    │
├──────────────────┤
│ id: string (PK)  │
│ email: string    │
│ name?: string    │
│ createdAt: string│
│ expiresAt: string│
└────────┬─────────┘
         │
         │ 1:N (one user has many tasks)
         │
         ▼
┌──────────────────┐
│   TaskResponse   │
├──────────────────┤
│ id: string (PK)  │
│ user_id: string  │◄─── References UserSession.id
│ title: string    │
│ is_completed:bool│
│ created_at:string│
│ updated_at:string│
└──────────────────┘
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Form State  │───►│  API Client  │───►│  UI State    │      │
│  │ (React Hook  │    │ (fetch +     │    │ (useState)   │      │
│  │   Form)      │    │  JWT)        │    │              │      │
│  └──────────────┘    └──────┬───────┘    └──────────────┘      │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐        │
│  │  TaskCreate│      │TaskResponse│      │  ApiError  │        │
│  │  TaskUpdate│      │   (list)   │      │            │        │
│  └────────────┘      └────────────┘      └────────────┘        │
│         │                   │                   │               │
└─────────┼───────────────────┼───────────────────┼───────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│  POST /api/{user_id}/tasks     → TaskResponse                    │
│  GET  /api/{user_id}/tasks     → TaskResponse[]                  │
│  GET  /api/{user_id}/tasks/{id}→ TaskResponse                    │
│  PUT  /api/{user_id}/tasks/{id}→ TaskResponse                    │
│  PATCH/api/{user_id}/tasks/{id}/complete → TaskResponse          │
│  DELETE /api/{user_id}/tasks/{id} → 204 No Content               │
└─────────────────────────────────────────────────────────────────┘
```

---

**Data Model Status**: ✅ Complete
**Next Step**: Create contracts/ directory with TypeScript interfaces
