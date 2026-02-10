"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Menu, LogOut, User, ListTodo, Home, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { useRouter, usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function MobileNav() {
  const { user, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const handleSignOut = async () => {
    try {
      setIsOpen(false);
      await signOut();
      toast.success("Signed out successfully");
      router.push("/");
      router.refresh();
    } catch (error) {
      toast.error("Failed to sign out");
    }
  };

  const handleNavigation = (href: string) => {
    setIsOpen(false);
    router.push(href);
  };

  const navItems = [
    { href: "/tasks", label: "Tasks", icon: ListTodo },
    { href: "/chat", label: "Chat", icon: MessageSquare },
  ];

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden min-h-[44px] min-w-[44px]"
          aria-label="Open menu"
        >
          <Menu className="h-6 w-6" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[280px] sm:w-[320px]">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <ListTodo className="h-6 w-6 text-primary" />
            <span>TaskFlow</span>
          </SheetTitle>
        </SheetHeader>

        <div className="flex flex-col h-[calc(100%-4rem)] mt-6">
          {/* User Info */}
          {user && (
            <div className="flex items-center gap-3 px-2 py-4 border-b">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="h-5 w-5 text-primary" />
              </div>
              <div className="flex flex-col overflow-hidden">
                <span className="font-medium truncate">{user.name || "User"}</span>
                <span className="text-sm text-muted-foreground truncate">
                  {user.email}
                </span>
              </div>
            </div>
          )}

          {/* Navigation Links */}
          <nav className="flex-1 py-4">
            <ul className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <button
                      onClick={() => handleNavigation(item.href)}
                      className={cn(
                        "flex items-center gap-3 w-full px-3 py-3 rounded-lg text-left transition-colors min-h-[44px]",
                        isActive
                          ? "bg-primary/10 text-primary font-medium"
                          : "hover:bg-muted"
                      )}
                    >
                      <Icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Sign Out Button */}
          {user && (
            <div className="border-t pt-4">
              <button
                onClick={handleSignOut}
                className="flex items-center gap-3 w-full px-3 py-3 rounded-lg text-left text-destructive hover:bg-destructive/10 transition-colors min-h-[44px]"
              >
                <LogOut className="h-5 w-5" />
                <span>Sign out</span>
              </button>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
