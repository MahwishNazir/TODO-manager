---
name: tailwindcss-styling
description: Comprehensive guide for using Tailwind CSS with Next.js 16 for the Todo application Phase 2. Includes installation, configuration, responsive design patterns, and integration with shadcn/ui components.
---

# Tailwind CSS Styling Guide for Next.js 16

## Instructions

Use this skill when implementing styling for the Todo application in Phase 2 using Tailwind CSS with Next.js 16. Follow these guidelines for proper implementation:

### 1. Initial Setup and Installation (Next.js 16 + Tailwind CSS)
- Initialize Tailwind CSS in your Next.js 16 project with: `npx create-next-app@latest frontend` (includes Tailwind CSS setup)
- For existing projects: `npm install -D tailwindcss postcss autoprefixer` then `npx tailwindcss init -p`
- Configure `tailwind.config.ts` for Next.js 16 with proper content paths:
```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Add custom theme extensions here
    },
  },
  plugins: [],
}
export default config
```
- Import Tailwind CSS in your root layout: `@import 'tailwindcss/base'; @import 'tailwindcss/components'; @import 'tailwindcss/utilities';` in `app/globals.css`

### 2. Configuration and Customization (tailwind.config.ts)
- Use CSS variables for theming to work with dark mode
- Extend theme for project-specific colors, spacing, and typography
- Configure safelist for dynamic class generation
- Set up dark mode strategy (class or media)

### 3. Responsive Design Patterns (Mobile-First Approach)
- Use responsive prefixes: `sm:`, `md:`, `lg:`, `xl:`, `2xl:`
- Implement mobile-first design with `max-w-sm`, `flex-col`, `gap-2` on small screens
- Scale up with `md:flex-row`, `lg:gap-4`, `xl:max-w-md` for larger screens
- Use `container` class with proper padding for responsive layouts

### 4. Integration with shadcn/ui Components
- All shadcn/ui components use Tailwind CSS utility classes internally
- Customize component styles by extending existing classes
- Use CSS variables defined in `:root` for consistent theming
- Leverage dark mode classes (e.g., `dark:bg-muted`) for theme consistency

### 5. Typography and Spacing Standards
- Use consistent spacing scale: `space-y-4`, `p-4`, `gap-4`
- Apply typography hierarchy: `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`
- Maintain vertical rhythm with consistent padding/margin
- Use `leading-tight`, `leading-normal`, `leading-relaxed` for line heights

### 6. Color Palette and Theming
- Primary: `blue-600`, `blue-500` for interactive elements
- Secondary: `gray-600`, `gray-500` for supporting elements
- Success: `green-600`, `green-500` for positive actions
- Warning: `yellow-500`, `yellow-400` for warnings
- Destructive: `red-600`, `red-500` for errors/deletions
- Muted: `gray-400`, `gray-300` for disabled/inactive elements
- Use `text-primary`, `bg-primary`, `border-primary` for consistent application

### 7. Utility-First Development
- Build components using utility classes rather than custom CSS
- Use `@apply` directive in CSS files sparingly (only for reusable component patterns)
- Leverage Tailwind's arbitrary values: `w-[200px]`, `text-[24px]`
- Use arbitrary modifiers: `bg-red-500/50` for opacity

### 8. Performance Optimization
- Enable Tailwind's purge/optimization in production builds
- Use `content` configuration to include only used classes
- Leverage `safelist` for dynamically generated classes
- Remove unused CSS with proper content configuration

### 9. Dark Mode Implementation
- Configure dark mode in `tailwind.config.ts`: `darkMode: 'class'`
- Use `dark:` prefix for dark theme variants: `dark:bg-gray-800`
- Implement theme toggle component with JavaScript
- Ensure proper contrast ratios in both light and dark modes

### 10. Animation and Transitions
- Use Tailwind's built-in transition utilities: `transition`, `duration-200`, `ease-in-out`
- Apply hover, focus, and active states: `hover:bg-primary`, `focus:ring-2`
- Use `transform` classes for subtle animations: `scale-105`, `rotate-1`
- Implement loading states with animation utilities

