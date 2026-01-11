# shadcn/ui Examples for Todo App

## Task Form with Validation

### Complete Task Creation Form
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
  priority: z.enum(["low", "medium", "high"]).default("medium"),
})

type TaskFormValues = z.infer<typeof taskFormSchema>

export default function TaskForm() {
  const form = useForm<TaskFormValues>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: {
      title: "",
      description: "",
      priority: "medium",
    },
  })

  function onSubmit(data: TaskFormValues) {
    console.log(data)
    toast.success("Task created successfully!")
    form.reset()
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
              <FieldLabel htmlFor="title">Title *</FieldLabel>
              <Input
                {...form.register("title")}
                id="title"
                placeholder="Task title"
                className={form.formState.errors.title ? "border-destructive" : ""}
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
                className={form.formState.errors.description ? "border-destructive" : ""}
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
        <Button
          variant="outline"
          type="button"
          onClick={() => form.reset()}
        >
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

## Task List Component

### Task List with Filtering
```tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"

interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
  createdAt: Date
}

export default function TaskList({ tasks }: { tasks: Task[] }) {
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all")
  const [search, setSearch] = useState("")

  const filteredTasks = tasks.filter(task => {
    const matchesFilter =
      filter === "all" ||
      (filter === "active" && !task.completed) ||
      (filter === "completed" && task.completed)

    const matchesSearch =
      task.title.toLowerCase().includes(search.toLowerCase()) ||
      (task.description?.toLowerCase().includes(search.toLowerCase()) ?? false)

    return matchesFilter && matchesSearch
  })

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <Input
          placeholder="Search tasks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <Button
          variant={filter === "all" ? "default" : "outline"}
          onClick={() => setFilter("all")}
        >
          All
        </Button>
        <Button
          variant={filter === "active" ? "default" : "outline"}
          onClick={() => setFilter("active")}
        >
          Active
        </Button>
        <Button
          variant={filter === "completed" ? "default" : "outline"}
          onClick={() => setFilter("completed")}
        >
          Completed
        </Button>
      </div>

      <div className="space-y-3">
        {filteredTasks.map((task) => (
          <TaskItem key={task.id} task={task} />
        ))}

        {filteredTasks.length === 0 && (
          <Card className="p-8 text-center text-muted-foreground">
            No tasks found
          </Card>
        )}
      </div>
    </div>
  )
}

function TaskItem({ task }: { task: Task }) {
  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        <Checkbox
          id={`task-${task.id}`}
          checked={task.completed}
          className="mt-0.5"
        />
        <div className="flex-1 min-w-0">
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
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Edit
          </Button>
          <Button variant="outline" size="sm">
            Delete
          </Button>
        </div>
      </div>
    </Card>
  )
}
```

## Confirmation Dialog

### Delete Task Confirmation
```tsx
"use client"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { toast } from "sonner"

interface DeleteTaskDialogProps {
  taskId: string
  taskTitle: string
  onConfirm: () => void
}

export default function DeleteTaskDialog({
  taskId,
  taskTitle,
  onConfirm
}: DeleteTaskDialogProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="destructive" size="sm">
          Delete
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirm Deletion</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete "{taskTitle}"? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => toast.info("Deletion cancelled")}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={() => {
              onConfirm()
              toast.success("Task deleted successfully!")
            }}
          >
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

## Responsive Layout with Sheet

### Mobile-Friendly Task Editor
```tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"

interface Task {
  id: string
  title: string
  description?: string
}

export default function TaskEditor({ task }: { task: Task }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description || "")

  const handleSave = () => {
    // Handle task update
    console.log({ id: task.id, title, description })
    setOpen(false)
  }

  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        Edit
      </Button>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Edit Task</SheetTitle>
            <SheetDescription>
              Make changes to your task here. Click save when you're done.
            </SheetDescription>
          </SheetHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label htmlFor="title" className="text-sm font-medium">
                Title
              </label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <label htmlFor="description" className="text-sm font-medium">
                Description
              </label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={6}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              className="flex-1"
            >
              Save
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </>
  )
}
```

## Toast Notifications

### Notification System
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
        Success
      </Button>
      <Button
        variant="outline"
        onClick={() => toast.error("Failed to create task")}
      >
        Error
      </Button>
      <Button
        variant="outline"
        onClick={() => toast.info("Task list refreshed")}
      >
        Info
      </Button>
      <Button
        variant="outline"
        onClick={() => toast.warning("Task is due soon")}
      >
        Warning
      </Button>
      <Button
        variant="outline"
        onClick={() => {
          toast.promise(
            new Promise((resolve) => setTimeout(resolve, 2000)),
            {
              loading: "Creating task...",
              success: "Task created successfully!",
              error: "Failed to create task",
            }
          )
        }}
      >
        Promise
      </Button>
    </div>
  )
}
```

## Priority Badge Component

