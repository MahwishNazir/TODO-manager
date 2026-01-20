# Research: Frontend Application & UX (Production-Ready)

**Feature**: 004-frontend-ux
**Date**: 2026-01-14
**Status**: Complete

## 1. Next.js 16 App Router Patterns

### Server Components vs Client Components

**Decision**: Use Server Components by default, Client Components only when needed for interactivity.

**Rationale**:
- Server Components reduce JavaScript bundle size
- Better performance for initial page load
- Client Components required for: useState, useEffect, event handlers, browser APIs

**Patterns**:
```typescript
// Server Component (default) - page.tsx
export default async function TasksPage() {
  // Can fetch data directly, no "use client" directive
  return <TaskList />;
}

// Client Component - task-list.tsx
"use client";
import { useState } from "react";

export function TaskList() {
  const [tasks, setTasks] = useState([]);
  // Interactive component with state
}
```

### Async Params in Next.js 16

**Decision**: Use `Promise<{ id: string }>` type for dynamic route params.

**Rationale**:
- Next.js 16 changed params to be async
- Must await params before accessing values
- Prevents hydration mismatches

**Pattern**:
```typescript
// app/tasks/[id]/page.tsx
type Props = {
  params: Promise<{ id: string }>;
};

export default async function TaskDetailPage({ params }: Props) {
  const { id } = await params;
  // Now use id safely
}
```

**Alternatives Considered**:
- Sync params (deprecated in Next.js 16)
- useParams hook (only in Client Components)

---

## 2. Better Auth JWT Integration

### Shared Secret Configuration

**Decision**: Use HS256 algorithm with shared `BETTER_AUTH_SECRET` between frontend and backend.

**Rationale**:
- Simpler than RSA key pairs
- Same secret validates tokens on both ends
- FastAPI backend already configured for HS256

**Frontend Configuration** (lib/auth.ts):
```typescript
import { betterAuth } from "better-auth";
import { Pool } from "@neondatabase/serverless";

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  secret: process.env.BETTER_AUTH_SECRET,
  session: {
    expiresIn: 60 * 60, // 1 hour
    updateAge: 60 * 5,  // Refresh every 5 minutes
  },
  advanced: {
    generateId: () => crypto.randomUUID(),
  },
});
```

**Environment Variables**:
```bash
# .env.local
BETTER_AUTH_SECRET=946ce734e0f4d857fbd8f999c759335349f986f9fb7c9bbacab57b0e102a0887
DATABASE_URL=postgresql://...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### HttpOnly Cookie Storage

**Decision**: Store JWT in HttpOnly cookies (not localStorage).

**Rationale**:
- XSS protection (JavaScript cannot access cookie)
- Automatic inclusion in requests
- Better Auth handles cookie management

**Implementation**:
- Better Auth sets `better-auth.session_token` cookie automatically
- Backend validates token from cookie or Authorization header
- CORS must allow credentials: `credentials: "include"`

---

## 3. shadcn/ui Component Selection

### Components Needed

| Component | Purpose | shadcn/ui Name |
|-----------|---------|----------------|
| Button | Actions (Add, Edit, Delete, Submit) | `button` |
| Card | Task item container | `card` |
| Checkbox | Task completion toggle | `checkbox` |
| Dialog | Task creation/edit modal | `dialog` |
| Form | Form wrapper with validation | `form` |
| Input | Text input for task title | `input` |
| Label | Form field labels | `label` |
| Skeleton | Loading placeholders | `skeleton` |
| Toast | Notification messages | `sonner` (via toast) |
| Alert Dialog | Delete confirmation | `alert-dialog` |
| Dropdown Menu | Task actions menu | `dropdown-menu` |

### Installation Commands

```bash
# Initialize shadcn/ui
npx shadcn@latest init

# Install required components
npx shadcn@latest add button card checkbox dialog form input label skeleton alert-dialog dropdown-menu

