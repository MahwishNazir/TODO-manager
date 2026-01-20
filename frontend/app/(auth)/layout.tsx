"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Loader2 } from "lucide-react";
import { DEFAULT_AUTH_REDIRECT } from "@/lib/constants";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Redirect to tasks if already authenticated
    if (!isLoading && isAuthenticated) {
      router.push(DEFAULT_AUTH_REDIRECT);
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // If authenticated, show nothing (will redirect)
  if (isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
