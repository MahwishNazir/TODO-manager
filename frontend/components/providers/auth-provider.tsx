"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useSession, signOut as authSignOut } from "@/lib/auth-client";
import { clearAuthToken } from "@/lib/api-client";
import type { UserSession, AuthState } from "@/types/user";

interface AuthContextValue extends AuthState {
  signOut: () => Promise<void>;
  refreshSession: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, isPending, error, refetch } = useSession();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isPending) {
      setIsLoading(false);
    }
  }, [isPending]);

  const user: UserSession | null = session?.user
    ? {
        id: session.user.id,
        email: session.user.email,
        name: session.user.name || undefined,
        emailVerified: session.user.emailVerified,
        createdAt: session.user.createdAt?.toString() || new Date().toISOString(),
        updatedAt: session.user.updatedAt?.toString() || new Date().toISOString(),
      }
    : null;

  const handleSignOut = async () => {
    clearAuthToken(); // Clear cached JWT token
    await authSignOut();
    refetch();
  };

  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated: !!user,
    error: error?.message,
    signOut: handleSignOut,
    refreshSession: refetch,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