# Install Sonner for toasts (separate package)
npm install sonner
```

### Customization

**Decision**: Use default shadcn/ui styles with custom theme colors.

**Rationale**:
- Consistent design system
- Accessible by default (Radix UI primitives)
- Easy to customize via CSS variables

---

## 4. Tailwind CSS Dual-Theme System

### Theme Configuration

**Decision**: LinkedIn Wrapped theme (light) + Regulatis AI theme (dark).

**Light Theme (LinkedIn Wrapped)**:
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --primary: 210 100% 45%; /* LinkedIn blue */
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --muted: 210 40% 96.1%;
  --accent: 210 40% 96.1%;
  --destructive: 0 84.2% 60.2%;
  --border: 214.3 31.8% 91.4%;
  --ring: 210 100% 45%;
}
```

**Dark Theme (Regulatis AI)**:
```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%; /* Bright blue accent */
  --primary-foreground: 222.2 47.4% 11.2%;
  --secondary: 217.2 32.6% 17.5%;
  --muted: 217.2 32.6% 17.5%;
  --accent: 217.2 32.6% 17.5%;
  --destructive: 0 62.8% 30.6%;
  --border: 217.2 32.6% 17.5%;
  --ring: 212.7 26.8% 83.9%;
}
```

### Theme Switching with next-themes

```typescript
// components/providers/theme-provider.tsx
"use client";
import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}
```

---

## 5. Form Validation with React Hook Form + Zod

### Validation Schema Pattern

**Decision**: Define Zod schemas that generate TypeScript types.

**Task Form Schema**:
```typescript
// lib/validations.ts
import { z } from "zod";

export const taskFormSchema = z.object({
  title: z
    .string()
    .min(1, "Task title is required")
    .max(500, "Title must be 500 characters or less")
    .trim(),
});

export type TaskFormData = z.infer<typeof taskFormSchema>;

export const authFormSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  name: z.string().optional(),
});

export type AuthFormData = z.infer<typeof authFormSchema>;
```

### Form Component Pattern

```typescript
// components/tasks/task-form.tsx
"use client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { taskFormSchema, TaskFormData } from "@/lib/validations";

export function TaskForm({ onSubmit }: { onSubmit: (data: TaskFormData) => void }) {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: { title: "" },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Task Title</FormLabel>
              <FormControl>
                <Input placeholder="Enter task title..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Creating..." : "Create Task"}
        </Button>
      </form>
    </Form>
  );
}
```

---

## 6. API Client Architecture

### JWT Token Injection Pattern

**Decision**: Create centralized API client with automatic token handling.

**Implementation**:
```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
    credentials: "include", // Include cookies for JWT
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(response.status, error.detail || "Request failed");
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}
```

### Task API Methods

```typescript
// lib/api-client.ts (continued)
export const tasksApi = {
  list: (userId: string) =>
    apiClient<TaskResponse[]>(`/api/${userId}/tasks`),

  get: (userId: string, taskId: string) =>
    apiClient<TaskResponse>(`/api/${userId}/tasks/${taskId}`),

  create: (userId: string, data: TaskCreate) =>
    apiClient<TaskResponse>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (userId: string, taskId: string, data: TaskUpdate) =>
    apiClient<TaskResponse>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  toggleComplete: (userId: string, taskId: string) =>
    apiClient<TaskResponse>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
    }),

  delete: (userId: string, taskId: string) =>
    apiClient<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    }),
};
```

---

## 7. Error Handling Patterns

### API Error Handling

**Decision**: Catch errors at component level, show toast notifications.

**Pattern**:
```typescript
// hooks/use-tasks.ts
import { toast } from "sonner";

export function useTasks(userId: string) {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await tasksApi.list(userId);
      setTasks(data);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          toast.error("Session expired. Please log in again.");
          // Redirect to signin
        } else {
          setError(err.message);
          toast.error(err.message);
        }
      } else {
        setError("An unexpected error occurred");
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return { tasks, isLoading, error, fetchTasks, refetch: fetchTasks };
}
```

