"use client";

import { TaskItem } from "./task-item";
import { EmptyState } from "./empty-state";
import { TaskListSkeleton } from "./task-skeleton";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw } from "lucide-react";
import type { TaskResponse } from "@/types/task";
import type { AsyncState } from "@/types/form";

interface TaskListProps {
  tasks: TaskResponse[];
  state: AsyncState;
  error: string | null;
  onRetry: () => void;
  onAddTask: () => void;
  onToggleComplete: (taskId: number) => Promise<void>;
  onEdit: (task: TaskResponse) => void;
  onDelete: (task: TaskResponse) => void;
  deletingTaskId?: number | null;
}

export function TaskList({
  tasks,
  state,
  error,
  onRetry,
  onAddTask,
  onToggleComplete,
  onEdit,
  onDelete,
  deletingTaskId,
}: TaskListProps) {
  if (state === "loading") {
    return <TaskListSkeleton />;
  }

  if (state === "error") {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center mb-6">
          <AlertCircle className="h-8 w-8 text-destructive" />
        </div>
        <h3 className="text-xl font-semibold mb-2">Failed to load tasks</h3>
        <p className="text-muted-foreground text-center mb-6 max-w-sm">
          {error || "Something went wrong. Please try again."}
        </p>
        <Button onClick={onRetry} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Try again
        </Button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return <EmptyState onAddTask={onAddTask} />;
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onEdit={onEdit}
          onDelete={onDelete}
          isDeleting={deletingTaskId === task.id}
        />
      ))}
    </div>
  );
}
