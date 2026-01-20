"use client";

import { useAuth as useAuthProvider } from "@/components/providers/auth-provider";

/**
 * Hook to access authentication state and methods
 * Re-exports from AuthProvider for convenience
 */
export function useAuth() {
  return useAuthProvider();
}
