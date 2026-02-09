import { API_BASE_URL } from "./constants";
import { ApiError, NetworkError } from "@/types/api";
import type { TaskResponse, TaskCreate, TaskUpdate, TaskListResponse } from "@/types/task";

interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
}

// Token cache
let cachedToken: string | null = null;
let tokenExpiresAt: number = 0;

/**
 * Get JWT token for backend API calls.
 * Fetches from /api/token and caches for reuse.
 */
async function getAuthToken(): Promise<string | null> {
  // Check if we have a valid cached token
  const now = Date.now();
  if (cachedToken && tokenExpiresAt > now + 60000) {
    // Token still valid with 1 min buffer
    return cachedToken;
  }

  try {
    const response = await fetch("/api/token", {
      credentials: "include",
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Not authenticated
        cachedToken = null;
        tokenExpiresAt = 0;
        return null;
      }
      throw new Error("Failed to get auth token");
    }

    const data = await response.json();
    cachedToken = data.token;
    tokenExpiresAt = now + (data.expiresIn * 1000);
    return cachedToken;
  } catch (error) {
    console.error("Error getting auth token:", error);
    return null;
  }
}

/**
 * Clear the cached token (call on logout)
 */
export function clearAuthToken(): void {
  cachedToken = null;
  tokenExpiresAt = 0;
}

/**
 * Generic API client with automatic error handling
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  // Get JWT token for authorization
  if (!skipAuth) {
    const token = await getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      throw await ApiError.fromResponse(response);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null as T;
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Handle network errors (including CORS failures)
    if (error instanceof TypeError) {
      console.error("Network/CORS error:", error.message);
      throw new NetworkError(`Unable to connect to server: ${error.message}`);
    }
    console.error("Unexpected API error:", error);
    throw new ApiError(500, error instanceof Error ? error.message : "Unknown error");
  }
}

/**
 * Task API methods
 */
export const tasksApi = {
  /**
   * List all tasks for user
   */
  list: (userId: string): Promise<TaskListResponse> =>
    apiClient<TaskListResponse>(`/api/${userId}/tasks`),

  /**
   * Get a single task
   */
  get: (userId: string, taskId: number): Promise<TaskResponse> =>
    apiClient<TaskResponse>(`/api/${userId}/tasks/${taskId}`),

  /**
   * Create a new task
   */
  create: (userId: string, data: TaskCreate): Promise<TaskResponse> =>
    apiClient<TaskResponse>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  /**
   * Update a task's title
   */
  update: (userId: string, taskId: number, data: TaskUpdate): Promise<TaskResponse> =>
    apiClient<TaskResponse>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  /**
   * Toggle task completion status
   */
  toggleComplete: (userId: string, taskId: number): Promise<TaskResponse> =>
    apiClient<TaskResponse>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
    }),

  /**
   * Delete a task
   */
  delete: (userId: string, taskId: number): Promise<void> =>
    apiClient<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    }),
};