### 11. Accessibility Considerations
- Ensure sufficient color contrast (4.5:1 for normal text, 3:1 for large text)
- Use focus utilities: `focus:outline-none`, `focus:ring-2`, `focus:ring-primary`
- Maintain semantic HTML structure with Tailwind classes
- Test color combinations in both light and dark modes

### 12. Integration with Next.js 16 Features
- Use Tailwind with Server Components for styling server-rendered content
- Apply Tailwind classes conditionally in Client Components
- Leverage Tailwind's JIT compiler for dynamic class generation
- Use Tailwind with Next.js Image component for styling

### 13. Using Tailwind CSS MCP Tools
- **Get Tailwind utilities**: `mcp__tailwindcss-mcp-server__get_tailwind_utilities` to search for specific utility classes
- **Get color palettes**: `mcp__tailwindcss-mcp-server__get_tailwind_colors` to explore Tailwind's color system
- **Search documentation**: `mcp__tailwindcss-mcp-server__search_tailwind_docs` to find specific Tailwind features
- **Convert CSS to Tailwind**: `mcp__tailwindcss-mcp-server__convert_css_to_tailwind` to convert traditional CSS
- **Generate color palettes**: `mcp__tailwindcss-mcp-server__generate_color_palette` to create custom colors
- **Install Tailwind**: `mcp__tailwindcss-mcp-server__install_tailwind` for setup commands

## Examples

### Example 1: Responsive Todo List Layout
```tsx
// app/tasks/page.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { PlusIcon } from 'lucide-react'

export default function TasksPage() {
  return (
    <div className="container mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Tasks</h1>
          <p className="text-muted-foreground mt-2">
            Manage your todo list efficiently
          </p>
        </div>
        <Button className="w-full sm:w-auto">
          <PlusIcon className="mr-2 h-4 w-4" />
          Add Task
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Task cards will be mapped here */}
        <Card className="overflow-hidden">
          <CardHeader className="pb-3">
            <CardTitle className="text-xl">Sample Task</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              This is a sample task description
            </p>
            <div className="flex justify-between items-center">
              <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
                Pending
              </span>
              <Button variant="outline" size="sm">
                View
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

### Example 2: Dark Mode Toggle Component
```tsx
// components/ui/theme-toggle.tsx
'use client'

import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'

import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="rounded-full"
      aria-label="Toggle theme"
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  )
}
```

### Example 3: Responsive Task Form with Validation States
```tsx
// components/task-form.tsx
'use client'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { useState } from 'react'

