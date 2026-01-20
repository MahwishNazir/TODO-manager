/**
 * Task API Contracts
 * Feature: 004-frontend-ux
 * Date: 2026-01-14
 *
 * Defines TypeScript interfaces for Task CRUD API endpoints.
 * All endpoints require JWT authentication via Authorization header or cookie.
 */

// ============================================================================
// Task Response Types
// ============================================================================

/**
 * Task entity as returned by the API
 * Matches backend TaskResponse schema exactly
 */
export interface TaskResponse {
  /** Unique task identifier (UUID) */
  id: string;

  /** Owner user ID (UUID) - must match authenticated user */
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
 * List of tasks response type
 */
export type TaskListResponse = TaskResponse[];

// ============================================================================
// Create Task
// ============================================================================

/**
 * POST /api/{user_id}/tasks
 *
 * Create a new task for the authenticated user.
 *
 * Authentication: Required (JWT Bearer token or session cookie)
 * Authorization: user_id in path must match authenticated user's ID
 *
 * @example
 * POST /api/123e4567-e89b-12d3-a456-426614174000/tasks
 * Content-Type: application/json
 * Authorization: Bearer <jwt_token>
 *
 * {
 *   "title": "Buy groceries"
 * }
 *
 * Response: 201 Created
 * {
 *   "id": "...",
 *   "user_id": "123e4567-e89b-12d3-a456-426614174000",
 *   "title": "Buy groceries",
 *   "is_completed": false,
 *   "created_at": "2026-01-14T10:30:00Z",
 *   "updated_at": "2026-01-14T10:30:00Z"
 * }
 */
export interface CreateTaskRequest {
  /** Task title (1-500 characters, trimmed) */
  title: string;
}

export interface CreateTaskResponse extends TaskResponse {}

// ============================================================================
// List Tasks
// ============================================================================

/**
 * GET /api/{user_id}/tasks
 *
 * Get all tasks for the authenticated user.
 *
 * Authentication: Required (JWT Bearer token or session cookie)
 * Authorization: user_id in path must match authenticated user's ID
 *
 * @example
 * GET /api/123e4567-e89b-12d3-a456-426614174000/tasks
 * Authorization: Bearer <jwt_token>
 *
 * Response: 200 OK
 * [
 *   {
 *     "id": "...",
 *     "user_id": "...",
 *     "title": "Buy groceries",
 *     "is_completed": false,
 *     "created_at": "2026-01-14T10:30:00Z",
 *     "updated_at": "2026-01-14T10:30:00Z"
 *   },
 *   ...
 * ]
 */
export interface ListTasksRequest {
  // No request body - user_id from path
}

export type ListTasksResponse = TaskListResponse;

// ============================================================================
// Get Single Task
// ============================================================================

/**
 * GET /api/{user_id}/tasks/{task_id}
 *
 * Get a single task by ID.
 *
 * Authentication: Required (JWT Bearer token or session cookie)
 * Authorization: user_id in path must match authenticated user's ID
 *
 * @example
 * GET /api/123e4567-e89b-12d3-a456-426614174000/tasks/abc123
 * Authorization: Bearer <jwt_token>
 *
 * Response: 200 OK
 * {
 *   "id": "abc123",
 *   "user_id": "123e4567-e89b-12d3-a456-426614174000",
 *   "title": "Buy groceries",
 *   "is_completed": false,
 *   "created_at": "2026-01-14T10:30:00Z",
 *   "updated_at": "2026-01-14T10:30:00Z"
 * }
 *
 * Error: 404 Not Found (task not found or belongs to another user)
 */
export interface GetTaskRequest {
  // No request body - task_id from path
}

export interface GetTaskResponse extends TaskResponse {}

// ============================================================================
// Update Task
// ============================================================================

/**
 * PUT /api/{user_id}/tasks/{task_id}
 *
 * Update a task's title.
 *
 * Authentication: Required (JWT Bearer token or session cookie)
 * Authorization: user_id in path must match authenticated user's ID
 *
 * @example
 * PUT /api/123e4567-e89b-12d3-a456-426614174000/tasks/abc123
 * Content-Type: application/json
 * Authorization: Bearer <jwt_token>
 *
 * {
 *   "title": "Buy groceries and vegetables"
 * }
 *
 * Response: 200 OK
 * {
 *   "id": "abc123",
 *   "user_id": "...",
 *   "title": "Buy groceries and vegetables",
 *   "is_completed": false,
 *   "created_at": "2026-01-14T10:30:00Z",
 *   "updated_at": "2026-01-14T11:00:00Z"
 * }
 */
export interface UpdateTaskRequest {
  /** Updated task title (1-500 characters, trimmed) */
  title: string;
}

export interface UpdateTaskResponse extends TaskResponse {}

// ============================================================================
// Toggle Task Completion
// ============================================================================

/**
 * PATCH /api/{user_id}/tasks/{task_id}/complete
 *
 * Toggle task completion status (complete ↔ incomplete).
 *
 * Authentication: Required (JWT Bearer token or session cookie)
 * Authorization: user_id in path must match authenticated user's ID
 *
 * @example
 * PATCH /api/123e4567-e89b-12d3-a456-426614174000/tasks/abc123/complete
 * Authorization: Bearer <jwt_token>
 *
 * Response: 200 OK
 * {
 *   "id": "abc123",
 *   "user_id": "...",
 *   "title": "Buy groceries",
 *   "is_completed": true,  // Toggled from false to true
 *   "created_at": "2026-01-14T10:30:00Z",
 *   "updated_at": "2026-01-14T11:30:00Z"
 * }
 */
export interface ToggleCompleteRequest {
  // No request body - toggles current state
}

export interface ToggleCompleteResponse extends TaskResponse {}

// ============================================================================
// Delete Task
// ============================================================================

/**
 * DELETE /api/{user_id}/tasks/{task_id}
 *
 * Delete a task permanently.
 *
 * Authentication: Required (JWT Bearer token or session cookie)
 * Authorization: user_id in path must match authenticated user's ID
 *
 * @example
 * DELETE /api/123e4567-e89b-12d3-a456-426614174000/tasks/abc123
 * Authorization: Bearer <jwt_token>
 *
 * Response: 204 No Content
 */
export interface DeleteTaskRequest {
  // No request body - task_id from path
}

// 204 No Content - no response body
export type DeleteTaskResponse = void;

// ============================================================================
// API Client Interface
// ============================================================================

/**
 * Task API client interface
 * Defines all available task operations
 */
export interface TasksApiClient {
  /**
   * Create a new task
   * @param userId - Authenticated user's ID
   * @param data - Task creation data
   */
  create(userId: string, data: CreateTaskRequest): Promise<CreateTaskResponse>;

