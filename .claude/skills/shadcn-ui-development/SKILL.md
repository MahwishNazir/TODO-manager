---
name: shadcn-ui-development
description: Comprehensive guide for using shadcn/ui with Next.js 16 and TypeScript for the Todo application Phase 2. Includes installation, configuration, and component usage patterns.
---

# shadcn/ui Development Guide for Next.js 16

## Instructions

Use this skill when implementing UI components for the Todo application in Phase 2 using shadcn/ui with Next.js 16 and TypeScript. Follow these guidelines for proper implementation:

### 1. Initial Setup and Installation
- Initialize shadcn/ui in your Next.js 16 project with: `npx shadcn@latest init`
  - This creates `components.json` configuration file
  - Sets up the components directory and base styles
  - Configures aliases for imports
- Install specific components using: `npx shadcn@latest add @shadcn/component-name`
- For basic Todo app components, install: `npx shadcn@latest add @shadcn/button @shadcn/input @shadcn/label @shadcn/card @shadcn/form @shadcn/checkbox @shadcn/dialog @shadcn/sheet @shadcn/sonner`

### 2. Configuration (components.json)
- The `components.json` file manages shadcn/ui configuration
- Defines import aliases, base paths, and style preferences
- Default configuration creates components in `@/components/ui/` directory
- Uses Tailwind CSS for styling with CSS variables for theming

### 3. Component Usage Patterns for Todo App
- **Task Form**: Use `@shadcn/card`, `@shadcn/input`, `@shadcn/button`, `@shadcn/form` for task creation/editing
- **Task List**: Use `@shadcn/card` with custom layouts for displaying tasks
- **Task Actions**: Use `@shadcn/button`, `@shadcn/checkbox`, `@shadcn/dialog` for task interactions
- **Notifications**: Use `@shadcn/sonner` for toast notifications
- **Responsive Layout**: Use `@shadcn/sheet` for mobile-friendly side panels

### 4. Form Implementation with Validation
- Use React Hook Form or TanStack Form with Zod for validation
- Implement proper error handling and user feedback
- Include character counters and field descriptions where appropriate
- Use proper labeling and accessibility attributes

### 5. Styling and Theming

#### CSS Variables for Dual-Theme Colors
Define custom colors in `app/globals.css` for light/dark mode. Use the site's dual-theme color system:

**Light Mode (LinkedIn Wrapped Style):**
```css
:root {
  --background: 255 255 255;        /* #FFFFFF */
  --foreground: 31 41 55;            /* #1F2937 */
  --card: 255 255 255;
  --card-foreground: 31 41 55;
  --primary: 124 58 237;            /* #7C3AED - Deep Purple */
  --primary-foreground: 255 255 255;
  --secondary: 196 181 253;         /* #C4B5FD - Light Lavender */
  --secondary-foreground: 124 58 237;
  --muted: 243 244 246;
  --muted-foreground: 107 114 128;
  --accent: 196 181 253;
  --accent-foreground: 124 58 237;
  --destructive: 239 68 68;
  --destructive-foreground: 255 255 255;
  --border: 229 231 235;
  --input: 229 231 235;
  --ring: 124 58 237;
  --radius: 0.75rem;
}
```

**Dark Mode (Regulatis AI Dashboard Style):**
```css
.dark {
  --background: 10 10 31;           /* #0A0A1F - Dark Blue-Black */
  --foreground: 255 255 255;
  --card: 20 20 40;
  --card-foreground: 255 255 255;
  --primary: 168 85 247;            /* #A855F7 - Purple */
  --primary-foreground: 255 255 255;
  --secondary: 196 181 253;         /* #C4B5FD - Lavender */
  --secondary-foreground: 10 10 31;
  --muted: 30 30 60;
  --muted-foreground: 163 163 163;
  --accent: 168 85 247;
  --accent-foreground: 255 255 255;
  --destructive: 239 68 68;
  --destructive-foreground: 255 255 255;
  --border: 168 85 247 20;         /* Semi-transparent purple */
  --input: 30 30 60;
  --ring: 168 85 247;
}
```

#### Hover Effects and Transitions
Add hover effects to shadcn components using Tailwind utility classes:

**Button Hover Effects:**
```tsx
<Button className="hover:scale-105 transition-transform duration-200 hover:shadow-lg hover:shadow-purple-500/25">
  Hover Me
</Button>
```

**Card Hover with Scale and Shadow:**
```tsx
<Card className="hover:scale-[1.02] transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/20 backdrop-blur-xl bg-white/5 dark:bg-gray-900/50">
  <CardContent>Card Content</CardContent>
</Card>
```

**Interactive Button with Multiple States:**
```tsx
<Button className="
  bg-primary hover:bg-primary/90
  active:scale-95
  transition-all duration-200
  hover:shadow-lg hover:shadow-primary/50
  focus:ring-2 focus:ring-primary focus:ring-offset-2
">
  Interactive Button
</Button>
```

#### Glassmorphism Effects
Apply glassmorphic styling to components:

```tsx
<Card className="
  bg-white/10 dark:bg-white/5
  backdrop-blur-xl
  border border-white/20 dark:border-white/10
  shadow-lg
">
  Glassmorphic Card
</Card>
```

#### Gradient Text and Borders
```tsx
<h1 className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
  Gradient Text
</h1>

<div className="border border-gradient-to-r from-purple-500 to-pink-500">
  Gradient Border
</div>
```

#### Animations
Add animations using Tailwind:

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
  className="animate-pulse"
>
  Animated Content
</motion.div>
```

**Fade-in animation:**
```tsx
<div className="animate-in fade-in duration-500">
  Fades in on mount