export default function TaskForm() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [errors, setErrors] = useState<{title?: string, description?: string}>({})

  const validate = () => {
    const newErrors: {title?: string, description?: string} = {}
    if (!title.trim()) {
      newErrors.title = 'Title is required'
    } else if (title.length > 100) {
      newErrors.title = 'Title must be less than 100 characters'
    }

    if (description && description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validate()) {
      // Handle form submission
      console.log({ title, description })
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg">
      <CardHeader className="pb-3">
        <CardTitle className="text-2xl font-bold">Create New Task</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title" className="text-base">Task Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter task title"
              className={`w-full ${errors.title ? 'border-red-500' : ''}`}
            />
            {errors.title && (
              <p className="text-red-500 text-sm mt-1">{errors.title}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description" className="text-base">Description (Optional)</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter task description"
              rows={4}
              className={`${errors.description ? 'border-red-500' : ''}`}
            />
            {errors.description && (
              <p className="text-red-500 text-sm mt-1">{errors.description}</p>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex flex-col sm:flex-row justify-end gap-3 pt-6 border-t">
          <Button
            type="button"
            variant="outline"
            className="w-full sm:w-auto"
            onClick={() => {
              setTitle('')
              setDescription('')
              setErrors({})
            }}
          >
            Reset
          </Button>
          <Button
            type="submit"
            className="w-full sm:w-auto bg-primary hover:bg-primary/90"
          >
            Create Task
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}
```

### Example 4: Responsive Dashboard Layout
```tsx
// app/dashboard/page.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  CalendarIcon,
  CheckCircleIcon,
  CircleIcon,
  PlusIcon
} from 'lucide-react'

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
              <CheckCircleIcon className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-xl font-bold">Todo App</h1>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <a href="/tasks" className="transition-colors hover:text-primary">Tasks</a>
            <a href="/dashboard" className="text-primary font-semibold">Dashboard</a>
            <a href="/settings" className="transition-colors hover:text-primary">Settings</a>
          </nav>
          <Button variant="outline" size="sm">
            <PlusIcon className="mr-2 h-4 w-4" />
            New Task
          </Button>
        </div>
      </header>

      <main className="container py-8 px-4 sm:px-6">
        <div className="mb-8">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground mt-2">
            Overview of your tasks and productivity
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
              <div className="rounded-full bg-blue-500/10 p-2">
                <CheckCircleIcon className="h-4 w-4 text-blue-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">+3 from last week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <div className="rounded-full bg-green-500/10 p-2">
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">18</div>
              <p className="text-xs text-muted-foreground">75% completion</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <div className="rounded-full bg-yellow-500/10 p-2">
                <CircleIcon className="h-4 w-4 text-yellow-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">6</div>
              <p className="text-xs text-muted-foreground">25% remaining</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Due Today</CardTitle>
              <div className="rounded-full bg-red-500/10 p-2">
                <CalendarIcon className="h-4 w-4 text-red-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">Due in next 24 hours</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Recent Tasks</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-4">
                <li className="flex items-center justify-between">
                  <span>Complete project proposal</span>
                  <span className="text-sm text-muted-foreground">Today</span>
                </li>
                <li className="flex items-center justify-between">
                  <span>Review team feedback</span>
                  <span className="text-sm text-muted-foreground">Tomorrow</span>
                </li>
                <li className="flex items-center justify-between">
                  <span>Prepare presentation</span>
                  <span className="text-sm text-muted-foreground">Dec 15</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Productivity Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted rounded-lg">
                <p className="text-muted-foreground">Chart placeholder</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
```

### Example 5: Responsive Mobile Menu
```tsx
// components/ui/mobile-menu.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Menu, X } from 'lucide-react'

export default function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="md:hidden">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className="rounded-md"
        aria-label="Toggle menu"
      >
        {isOpen ? (
          <X className="h-5 w-5" />
        ) : (
          <Menu className="h-5 w-5" />
        )}
      </Button>

      {isOpen && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm md:hidden">
          <div className="absolute inset-y-0 right-0 w-4/5 bg-background p-6 shadow-lg">
            <div className="flex flex-col h-full">
              <div className="flex justify-end mb-8">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="rounded-md"
                  aria-label="Close menu"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <nav className="flex flex-col space-y-4 flex-1">
                <a
                  href="/tasks"
                  className="text-lg font-medium hover:text-primary transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Tasks
                </a>
                <a
                  href="/dashboard"
                  className="text-lg font-medium hover:text-primary transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Dashboard
                </a>
                <a
                  href="/settings"
                  className="text-lg font-medium hover:text-primary transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Settings
                </a>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

## Best Practices

- Use Tailwind's official class naming conventions consistently
- Leverage the `container` class for responsive layouts with proper max-width
- Implement consistent spacing using Tailwind's spacing scale (0, 1, 2, 3, 4, 6, 8, etc.)
- Use semantic HTML elements with Tailwind classes for accessibility
- Maintain a consistent color palette throughout the application
- Implement responsive design from mobile-first perspective
- Use Tailwind's arbitrary values feature for custom requirements when needed
- Test layouts across different screen sizes and devices
- Use Tailwind's dark mode classes for theme consistency
- Follow accessibility guidelines when applying styles
- Keep custom CSS to a minimum, preferring Tailwind utilities
- Use CSS variables defined in Tailwind config for consistent theming
- Implement proper focus states for keyboard navigation
- Use Tailwind's JIT compiler for dynamic class generation
- Leverage Tailwind's responsive prefixes for mobile-first design
- Use proper contrast ratios for text and background colors
- Implement consistent typography scales across the application