  /**
   * List all tasks for user
   * @param userId - Authenticated user's ID
   */
  list(userId: string): Promise<ListTasksResponse>;

  /**
   * Get a single task
   * @param userId - Authenticated user's ID
   * @param taskId - Task ID to retrieve
   */
  get(userId: string, taskId: string): Promise<GetTaskResponse>;

  /**
   * Update a task's title
   * @param userId - Authenticated user's ID
   * @param taskId - Task ID to update
   * @param data - Update data
   */
  update(
    userId: string,
    taskId: string,
    data: UpdateTaskRequest
  ): Promise<UpdateTaskResponse>;

  /**
   * Toggle task completion status
   * @param userId - Authenticated user's ID
   * @param taskId - Task ID to toggle
   */
  toggleComplete(
    userId: string,
    taskId: string
  ): Promise<ToggleCompleteResponse>;

  /**
   * Delete a task
   * @param userId - Authenticated user's ID
   * @param taskId - Task ID to delete
   */
  delete(userId: string, taskId: string): Promise<DeleteTaskResponse>;
}

// ============================================================================
// Path Parameters
// ============================================================================

/**
 * Path parameters for task endpoints
 */
export interface TaskPathParams {
  /** User ID (UUID) - must match authenticated user */
  user_id: string;
}

/**
 * Path parameters for single task endpoints
 */
export interface SingleTaskPathParams extends TaskPathParams {
  /** Task ID (UUID) */
  task_id: string;
}

// ============================================================================
// Endpoint Definitions
// ============================================================================

/**
 * Task API endpoint definitions
 * Used for generating API client methods
 */
export const TASK_ENDPOINTS = {
  /** Create task: POST /api/{user_id}/tasks */
  CREATE: (userId: string) => `/api/${userId}/tasks`,

  /** List tasks: GET /api/{user_id}/tasks */
  LIST: (userId: string) => `/api/${userId}/tasks`,

  /** Get task: GET /api/{user_id}/tasks/{task_id} */
  GET: (userId: string, taskId: string) => `/api/${userId}/tasks/${taskId}`,

  /** Update task: PUT /api/{user_id}/tasks/{task_id} */
  UPDATE: (userId: string, taskId: string) => `/api/${userId}/tasks/${taskId}`,

  /** Toggle complete: PATCH /api/{user_id}/tasks/{task_id}/complete */
  TOGGLE_COMPLETE: (userId: string, taskId: string) =>
    `/api/${userId}/tasks/${taskId}/complete`,

  /** Delete task: DELETE /api/{user_id}/tasks/{task_id} */
  DELETE: (userId: string, taskId: string) => `/api/${userId}/tasks/${taskId}`,
} as const;

// ============================================================================
// UI-Extended Types
// ============================================================================

/**
 * Task with UI-specific state
 * Extends API response with client-side state
 */
export interface TaskWithUIState extends TaskResponse {
  /** Task is currently being edited */
  isEditing?: boolean;

  /** Task operation in progress */
  isLoading?: boolean;

  /** Task has pending optimistic update */
  isPending?: boolean;
}

/**
 * Task operation types
 */
export type TaskOperation = "create" | "update" | "delete" | "toggle";

/**
 * Task operation state
 */
export interface TaskOperationState {
  /** Operation type */
  operation: TaskOperation;

  /** Task ID (null for create) */
  taskId?: string;

  /** Operation in progress */
  isLoading: boolean;

  /** Operation error */
  error?: string;
}
