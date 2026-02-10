"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { LogOut, User, ListTodo, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { useRouter, usePathname } from "next/navigation";
import { MobileNav } from "./mobile-nav";
import { ThemeToggle } from "./theme-toggle";
import { cn } from "@/lib/utils";

export function Header() {
  const { user, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleSignOut = async () => {
    try {
      await signOut();
      toast.success("Signed out successfully");
      router.push("/");
      router.refresh();
    } catch (error) {
      toast.error("Failed to sign out");
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-4">
          {/* Mobile Navigation */}
          <MobileNav />

          <Link href="/tasks" className="flex items-center gap-2">
            <ListTodo className="h-6 w-6 text-primary" />
            <span className="brand-text brand-gradient text-xl">TaskFlow</span>
          </Link>

          {/* Desktop Navigation Links (T016 active state) */}
          <nav className="hidden md:flex items-center gap-1 ml-6">
            <Link href="/tasks">
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  "gap-2",
                  pathname === "/tasks" && "bg-primary/10 text-primary"
                )}
              >
                <ListTodo className="h-4 w-4" />
                Tasks
              </Button>
            </Link>
            <Link href="/chat">
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  "gap-2",
                  pathname === "/chat" && "bg-primary/10 text-primary"
                )}
              >
                <MessageSquare className="h-4 w-4" />
                Chat
              </Button>
            </Link>
          </nav>
        </div>

        {/* Desktop User Menu */}
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <div className="hidden md:flex items-center gap-4">
          {user && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2 min-h-[44px]">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <span>{user.name || user.email}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span className="font-medium">{user.name || "User"}</span>
                    <span className="text-xs text-muted-foreground">{user.email}</span>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleSignOut} className="text-destructive min-h-[44px]">
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
          </div>
        </div>
      </div>
    </header>
  );
}
