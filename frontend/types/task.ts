/**
 * Task response from backend API
 * Matches backend TaskResponse schema exactly
 */
export interface TaskResponse {
  /** Unique task identifier (auto-incrementing integer) */
  id: number;

  /** Owner user ID */
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
 * Task list response from backend API
 * Matches backend TaskListResponse schema exactly
 */
export interface TaskListResponse {
  /** List of tasks */
  tasks: TaskResponse[];

  /** Number of tasks returned */
  count: number;
}

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
