# Next.js 16 Examples for Todo App

## Basic Page with Data Fetching

### Server Component with Async Params (Next.js 16 Required)
```tsx
// app/tasks/[id]/page.tsx
import { getTask } from '@/lib/api/tasks'

export default async function TaskPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params  // Critical: await in Next.js 16!
  const task = await getTask(id)

  if (!task) {
    return <div>Task not found</div>
  }

  return (
    <div>
      <h1>{task.title}</h1>
      <p>{task.description}</p>
      <p>Status: {task.completed ? 'Completed' : 'Pending'}</p>
    </div>
  )
}
```

## Client Component with Server Action

### Task Creation Form
```tsx
// components/tasks/TaskForm.tsx
'use client'

import { useState } from 'react'
import { createTask } from '@/actions/tasks'

export default function TaskForm() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = async (formData: FormData) => {
    formData.set('title', title)
    formData.set('description', description)
    await createTask(formData)
    setTitle('')
    setDescription('')
  }

  return (
    <form action={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
        required
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />
      <button type="submit">Add Task</button>
    </form>
  )
}
```

## Layout with Navigation

### Dashboard Layout
```tsx
// app/dashboard/layout.tsx
import { auth } from '@/lib/auth/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth()
  if (!session) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-xl font-bold">
                Todo App
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/dashboard/tasks">Tasks</Link>
              <Link href="/dashboard/profile">Profile</Link>
              <form action="/api/auth/signout" method="post">
                <button type="submit" className="text-red-600">
                  Sign Out
                </button>
              </form>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}
```

## Server Action with Cache Invalidation

### Task Update Server Action
```ts
// actions/tasks.ts
'use server'

import { revalidateTag, updateTag } from 'next/cache'
import { cookies } from 'next/headers'

export async function updateTask(formData: FormData) {
  const id = formData.get('id') as string
  const title = formData.get('title') as string
  const description = formData.get('description') as string
  const completed = formData.get('completed') === 'on'

  // Update task in database
  const updatedTask = await db.tasks.update({
    where: { id },
    data: { title, description, completed }
  })

  // Update cache to reflect changes immediately
  updateTag(`task-${id}`)
  updateTag('user-tasks')

  return updatedTask
}
```

## Error Boundary Component

### Global Error Component
```tsx
// app/error.tsx
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-red-50">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-red-600">Something went wrong!</h2>
        <p className="text-red-500 mb-4">{error.message}</p>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
```

## Loading Component

### Global Loading Component
```tsx
// app/loading.tsx
export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
    </div>
  )
}
```

## API Route Example

### Task API Route
```ts
// app/api/tasks/route.ts
import { cookies } from 'next/headers'
import { verifyAuth } from '@/lib/auth/server'

export async function GET(request: Request) {
  try {
    // Verify authentication
    const token = cookies().get('better-auth_session_token')?.value
    if (!token) {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const user = await verifyAuth(token)
    if (!user) {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user's tasks from database
    const tasks = await db.tasks.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'desc' }
    })

    return Response.json(tasks)
  } catch (error) {
    console.error('Error fetching tasks:', error)
    return Response.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    // Verify authentication
    const token = cookies().get('better-auth_session_token')?.value
    if (!token) {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const user = await verifyAuth(token)
    if (!user) {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Parse request body
    const body = await request.json()
    const { title, description } = body

    // Validate input
    if (!title || title.trim().length === 0) {
      return Response.json({ error: 'Title is required' }, { status: 400 })
    }

    // Create task in database
    const task = await db.tasks.create({
      data: {
        title: title.trim(),
        description: description?.trim() || '',
        userId: user.id
      }
    })

    return Response.json(task, { status: 201 })
  } catch (error) {
    console.error('Error creating task:', error)
    return Response.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

## Authentication Integration Example

### Login Page
```tsx
// app/login/page.tsx
'use client'

import { signIn } from 'better-auth/client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const result = await signIn.email({
        email,
        password,
        callbackURL: '/dashboard'
      })

      if (result.error) {
        setError(result.error.message)
      } else {
        router.push('/dashboard')
      }
    } catch (err) {
      setError('An error occurred during login')
      console.error(err)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                type="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <input
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
```