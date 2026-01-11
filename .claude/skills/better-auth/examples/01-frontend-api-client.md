# Frontend API Client Pattern - Better Auth JWT Integration

## Overview
Production-ready API client that automatically attaches JWT tokens from Better Auth sessions to all backend requests. Handles authentication state, token refresh, and error responses.

## Full Implementation

```typescript
/**
 * API Client with Automatic JWT Token Attachment
 *
 * Features:
 * - Automatic JWT token extraction from Better Auth session
 * - Type-safe request/response handling
 * - Centralized error handling with 401 redirect
 * - Query parameter building
 * - Consistent response types
 */

import type { APIRequestConfig, APIClientError } from '@/types/api'
import type { Task, TaskCreate, TaskUpdate } from '@/types/task'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Get JWT token from Better Auth session
 * CRITICAL: Better Auth stores session in cookies, we extract the token
 */
async function getSessionToken(): Promise<string | null> {
  try {
    const { getSession } = await import('@/lib/auth-client')
    const sessionData = await getSession()

    // Type-safe session data extraction
    if (sessionData && typeof sessionData === 'object' && 'data' in sessionData) {
      const data = sessionData.data
      if (data && typeof data === 'object' && 'session' in data) {
        const session = data.session as { token?: string } | null
        return session?.token || null
      }
    }

    return null
  } catch (error) {
    console.error('Failed to get session token:', error)
    return null
  }
}

/**
 * Build query string from parameters
 */
function buildQueryString(params?: Record<string, string | number | boolean | undefined>): string {
  if (!params) return ''

  const filtered = Object.entries(params).filter(([_, value]) => value !== undefined)
  if (filtered.length === 0) return ''

  const query = new URLSearchParams(
    filtered.map(([key, value]) => [key, String(value)])
  ).toString()

  return `?${query}`
}

/**
 * Generic fetch wrapper with automatic JWT token attachment
 */
async function apiRequest<T>(
  endpoint: string,
  config: APIRequestConfig = {}
): Promise<T> {
  const { method = 'GET', headers = {}, body, params } = config

  // Get JWT token from Better Auth session
  const token = await getSessionToken()

  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  }

  // Attach JWT token to Authorization header
  if (token) {
    requestHeaders['Authorization'] = `Bearer ${token}`
  }

  const queryString = buildQueryString(params)
  const url = `${API_BASE_URL}${endpoint}${queryString}`

  try {
    const response = await fetch(url, {
      method,
      headers: requestHeaders,
      body: body ? JSON.stringify(body) : undefined,
    })

    // Handle 401 Unauthorized - redirect to sign-in
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        window.location.href = '/sign-in'
      }
      throw new Error('Unauthorized - redirecting to sign-in')
    }

    const data = await response.json()

    // Handle non-2xx responses
    if (!response.ok) {
      const error: APIClientError = new Error(
        data.detail || data.message || 'API request failed'
      ) as APIClientError
      error.name = 'APIClientError'
      error.statusCode = response.status
      error.details = data
      throw error
    }

    return data as T
  } catch (error) {
    if ((error as APIClientError).name === 'APIClientError') {
      throw error
    }

    const networkError: APIClientError = new Error(
      'Network error - unable to reach server'
    ) as APIClientError
    networkError.name = 'APIClientError'
    networkError.details = error
    throw networkError
  }
}

/**
 * API Client with typed methods for task operations
 */
export const api = {
  async getTasks(userId: string, params?: { status?: string; limit?: number; offset?: number }): Promise<Task[]> {
    return apiRequest<Task[]>(`/api/${userId}/tasks`, { params })
  },

  async getTask(userId: string, taskId: number): Promise<Task> {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`)
  },

  async createTask(userId: string, data: TaskCreate): Promise<Task> {
    return apiRequest<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: data,
    })
  },

  async updateTask(userId: string, taskId: number, data: TaskUpdate): Promise<Task> {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: data,
    })
  },

  async deleteTask(userId: string, taskId: number): Promise<void> {
    return apiRequest<void>(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    })
  },

  async toggleTaskComplete(userId: string, taskId: number): Promise<Task> {
    return apiRequest<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    })
  },
}
```

## Type Definitions

```typescript
// types/api.ts
export interface APIRequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  headers?: Record<string, string>
  body?: unknown
  params?: Record<string, string | number | boolean | undefined>
}

export interface APIClientError extends Error {
  name: 'APIClientError'
  statusCode?: number
  details?: unknown
}

// types/task.ts
export interface Task {
  id: number
  user_id: string
  title: string
  description?: string
  completed: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
}
```

## Usage Examples

### 1. Fetch All Tasks
```typescript
'use client'

import { api } from '@/lib/api-client'
import { useEffect, useState } from 'react'

export function TaskList({ userId }: { userId: string }) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadTasks() {
      try {
        const data = await api.getTasks(userId, { status: 'pending' })
        setTasks(data)
      } catch (error) {
        console.error('Failed to load tasks:', error)
      } finally {
        setLoading(false)
      }
    }

    loadTasks()
  }, [userId])

  return <div>{/* Render tasks */}</div>
}
```

### 2. Create Task
```typescript
async function handleCreateTask(title: string, description?: string) {
  try {
    const newTask = await api.createTask(userId, { title, description })
    console.log('Task created:', newTask)
  } catch (error) {
    console.error('Failed to create task:', error)
  }
}
```

### 3. With Server Actions
```typescript
'use server'

import { api } from '@/lib/api-client'
import { revalidatePath } from 'next/cache'

export async function deleteTaskAction(userId: string, taskId: number) {
  try {
    await api.deleteTask(userId, taskId)
    revalidatePath('/dashboard')
    return { success: true }
  } catch (error) {
    return { success: false, error: 'Failed to delete task' }
  }
}
```

## Security Features

✅ **Automatic JWT Attachment**: No manual token management
✅ **Session Expiry Handling**: Redirects to sign-in on 401
✅ **Type Safety**: Full TypeScript types for requests/responses
✅ **Error Handling**: Centralized error management
✅ **HTTPS Ready**: Works with production environments

## Best Practices

1. **Always import from `@/lib/api-client`** - Never duplicate this logic
2. **Use Server Actions for mutations** - Leverage Next.js caching
3. **Handle errors gracefully** - Always wrap API calls in try-catch
4. **Revalidate paths** - Use `revalidatePath()` after mutations
5. **Type everything** - Use TypeScript interfaces for all data

## Common Pitfalls

❌ **Don't manually manage tokens** - Let the client handle it
❌ **Don't hardcode API URLs** - Use environment variables
❌ **Don't ignore 401 errors** - User needs to re-authenticate
❌ **Don't duplicate API logic** - Always use this client
