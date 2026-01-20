/**
 * Error Response Contracts
 * Feature: 004-frontend-ux
 * Date: 2026-01-14
 *
 * Defines TypeScript interfaces for API error responses
 * and error handling utilities.
 */

// ============================================================================
// HTTP Status Codes
// ============================================================================

/**
 * HTTP status codes used by the API
 */
export const HTTP_STATUS = {
  // Success
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,

  // Client Errors
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,

  // Server Errors
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

export type HttpStatus = (typeof HTTP_STATUS)[keyof typeof HTTP_STATUS];

// ============================================================================
// Base Error Response
// ============================================================================

/**
 * Base API error response structure
 * Matches FastAPI's default error response format
 */
export interface ApiErrorResponse {
  /** Error detail message */
  detail: string;
}

/**
 * Extended error response with additional metadata
 */
export interface ExtendedErrorResponse extends ApiErrorResponse {
  /** HTTP status code */
  status?: number;

  /** Error code for programmatic handling */
  code?: string;

  /** Timestamp of error */
  timestamp?: string;

  /** Request ID for debugging */
  requestId?: string;
}

// ============================================================================
// Validation Errors (422)
// ============================================================================

/**
 * Single validation error detail
 * Matches FastAPI's RequestValidationError format
 */
export interface ValidationErrorDetail {
  /** Location of the error (e.g., ["body", "title"]) */
  loc: (string | number)[];

  /** Error message */
  msg: string;

  /** Error type (e.g., "value_error", "type_error") */
  type: string;
}

/**
 * Validation error response (422 Unprocessable Entity)
 */
export interface ValidationErrorResponse {
  /** Array of validation errors */
  detail: ValidationErrorDetail[];
}

/**
 * Parsed validation errors keyed by field name
 */
export type FieldErrors = Record<string, string>;

/**
 * Parse validation error response into field errors
 */
export function parseValidationErrors(
  response: ValidationErrorResponse
): FieldErrors {
  const errors: FieldErrors = {};

  for (const error of response.detail) {
    // Get field name from location (last element of body path)
    const fieldName = error.loc[error.loc.length - 1];
    if (typeof fieldName === "string") {
      errors[fieldName] = error.msg;
    }
  }

  return errors;
}

// ============================================================================
// Authentication Errors (401, 403)
// ============================================================================

/**
 * Authentication error codes
 */
export type AuthErrorCode =
  | "UNAUTHORIZED"
  | "TOKEN_EXPIRED"
  | "TOKEN_INVALID"
  | "TOKEN_MISSING"
  | "SESSION_EXPIRED";

/**
 * Authorization error codes
 */
export type AuthorizationErrorCode =
  | "FORBIDDEN"
  | "ACCESS_DENIED"
  | "USER_MISMATCH"
  | "INSUFFICIENT_PERMISSIONS";

/**
 * Authentication error response (401 Unauthorized)
 */
export interface AuthErrorResponse extends ApiErrorResponse {
  /** Specific auth error code */
  code?: AuthErrorCode;
}

/**
 * Authorization error response (403 Forbidden)
 */
export interface ForbiddenErrorResponse extends ApiErrorResponse {
  /** Specific authorization error code */
  code?: AuthorizationErrorCode;
}

// ============================================================================
// Not Found Errors (404)
// ============================================================================

/**
 * Resource not found error codes
 */
export type NotFoundErrorCode = "TASK_NOT_FOUND" | "USER_NOT_FOUND" | "NOT_FOUND";

/**
 * Not found error response (404 Not Found)
 */
export interface NotFoundErrorResponse extends ApiErrorResponse {
  /** Specific not found error code */
  code?: NotFoundErrorCode;

  /** Resource type that was not found */
  resourceType?: string;

  /** Resource ID that was not found */
  resourceId?: string;
}

// ============================================================================
// Server Errors (500, 503)
// ============================================================================

/**
 * Server error codes
 */
export type ServerErrorCode =
  | "INTERNAL_ERROR"
  | "DATABASE_ERROR"
  | "SERVICE_UNAVAILABLE"
  | "UNKNOWN_ERROR";

/**
 * Server error response (500 Internal Server Error)
 */
export interface ServerErrorResponse extends ApiErrorResponse {
  /** Specific server error code */
  code?: ServerErrorCode;

  /** Request ID for support debugging */
  requestId?: string;
}

// ============================================================================
// Custom API Error Class
// ============================================================================

/**
 * Custom API error class for frontend error handling
 */
export class ApiError extends Error {
  constructor(
    /** HTTP status code */
    public status: number,
    /** Error detail message */
    public detail: string,
    /** Optional error code */
    public code?: string,
    /** Optional validation errors */
    public validationErrors?: FieldErrors
  ) {
    super(detail);
    this.name = "ApiError";
  }

  /** Check if error is authentication error (401) */
  get isUnauthorized(): boolean {
    return this.status === HTTP_STATUS.UNAUTHORIZED;
  }

  /** Check if error is authorization error (403) */
  get isForbidden(): boolean {
    return this.status === HTTP_STATUS.FORBIDDEN;
  }

  /** Check if error is not found error (404) */
  get isNotFound(): boolean {
    return this.status === HTTP_STATUS.NOT_FOUND;
  }

  /** Check if error is validation error (422) */
  get isValidationError(): boolean {
    return this.status === HTTP_STATUS.UNPROCESSABLE_ENTITY;
  }

  /** Check if error is server error (5xx) */
  get isServerError(): boolean {
    return this.status >= 500;
  }

  /** Check if error is client error (4xx) */
  get isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  /** Get user-friendly error message */
  get userMessage(): string {
    switch (this.status) {
      case HTTP_STATUS.UNAUTHORIZED:
        return "Your session has expired. Please log in again.";
      case HTTP_STATUS.FORBIDDEN:
        return "You don't have permission to perform this action.";
      case HTTP_STATUS.NOT_FOUND:
        return "The requested resource was not found.";
      case HTTP_STATUS.UNPROCESSABLE_ENTITY:
        return "Please check your input and try again.";
      case HTTP_STATUS.INTERNAL_SERVER_ERROR:
        return "Something went wrong. Please try again later.";
      case HTTP_STATUS.SERVICE_UNAVAILABLE:
        return "Service is temporarily unavailable. Please try again later.";
      default:
        return this.detail || "An error occurred. Please try again.";
    }
  }

  /** Create ApiError from fetch response */
  static async fromResponse(response: Response): Promise<ApiError> {
    let detail = "Request failed";
    let code: string | undefined;
    let validationErrors: FieldErrors | undefined;

    try {
      const data = await response.json();

      if (response.status === HTTP_STATUS.UNPROCESSABLE_ENTITY) {
        // Validation error - parse field errors
        const validationResponse = data as ValidationErrorResponse;
        validationErrors = parseValidationErrors(validationResponse);
        detail = "Validation failed";
      } else {
        detail = data.detail || detail;
        code = data.code;
      }
    } catch {
      // Response body not JSON or empty
      detail = response.statusText || detail;
    }

    return new ApiError(response.status, detail, code, validationErrors);
  }
}

// ============================================================================
// Error Message Maps
// ============================================================================

/**
 * User-friendly error messages by status code
 */
export const ERROR_MESSAGES: Record<number, string> = {
  [HTTP_STATUS.BAD_REQUEST]: "Invalid request. Please check your input.",
  [HTTP_STATUS.UNAUTHORIZED]: "Please log in to continue.",
  [HTTP_STATUS.FORBIDDEN]: "You don't have permission to do this.",
  [HTTP_STATUS.NOT_FOUND]: "The item you're looking for doesn't exist.",
  [HTTP_STATUS.CONFLICT]: "This action conflicts with existing data.",
  [HTTP_STATUS.UNPROCESSABLE_ENTITY]: "Please check your input and try again.",
  [HTTP_STATUS.INTERNAL_SERVER_ERROR]: "Something went wrong. Please try again.",
  [HTTP_STATUS.SERVICE_UNAVAILABLE]: "Service is temporarily unavailable.",
};

/**
 * Get user-friendly error message for status code
 */
export function getErrorMessage(status: number, fallback?: string): string {
  return ERROR_MESSAGES[status] || fallback || "An error occurred.";
}

// ============================================================================
// Error Handling Utilities
// ============================================================================

/**
 * Check if error requires authentication redirect
 */
export function requiresAuthRedirect(error: ApiError): boolean {
  return error.isUnauthorized || error.isForbidden;
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: ApiError): boolean {
  // Retry on server errors and network issues, not on client errors
  return error.isServerError || error.status === 0; // status 0 = network error
}

/**
 * Error action to take based on error type
 */
export type ErrorAction =
  | { type: "redirect"; path: string }
  | { type: "toast"; message: string; variant: "error" | "warning" }
  | { type: "inline"; errors: FieldErrors }
  | { type: "retry"; message: string };

/**
 * Determine action to take for an error
 */
export function getErrorAction(error: ApiError): ErrorAction {
  if (error.isUnauthorized || error.isForbidden) {
    return { type: "redirect", path: "/signin" };
  }

  if (error.isValidationError && error.validationErrors) {
    return { type: "inline", errors: error.validationErrors };
  }

  if (error.isServerError) {
    return { type: "retry", message: error.userMessage };
  }

  return { type: "toast", message: error.userMessage, variant: "error" };
}

// ============================================================================
// Network Error
// ============================================================================

/**
 * Network error (no response from server)
 */
export class NetworkError extends Error {
  constructor(message: string = "Network error. Check your connection.") {
    super(message);
    this.name = "NetworkError";
  }
}

/**
 * Check if error is network error
 */
export function isNetworkError(error: unknown): error is NetworkError {
  return error instanceof NetworkError;
}

/**
 * Create appropriate error from fetch failure
 */
export function createErrorFromFetch(error: unknown): ApiError | NetworkError {
  if (error instanceof ApiError) {
    return error;
  }

  if (error instanceof TypeError && error.message.includes("fetch")) {
    return new NetworkError();
  }

  return new ApiError(
    HTTP_STATUS.INTERNAL_SERVER_ERROR,
    error instanceof Error ? error.message : "Unknown error"
  );
}
