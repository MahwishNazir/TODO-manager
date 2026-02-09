/**
 * API base URL
 *
 * Empty string = same origin. Backend requests are proxied via
 * next.config.ts rewrites to eliminate CORS issues.
 */
export const API_BASE_URL = "";

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
 * Application routes
 */
export const ROUTES = {
  HOME: "/",
  SIGNIN: "/signin",
  SIGNUP: "/signup",
  TASKS: "/tasks",
  TASK_DETAIL: (id: number) => `/tasks/${id}`,
  CHAT: "/chat",
} as const;

/**
 * Protected routes that require authentication
 */
export const PROTECTED_ROUTES = ["/tasks", "/chat"] as const;

/**
 * Auth routes (redirect to /tasks if already authenticated)
 */
export const AUTH_ROUTES = ["/signin", "/signup"] as const;

/**
 * Default redirect after authentication
 */
export const DEFAULT_AUTH_REDIRECT = "/tasks";
