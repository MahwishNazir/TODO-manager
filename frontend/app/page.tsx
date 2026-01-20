import Link from "next/link";
import { Button } from "@/components/ui/button";
import { AuthRedirect } from "@/components/auth/auth-redirect";
import { ThemeToggle } from "@/components/layout/theme-toggle";

// Static SVG icons (no JS bundle cost)
function ListIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-primary">
      <rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/><path d="M14 4h7"/><path d="M14 9h7"/><path d="M14 15h7"/><path d="M14 20h7"/>
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-primary">
      <circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>
    </svg>
  );
}

function ZapIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-primary">
      <path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>
    </svg>
  );
}

export default function Home() {
  return (
    <>
      {/* Client component for auth redirect - minimal JS */}
      <AuthRedirect />

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
                  <ListIcon />
                </div>
                <h3 className="font-semibold mb-2">Simple Task Management</h3>
                <p className="text-sm text-muted-foreground text-center">
                  Create, edit, and organize your tasks with ease
                </p>
              </div>

              <div className="flex flex-col items-center p-6 rounded-lg bg-card border transition-shadow hover:shadow-md">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <CheckIcon />
                </div>
                <h3 className="font-semibold mb-2">Track Progress</h3>
                <p className="text-sm text-muted-foreground text-center">
                  Mark tasks complete and see your accomplishments
                </p>
              </div>

              <div className="flex flex-col items-center p-6 rounded-lg bg-card border transition-shadow hover:shadow-md">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <ZapIcon />
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
    </>
  );
}
