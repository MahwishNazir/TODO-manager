/**
 * HTTP status codes used by the API
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

export type HttpStatus = (typeof HTTP_STATUS)[keyof typeof HTTP_STATUS];

/**
 * Base API error response structure
 */
export interface ApiErrorResponse {
  /** Error detail message */
  detail: string;
}

/**
 * Validation error detail
 */
export interface ValidationErrorDetail {
  /** Location of the error (e.g., ["body", "title"]) */
  loc: (string | number)[];

  /** Error message */
  msg: string;

  /** Error type */
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
    const fieldName = error.loc[error.loc.length - 1];
    if (typeof fieldName === "string") {
      errors[fieldName] = error.msg;
    }
  }

  return errors;
}

/**
 * Custom API error class for frontend error handling
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public code?: string,
    public validationErrors?: FieldErrors
  ) {
    super(detail);
    this.name = "ApiError";
  }

  get isUnauthorized(): boolean {
    return this.status === HTTP_STATUS.UNAUTHORIZED;
  }

  get isForbidden(): boolean {
    return this.status === HTTP_STATUS.FORBIDDEN;
  }

  get isNotFound(): boolean {
    return this.status === HTTP_STATUS.NOT_FOUND;
  }

  get isValidationError(): boolean {
    return this.status === HTTP_STATUS.UNPROCESSABLE_ENTITY;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }

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

  static async fromResponse(response: Response): Promise<ApiError> {
    let detail = "Request failed";
    let code: string | undefined;
    let validationErrors: FieldErrors | undefined;

    try {
      const data = await response.json();

      if (response.status === HTTP_STATUS.UNPROCESSABLE_ENTITY) {
        const validationResponse = data as ValidationErrorResponse;
        validationErrors = parseValidationErrors(validationResponse);
        detail = "Validation failed";
      } else {
        detail = data.detail || detail;
        code = data.code;
      }
    } catch {
      detail = response.statusText || detail;
    }

    return new ApiError(response.status, detail, code, validationErrors);
  }
}

/**
 * Network error (no response from server)
 */
export class NetworkError extends Error {
  constructor(message: string = "Network error. Check your connection.") {
    super(message);
    this.name = "NetworkError";
  }
}
