/**
 * Authentication API Contracts
 * Feature: 004-frontend-ux
 * Date: 2026-01-14
 *
 * Defines TypeScript interfaces for Better Auth authentication endpoints
 * and session management types.
 */

// ============================================================================
// Session Types
// ============================================================================

/**
 * User session data returned by Better Auth
 */
export interface UserSession {
  /** Unique user identifier (UUID) */
  id: string;

  /** User's email address */
  email: string;

  /** User's display name (optional) */
  name?: string;

  /** Whether email is verified */
  emailVerified: boolean;

  /** Session creation timestamp (ISO 8601) */
  createdAt: string;

  /** Session update timestamp (ISO 8601) */
  updatedAt: string;
}

/**
 * Better Auth session response
 */
export interface SessionResponse {
  /** User data */
  user: UserSession;

  /** Session metadata */
  session: {
    id: string;
    userId: string;
    expiresAt: string;
    createdAt: string;
    updatedAt: string;
  };
}

// ============================================================================
// Sign Up
// ============================================================================

/**
 * POST /api/auth/sign-up/email
 *
 * Request body for user registration
 */
export interface SignUpRequest {
  /** User's email address */
  email: string;

  /** User's password (min 8 characters) */
  password: string;

  /** User's display name (optional) */
  name?: string;
}

/**
 * Sign up success response
 */
export interface SignUpResponse {
  /** JWT token (also set in HttpOnly cookie) */
  token: string;

  /** Created user data */
  user: {
    id: string;
    email: string;
    name?: string;
  };
}

/**
 * Sign up error codes
 */
export type SignUpErrorCode =
  | "USER_ALREADY_EXISTS"
  | "INVALID_EMAIL"
  | "PASSWORD_TOO_SHORT"
  | "VALIDATION_ERROR";

// ============================================================================
// Sign In
// ============================================================================

/**
 * POST /api/auth/sign-in/email
 *
 * Request body for user login
 */
export interface SignInRequest {
  /** User's email address */
  email: string;

  /** User's password */
  password: string;

  /** Remember me option (extends session) */
  rememberMe?: boolean;
}

/**
 * Sign in success response
 */
export interface SignInResponse {
  /** JWT token (also set in HttpOnly cookie) */
  token: string;

  /** Authenticated user data */
  user: {
    id: string;
    email: string;
    name?: string;
  };
}

/**
 * Sign in error codes
 */
export type SignInErrorCode =
  | "INVALID_CREDENTIALS"
  | "USER_NOT_FOUND"
  | "ACCOUNT_LOCKED"
  | "VALIDATION_ERROR";

// ============================================================================
// Sign Out
// ============================================================================

/**
 * POST /api/auth/sign-out
 *
 * No request body required (uses session cookie)
 */
export interface SignOutRequest {
  // Empty - authentication via cookie
}

/**
 * Sign out success response
 */
export interface SignOutResponse {
  /** Success indicator */
  success: boolean;
}

// ============================================================================
// Session
// ============================================================================

/**
 * GET /api/auth/session
 *
 * Get current session (uses session cookie)
 */
export interface GetSessionRequest {
  // Empty - authentication via cookie
}

/**
 * Get session response
 * Returns null if not authenticated
 */
export type GetSessionResponse = SessionResponse | null;

// ============================================================================
// Authentication Context Types
// ============================================================================

/**
 * Authentication state for React context
 */
export interface AuthState {
  /** Current user (null if not authenticated) */
  user: UserSession | null;

  /** Whether auth state is loading */
  isLoading: boolean;

  /** Whether user is authenticated */
  isAuthenticated: boolean;

  /** Error message if auth failed */
  error?: string;
}

/**
 * Authentication context value with methods
 */
export interface AuthContextValue extends AuthState {
  /** Sign up new user */
  signUp: (data: SignUpRequest) => Promise<SignUpResponse>;

  /** Sign in existing user */
  signIn: (data: SignInRequest) => Promise<SignInResponse>;

  /** Sign out current user */
  signOut: () => Promise<void>;

  /** Refresh session data */
  refreshSession: () => Promise<void>;
}

// ============================================================================
// JWT Types (for reference)
// ============================================================================

/**
 * JWT token payload structure
 * Used by backend for validation
 */
export interface JWTPayload {
  /** Subject - User ID */
  sub: string;

  /** User email */
  email: string;

  /** Issued at timestamp (Unix seconds) */
  iat: number;

  /** Expiration timestamp (Unix seconds) */
  exp: number;

  /** Issuer */
  iss: string;

  /** Audience */
  aud: string;
}

/**
 * JWT validation result
 */
export interface JWTValidationResult {
  /** Whether token is valid */
  valid: boolean;

  /** Decoded payload if valid */
  payload?: JWTPayload;

  /** Error message if invalid */
  error?: string;
}

// ============================================================================
// Route Protection Types
// ============================================================================

/**
 * Protected route configuration
 */
export interface ProtectedRouteConfig {
  /** Route path pattern */
  path: string;

  /** Redirect path if not authenticated */
  redirectTo: string;

  /** Optional: Required roles (future use) */
  roles?: string[];
}

/**
 * Default protected routes
 */
export const PROTECTED_ROUTES: ProtectedRouteConfig[] = [
  { path: "/tasks", redirectTo: "/signin" },
  { path: "/tasks/:id", redirectTo: "/signin" },
];

/**
 * Auth routes (redirect if already authenticated)
 */
export const AUTH_ROUTES: string[] = ["/signin", "/signup"];

/**
 * Default redirect after authentication
 */
export const DEFAULT_AUTH_REDIRECT = "/tasks";
