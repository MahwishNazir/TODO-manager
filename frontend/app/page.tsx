"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { CheckCircle2, ListTodo, Zap, Loader2 } from "lucide-react";
import { ThemeToggle } from "@/components/layout/theme-toggle";

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/tasks");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background to-muted/50">
      {/* Theme Toggle in Corner */}
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <div className="container mx-auto px-4 py-16">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="mb-8">
            <h1 className="text-4xl sm:text-5xl font-bold text-primary mb-4">TaskFlow</h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-md">
              A modern, responsive task management app to keep you organized and productive.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 mb-16 w-full sm:w-auto">
            <Button asChild size="lg" className="min-h-[44px]">
              <Link href="/signup">Get Started</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="min-h-[44px]">
              <Link href="/signin">Sign In</Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 max-w-4xl w-full">
            <div className="flex flex-col items-center p-6 rounded-lg bg-card border transition-shadow hover:shadow-md">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <ListTodo className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Simple Task Management</h3>
              <p className="text-sm text-muted-foreground text-center">
                Create, edit, and organize your tasks with ease
              </p>
            </div>

            <div className="flex flex-col items-center p-6 rounded-lg bg-card border transition-shadow hover:shadow-md">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <CheckCircle2 className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Track Progress</h3>
              <p className="text-sm text-muted-foreground text-center">
                Mark tasks complete and see your accomplishments
              </p>
            </div>

            <div className="flex flex-col items-center p-6 rounded-lg bg-card border transition-shadow hover:shadow-md">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Fast & Responsive</h3>
              <p className="text-sm text-muted-foreground text-center">
                Works great on desktop, tablet, and mobile
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
