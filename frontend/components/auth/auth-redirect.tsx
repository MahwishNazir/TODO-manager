"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";

/**
 * Minimal client component for auth redirect only.
 * Keeps the landing page mostly server-rendered for better performance.
 */
export function AuthRedirect() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/tasks");
    }
  }, [isAuthenticated, isLoading, router]);

  // Render nothing - this component only handles redirect logic
  return null;
}