### Task Priority Indicator
```tsx
import { Badge } from "@/components/ui/badge"

interface PriorityBadgeProps {
  priority: "low" | "medium" | "high"
}

export default function PriorityBadge({ priority }: PriorityBadgeProps) {
  const priorityConfig = {
    low: { text: "Low", className: "bg-green-100 text-green-800" },
    medium: { text: "Medium", className: "bg-yellow-100 text-yellow-800" },
    high: { text: "High", className: "bg-red-100 text-red-800" },
  }

  const config = priorityConfig[priority]

  return (
    <Badge variant="secondary" className={config.className}>
      {config.text}
    </Badge>
  )
}
```

## Loading and Skeleton Components

### Task List Loading Skeleton
```tsx
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export default function TaskListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, index) => (
        <Card key={index} className="p-4">
          <div className="flex items-center gap-3">
            <Skeleton className="h-5 w-5 rounded-sm" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
            <Skeleton className="h-8 w-16 rounded-md" />
          </div>
        </Card>
      ))}
    </div>
  )
}
```

### Loading Spinner
```tsx
import { Item, ItemContent, ItemMedia, ItemTitle } from "@/components/ui/item"
import { Spinner } from "@/components/ui/spinner"

export default function ProcessingItem() {
  return (
    <Item variant="muted">
      <ItemMedia>
        <Spinner />
      </ItemMedia>
      <ItemContent>
        <ItemTitle className="line-clamp-1">Processing task...</ItemTitle>
      </ItemContent>
    </Item>
  )
}
```

## Sidebar Navigation

### Todo App Sidebar
```tsx
"use client"

import { HomeIcon, CalendarIcon, SettingsIcon, UserIcon } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

const items = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: HomeIcon,
  },
  {
    title: "Tasks",
    url: "/tasks",
    icon: CalendarIcon,
  },
  {
    title: "Profile",
    url: "/profile",
    icon: UserIcon,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: SettingsIcon,
  },
]

export default function TodoSidebar() {
  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Navigation</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {items.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild>
                      <a href={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
      <div className="flex-1">
        <header className="flex h-12 items-center gap-2 px-4">
          <SidebarTrigger />
        </header>
        <main className="p-4">
          {/* Your main content goes here */}
        </main>
      </div>
    </SidebarProvider>
  )
}
```

## Alert and Confirmation Components

### Task Action Alerts
```tsx
import { AlertCircle, CheckCircle2, AlertTriangle } from "lucide-react"
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"

// Success Alert
export function TaskSuccessAlert() {
  return (
    <Alert>
      <CheckCircle2 />
      <AlertTitle>Success! Task updated</AlertTitle>
      <AlertDescription>
        Your task has been updated successfully.
      </AlertDescription>
    </Alert>
  )
}

// Warning Alert
export function TaskWarningAlert() {
  return (
    <Alert variant="destructive">
      <AlertTriangle />
      <AlertTitle>Task due soon</AlertTitle>
      <AlertDescription>
        This task is due within 24 hours.
      </AlertDescription>
    </Alert>
  )
}

// Error Alert
export function TaskErrorAlert() {
  return (
    <Alert variant="destructive">
      <AlertCircle />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>
        Failed to update task. Please try again.
      </AlertDescription>
    </Alert>
  )
}
```

### Alert Dialog for Critical Actions
```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"

interface DeleteTaskDialogProps {
  onConfirm: () => void
  taskTitle: string
}

export default function DeleteTaskDialog({ onConfirm, taskTitle }: DeleteTaskDialogProps) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete Task</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. This will permanently delete the task "{taskTitle}"
            and remove it from your list.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

## User Profile Components

### User Avatar
```tsx
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"

interface UserAvatarProps {
  user: {
    name: string
    avatar?: string
  }
}

export default function UserAvatar({ user }: UserAvatarProps) {
  return (
    <Avatar>
      {user.avatar && <AvatarImage src={user.avatar} alt={user.name} />}
      <AvatarFallback>
        {user.name
          .split(" ")
          .map((n) => n[0])
          .join("")
          .toUpperCase()}
      </AvatarFallback>
    </Avatar>
  )
}
```

## Date and Time Components

### Task Due Date Picker
```tsx
"use client"

import * as React from "react"
import { format } from "date-fns"

import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { CalendarIcon } from "lucide-react"

interface DatePickerProps {
  date: Date | undefined
  setDate: (date: Date | undefined) => void
}

export default function DatePicker({ date, setDate }: DatePickerProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className="w-full justify-start text-left font-normal"
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, "PPP") : <span>Pick a date</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar
          mode="single"
          selected={date}
          onSelect={setDate}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  )
}
```

## Tooltip Components

### Task Status Tooltip
```tsx
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface TaskStatusTooltipProps {
  status: "pending" | "in-progress" | "completed"
  children: React.ReactNode
}

export default function TaskStatusTooltip({ status, children }: TaskStatusTooltipProps) {
  const statusText = {
    "pending": "Task is pending",
    "in-progress": "Task is in progress",
    "completed": "Task is completed"
  }[status]

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        {children}
      </TooltipTrigger>
      <TooltipContent>
        <p>{statusText}</p>
      </TooltipContent>
    </Tooltip>
  )
}
```

## Theme Toggle (Dark/Light Mode)

### Theme Toggle Component
```tsx
"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```