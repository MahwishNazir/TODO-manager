# Next.js 16 Reference for Todo App Development

## Key Next.js 16 Features

### Cache Components
- Enable with `cacheComponents: true` in `next.config.ts`
- Optimizes data fetching operations in Server Components
- Excludes non-cached data from pre-renders unless explicitly cached
- Improves performance for dynamic data fetching

### React 19.2 Features
- **View Transitions**: Animate elements during transitions
- **useEffectEvent**: Extract non-reactive logic from Effects
- **Activity**: Render background activity with `display: none`

### Async Request APIs (Breaking Change)
- `cookies`, `headers`, `params`, `searchParams` must be awaited
- This is a **critical breaking change** in Next.js 16
- Failure to await will cause runtime errors

### Turbopack by Default
- Turbopack is now the default bundler for both dev and build
- No need for `--turbopack` flag anymore
- For custom webpack configs, use `--webpack` to opt out

## Common Todo App Implementation Patterns

### Task List Page
```tsx
// app/tasks/page.tsx
import { getTasks } from '@/lib/api/tasks'
import TaskList from '@/components/tasks/TaskList'

export default async function TasksPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string; page?: string }>
}) {
  const { status, page = '1' } = await searchParams
  const tasks = await getTasks({ status, page: Number(page) })

  return <TaskList tasks={tasks} />
}
```

### Protected Dashboard Route
```tsx
// app/dashboard/page.tsx
import { auth } from '@/lib/auth/server'

export default async function DashboardPage() {
  const session = await auth()
  if (!session) {
    redirect('/login')
  }

  return (
    <div>
      <h1>Dashboard</h1>
      {/* Dashboard content */}
    </div>
  )
}
```

### API Route with Authentication
```ts
// app/api/tasks/route.ts
import { cookies } from 'next/headers'
import { verifyAuth } from '@/lib/auth/server'

export async function GET(request: Request) {
  const token = cookies().get('better-auth_session_token')?.value
  if (!token) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const user = await verifyAuth(token)
  if (!user) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Return user's tasks
  const tasks = await getUserTasks(user.id)
  return Response.json(tasks)
}
```

## Authentication Flow

### Frontend (Next.js)
1. User logs in via Better Auth
2. Better Auth creates JWT token
3. JWT token stored in cookies
4. For API calls, include JWT in Authorization header

### Backend (FastAPI)
1. Verify JWT token using shared secret
2. Extract user information from token
3. Filter data by authenticated user ID
4. Return only user's data

## Environment Variables Setup

### Frontend (Next.js)
```bash
# .env.local
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (FastAPI)
```bash
# .env
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret-key  # Same as frontend
```

## Next.js Configuration

Use `next.config.ts` for TypeScript projects:

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

## Type Generation

## Project Setup Commands

- Create new Next.js 16 app: `npx create-next-app@latest frontend`
  - Creates app with TypeScript, ESLint, Tailwind CSS, and App Router pre-configured
- For existing projects: `npm install next@latest react@latest react-dom@latest`
- Development server: `npm run dev`
- Production build: `npm run build`
- Start production server: `npm run start`

## Type Generation

Run `npx next typegen` to generate route-aware type helpers:
- `PageProps<'/path'>` for page components
- `LayoutProps<'/path'>` for layout components
- Provides full type safety for route parameters