"use client";

import { createContext, useContext, useEffect, useState } from "react";
import type { Session, User } from "@/src/lib/auth";

/**
 * Authentication context value.
 */
interface AuthContextValue {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

/**
 * Authentication context for global auth state management.
 */
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * AuthProvider component wraps the application to provide authentication context.
 *
 * @param children - Child components
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session/token on mount
    const checkAuth = async () => {
      try {
        // Check if JWT token exists in sessionStorage
        const token =
          typeof window !== "undefined"
            ? sessionStorage.getItem("jwt_token")
            : null;

        if (token) {
          // TODO: Fetch user session from Better Auth
          // For now, just mark as authenticated if token exists
          // This will be implemented when we add the Better Auth client SDK
        }
      } catch (error) {
        console.error("Failed to check authentication:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const value: AuthContextValue = {
    user,
    session,
    isLoading,
    isAuthenticated: !!user && !!session,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access authentication context.
 *
 * @returns AuthContextValue
 * @throws Error if used outside AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
