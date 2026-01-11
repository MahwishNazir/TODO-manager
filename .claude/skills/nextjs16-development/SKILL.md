---
name: nextjs16-development
description: Comprehensive guide for developing Next.js 16 applications with App Router, Server Components, and modern features for the Todo application Phase 2.
---

# Next.js 16 Development Guide

## Instructions

Use this skill when implementing Next.js 16 features for the Todo application in Phase 2. Follow these guidelines for proper implementation:

### 1. App Router Structure (Next.js 16)
- Use file-based routing with the App Router in the `app` directory
- Create pages with `page.tsx` files in route segments
- Create shared UI with `layout.tsx` files
- Root layout must include `html` and `body` tags
- Use square brackets `[param]` for dynamic route segments
- Use `PageProps<'/path'>` and `LayoutProps<'/path'>` for type safety

### 2. Server and Client Components (Critical)
- **Server Components** (default): No directive needed, run on server, can fetch data
- **Client Components**: Use `'use client'` directive when interactivity is needed
- Server Components can import Client Components, but not vice versa
- Use Server Components by default for data fetching and rendering

### 3. Async Request APIs (Next.js 16 Breaking Change - Critical!)
- **ALL** `params`, `searchParams`, `cookies`, `headers` must be accessed ASYNCHRONOUSLY
- Always use `await` when accessing these APIs in Server Components
- Correct: `const { slug } = await params`
- Incorrect: `const { slug } = params` (will cause runtime errors in Next.js 16)

### 4. Authentication Integration (Better Auth + JWT)
- Better Auth creates JWT tokens on frontend
- Frontend includes JWT in Authorization header for API calls
- FastAPI backend verifies JWT tokens and extracts user information
- All API endpoints should validate JWT and filter by user ID
- Use shared BETTER_AUTH_SECRET between frontend and backend

### 5. Server Actions for Data Mutations
- Use `'use server'` directive for server-side functions
- Use `revalidateTag` or `updateTag` for cache management
- Example:
```ts
'use server'
import { revalidateTag } from 'next/cache'

export async function createTask(formData: FormData) {
  const title = formData.get('title') as string
  const description = formData.get('description') as string

  const task = await db.tasks.create({ title, description })

  revalidateTag('user-tasks')
  return task
}
```

### 6. Performance Optimizations
- Enable `cacheComponents: true` in `next.config.ts` for Cache Components
- Use Server Components to reduce client bundle size
- Use `next/image` with proper `remotePatterns` configuration
- Implement proper loading and error boundaries
- Use Suspense for component-level loading states

### 7. Next.js 16 Configuration
```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,  // Enable Cache Components
  reactCompiler: true,    // Enable React Compiler (optional)

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'example.com',
      },
    ],
    qualities: [75, 85, 95],
    minimumCacheTTL: 14400, // 4 hours default in v16
  },

  experimental: {
    typedRoutes: true,  // Enable typed route helpers
  },
}

export default nextConfig
```

### 8. Environment Variables
- Server Components: `process.env.VARIABLE_NAME` (server-only)
- Client Components: `process.env.NEXT_PUBLIC_` (client-accessible)
- No more `serverRuntimeConfig` or `publicRuntimeConfig` (removed in v16)

### 9. Error Handling and Loading States
- Create `error.tsx` files for error boundaries
- Create `loading.tsx` files for loading states
- Use Suspense for component-level loading
- Handle errors gracefully in Server Actions

### 10. Removed Features (Do NOT use in Next.js 16)
- No AMP support (completely removed)
- No `next lint` command (use ESLint directly)
- No `serverRuntimeConfig` or `publicRuntimeConfig` (removed)
- No `next/legacy/image` component (deprecated)
- No `images.domains` config (use `remotePatterns`)

### 11. Installation Command
- Install Next.js 16 with all dependencies: `npx create-next-app@latest frontend`
  - This command creates a new Next.js 16 app with TypeScript, ESLint, Tailwind CSS, and App Router pre-configured
  - For an existing project: `npm install next@latest react@latest react-dom@latest`

## Examples

### Example 1: Server Component with Async Params (Next.js 16 Required)
```tsx
export default async function TaskPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params  // Critical: use await!
  const task = await getTask(id)

  return <div>{task.title}</div>
}
```

### Example 2: Authentication Check in Server Component
```tsx
import { cookies } from 'next/headers'
import { verifyAuth } from '@/lib/auth/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const token = cookies().get('better-auth_session_token')?.value
  const user = await verifyAuth(token)

  if (!user) {
    redirect('/login')
  }

  return <div>Welcome {user.name}</div>
}
```

### Example 3: Client Component Form with Server Action
```tsx
'use client'

import { createTask } from '@/actions/tasks'

export default function TaskForm() {
  return (
    <form action={createTask}>
      <input name="title" placeholder="Task title" required />
      <textarea name="description" placeholder="Description" />
      <button type="submit">Add Task</button>
    </form>
  )
}
```

## Best Practices

- Always use async/await for Request APIs in Next.js 16
- Leverage Server Components for data fetching
- Use Client Components only when client-side interactivity is required
- Implement proper TypeScript typing with PageProps and LayoutProps
- Use next/link for internal navigation with prefetching
- Enable and use the new caching APIs
- Follow the App Router file structure conventions
- Test with both development and production builds