### Error Response Types

| Status | Error Type | User Message | Action |
|--------|------------|--------------|--------|
| 400 | Validation Error | "Invalid input: {details}" | Show inline error |
| 401 | Unauthorized | "Session expired" | Redirect to /signin |
| 403 | Forbidden | "Access denied" | Redirect to /signin |
| 404 | Not Found | "Task not found" | Show 404 page |
| 500 | Server Error | "Something went wrong" | Show retry button |

---

## 8. Toast Notifications with Sonner

### Configuration

```typescript
// app/layout.tsx
import { Toaster } from "sonner";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster position="bottom-right" richColors closeButton />
      </body>
    </html>
  );
}
```

### Usage Patterns

```typescript
import { toast } from "sonner";

// Success
toast.success("Task created successfully");

// Error
toast.error("Failed to create task. Please try again.");

// Loading with promise
toast.promise(createTask(data), {
  loading: "Creating task...",
  success: "Task created!",
  error: "Failed to create task",
});

// With action button
toast.error("Failed to load tasks", {
  action: {
    label: "Retry",
    onClick: () => fetchTasks(),
  },
});
```

---

## 9. Loading State Patterns

### Skeleton Loaders

**Decision**: Use skeleton components that match final content dimensions.

**Pattern**:
```typescript
// components/tasks/task-skeleton.tsx
import { Skeleton } from "@/components/ui/skeleton";

export function TaskSkeleton() {
  return (
    <div className="flex items-center space-x-4 p-4 border rounded-lg">
      <Skeleton className="h-5 w-5 rounded" /> {/* Checkbox */}
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-3/4" /> {/* Title */}
        <Skeleton className="h-3 w-1/4" /> {/* Date */}
      </div>
      <Skeleton className="h-8 w-20" /> {/* Actions */}
    </div>
  );
}

export function TaskListSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <TaskSkeleton key={i} />
      ))}
    </div>
  );
}
```

### Button Loading States

```typescript
<Button disabled={isLoading}>
  {isLoading ? (
    <>
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      Creating...
    </>
  ) : (
    "Create Task"
  )}
</Button>
```

---

## 10. Responsive Design Patterns

### Mobile-First Approach

**Breakpoints**:
- Default: Mobile (< 768px)
- `md:`: Tablet (768px - 1023px)
- `lg:`: Desktop (≥ 1024px)

**Grid Layout Pattern**:
```typescript
// Task list responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {tasks.map((task) => (
    <TaskCard key={task.id} task={task} />
  ))}
</div>
```

**Touch Target Sizing**:
```typescript
// Ensure 44x44px minimum touch targets
<Button className="min-h-[44px] min-w-[44px] p-3">
  <Trash2 className="h-5 w-5" />
</Button>

// Checkbox with adequate touch area
<div className="p-2"> {/* Padding adds touch area */}
  <Checkbox className="h-5 w-5" />
</div>
```

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Component Model | Server Components default, Client when needed | Performance, reduced JS bundle |
| Params | Async params with await | Next.js 16 requirement |
| JWT Storage | HttpOnly cookies | Security (XSS protection) |
| Auth Library | Better Auth with HS256 | Shared secret with FastAPI |
| UI Components | shadcn/ui | Accessible, customizable |
| Theme | LinkedIn Wrapped (light) + Regulatis AI (dark) | User preference support |
| Validation | React Hook Form + Zod | Type-safe, excellent DX |
| API Client | Centralized with credentials | Consistent token handling |
| Errors | Try-catch + toast | User-friendly feedback |
| Loading | Skeleton loaders | Zero layout shift |
| Responsive | Tailwind mobile-first | Industry best practice |

---

**Research Status**: ✅ Complete - All technical decisions documented
**Next Step**: Create data-model.md with TypeScript interfaces
