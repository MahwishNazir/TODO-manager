"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useTasks } from "@/hooks/use-tasks";
import { TaskList } from "@/components/tasks/task-list";
import { CreateTaskDialog } from "@/components/tasks/create-task-dialog";
import { EditTaskDialog } from "@/components/tasks/edit-task-dialog";
import { DeleteTaskDialog } from "@/components/tasks/delete-task-dialog";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import type { TaskResponse } from "@/types/task";

export default function TasksPage() {
  const { user } = useAuth();
  const { tasks, state, error, refetch, createTask, updateTask, toggleComplete, deleteTask } =
    useTasks(user?.id);

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskResponse | null>(null);
  const [deletingTask, setDeletingTask] = useState<TaskResponse | null>(null);
  const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null);

  const handleCreateTask = async (title: string) => {
    const result = await createTask(title);
    if (result) {
      setIsCreateDialogOpen(false);
    }
    return result;
  };

  const handleUpdateTask = async (taskId: number, title: string) => {
    const result = await updateTask(taskId, title);
    if (result) {
      setEditingTask(null);
    }
    return result;
  };

  const handleDeleteTask = async (taskId: number) => {
    // Trigger fade-out animation
    setDeletingTaskId(taskId);
    setDeletingTask(null);

    // Wait for animation to complete (300ms)
    await new Promise((resolve) => setTimeout(resolve, 300));

    // Delete the task
    const result = await deleteTask(taskId);
    setDeletingTaskId(null);
    return result;
  };

  const handleToggleComplete = async (taskId: number) => {
    await toggleComplete(taskId);
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Tasks</h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Manage your tasks and stay organized
          </p>
        </div>
        <Button
          onClick={() => setIsCreateDialogOpen(true)}
          className="w-full sm:w-auto min-h-[44px]"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Task
        </Button>
      </div>

      {/* Task List */}
      <TaskList
        tasks={tasks}
        state={state}
        error={error}
        onRetry={refetch}
        onAddTask={() => setIsCreateDialogOpen(true)}
        onToggleComplete={handleToggleComplete}
        onEdit={setEditingTask}
        onDelete={setDeletingTask}
        deletingTaskId={deletingTaskId}
      />

      {/* Create Task Dialog */}
      <CreateTaskDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSubmit={handleCreateTask}
      />

      {/* Edit Task Dialog */}
      <EditTaskDialog
        task={editingTask}
        open={!!editingTask}
        onOpenChange={(open) => !open && setEditingTask(null)}
        onSubmit={handleUpdateTask}
      />

      {/* Delete Task Dialog */}
      <DeleteTaskDialog
        task={deletingTask}
        open={!!deletingTask}
        onOpenChange={(open) => !open && setDeletingTask(null)}
        onConfirm={handleDeleteTask}
      />
    </div>
  );
}