</div>
```

**Slide-in animation:**
```tsx
<div className="animate-in slide-in-from-bottom duration-500">
  Slides up from bottom
</div>
```

#### Custom Component Variants
Extend shadcn components with custom variants:

```tsx
// Create custom button variant in globals.css
@layer components {
  .btn-glass {
    @apply px-4 py-2 rounded-lg
           bg-white/10 dark:bg-white/5
           backdrop-blur-xl
           border border-white/20
           hover:bg-white/20 hover:scale-105
           transition-all duration-200;
  }
}

// Use in component
<Button className="btn-glass">Glass Button</Button>
```

### 6. Accessibility
- All components follow WAI-ARIA best practices
- Proper semantic HTML structure
- Keyboard navigation support
- Screen reader compatibility

### 7. TypeScript Integration
- Components are fully typed with TypeScript
- Form schemas provide type safety
- Proper prop validation and typing

### 8. Additional UI Components for Todo App
- **Skeleton**: Loading states for better UX while data loads
- **Spinner**: Visual feedback during async operations
- **Sidebar**: Navigation menu for app sections
- **Alert/AlertDialog**: Notifications and confirmation dialogs
- **Avatar**: User profile pictures and initials
- **Calendar/DatePicker**: Date selection for due dates
- **Tooltip**: Hover information for UI elements
- **Theme Toggle**: Dark/light mode switching

### 9. Using shadcn MCP Tools
- **Search for components**: `mcp__shadcn__search_items_in_registries` with registries ["@shadcn"] and query for specific component names
- **Get component examples**: `mcp__shadcn__get_item_examples_from_registries` to see real usage examples
- **Get add commands**: `mcp__shadcn__get_add_command_for_items` to get the exact command to install components
- **View component details**: `mcp__shadcn__view_items_in_registries` for component information
- **Get project registries**: `mcp__shadcn__get_project_registries` to see configured registries in current project

## Examples

### Example 1: Task Creation Form
```tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Field,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

const taskFormSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(100, "Title must be less than 100 characters"),
  description: z
    .string()
    .max(500, "Description must be less than 500 characters")
    .optional()
    .nullable(),
})

type TaskFormValues = z.infer<typeof taskFormSchema>

export default function TaskForm() {
  const form = useForm<TaskFormValues>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: {
      title: "",
      description: "",
    },
  })

  function onSubmit(data: TaskFormValues) {
    // Handle task creation
    console.log(data)
    toast.success("Task created successfully!")
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Create New Task</CardTitle>
        <CardDescription>Add a new task to your list</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="title">Title</FieldLabel>
              <Input
                {...form.register("title")}
                id="title"
                placeholder="Task title"
              />
              {form.formState.errors.title && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.title.message}
                </p>
              )}
            </Field>
            <Field>
              <FieldLabel htmlFor="description">Description</FieldLabel>
              <Textarea
                {...form.register("description")}
                id="description"
                placeholder="Task description (optional)"
                rows={3}
              />
              {form.formState.errors.description && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.description.message}
                </p>
              )}
            </Field>
          </FieldGroup>
        </form>
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => form.reset()}>
          Reset
        </Button>
        <Button
          type="submit"
          onClick={form.handleSubmit(onSubmit)}
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? "Creating..." : "Create Task"}
        </Button>
      </CardFooter>
    </Card>
  )
}
```

### Example 2: Task List Item with Actions
```tsx
"use client"

import { useState } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"

interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
}

export default function TaskItem({ task }: { task: Task }) {
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(task.title)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const handleUpdate = () => {
    // Handle task update
    toast.success("Task updated successfully!")
    setIsEditing(false)
  }

  const handleDelete = () => {
    // Handle task deletion
    toast.success("Task deleted successfully!")
    setShowDeleteDialog(false)
  }

  return (
    <Card className="mb-3">
      <CardContent className="p-4 flex items-start gap-4">
        <Checkbox
          id={`task-${task.id}`}
          checked={task.completed}
          onCheckedChange={() => toast.info("Task status updated")}
          className="mt-1"
        />
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <div className="space-y-3">
              <Input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="font-medium"
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleUpdate}
                >
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false)
                    setEditTitle(task.title)
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div>
              <label
                htmlFor={`task-${task.id}`}
                className={`font-medium ${task.completed ? 'line-through text-muted-foreground' : ''}`}
              >
                {task.title}
              </label>
              {task.description && (
                <p className="text-sm text-muted-foreground mt-1">
                  {task.description}
                </p>
              )}
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? "Cancel" : "Edit"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowDeleteDialog(true)}
          >
            Delete
          </Button>
        </div>
      </CardContent>

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Deletion</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{task.title}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
```

### Example 3: Toast Notifications
```tsx
"use client"

import { Button } from "@/components/ui/button"
import { toast } from "sonner"

export default function NotificationDemo() {
  return (
    <div className="flex flex-col gap-2">
      <Button
        variant="outline"
        onClick={() => toast.success("Task completed successfully!")}
      >
        Success Toast
      </Button>
      <Button
        variant="outline"
        onClick={() => toast.error("Failed to create task")}
      >
        Error Toast
      </Button>
      <Button
        variant="outline"
        onClick={() => toast.info("Task list refreshed")}
      >
        Info Toast
      </Button>
    </div>
  )
}
```

## Best Practices

- Always initialize shadcn/ui with `npx shadcn@latest init` in new projects
- Use the component library for consistent UI patterns
- Follow accessibility best practices
- Implement proper form validation with Zod
- Use toast notifications for user feedback
- Keep custom styling minimal and consistent with the design system
- Use TypeScript for all components to ensure type safety
- Test components across different screen sizes for responsive design