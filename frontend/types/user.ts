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

  /** Error message if auth failed */
  error?: string;
}
