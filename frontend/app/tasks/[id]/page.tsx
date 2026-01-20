"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, notFound } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { tasksApi } from "@/lib/api-client";
import { TaskDetail } from "@/components/tasks/task-detail";
import { EditTaskDialog } from "@/components/tasks/edit-task-dialog";
import { DeleteTaskDialog } from "@/components/tasks/delete-task-dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { ApiError, NetworkError } from "@/types/api";
import { toast } from "sonner";
import type { TaskResponse } from "@/types/task";
import { use } from "react";

interface TaskDetailPageProps {
  params: Promise<{ id: string }>;
}

function TaskDetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* Back Button Skeleton */}
      <Skeleton className="h-10 w-32" />

      {/* Task Card Skeleton */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-start gap-4">
            <Skeleton className="h-6 w-6 rounded" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-5 w-24" />
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-5 w-48" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-48" />
            </div>
          </div>
          <div className="flex gap-3 pt-4 border-t">
            <Skeleton className="h-11 flex-1" />
            <Skeleton className="h-11 flex-1" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function TaskDetailPage({ params }: TaskDetailPageProps) {
  const { id } = use(params);
  const { user } = useAuth();
  const router = useRouter();

  const [task, setTask] = useState<TaskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialog states
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const taskId = parseInt(id, 10);

  const fetchTask = useCallback(async () => {
    if (!user?.id || isNaN(taskId)) return;

    setIsLoading(true);
    setError(null);

    try {
      const fetchedTask = await tasksApi.get(user.id, taskId);
      setTask(fetchedTask);
    } catch (err) {
      console.error("Failed to fetch task:", err);
      if (err instanceof ApiError) {
        if (err.isNotFound) {
          setError("not_found");
        } else if (err.isUnauthorized || err.isForbidden) {
          toast.error("Session expired. Please log in again.");
          router.push("/signin");
        } else {
          setError(err.userMessage);
        }
      } else if (err instanceof NetworkError) {
        setError("Unable to connect to server");
      } else {
        setError("Failed to load task");
      }
    } finally {
      setIsLoading(false);
    }
  }, [user?.id, taskId, router]);

  useEffect(() => {
    fetchTask();
  }, [fetchTask]);

  const handleToggleComplete = async (taskId: number) => {
    if (!user?.id || !task) return;

    setIsToggling(true);
    try {
      const updatedTask = await tasksApi.toggleComplete(user.id, taskId);
      setTask(updatedTask);
      toast.success(
        updatedTask.is_completed ? "Task marked complete" : "Task marked incomplete"
      );
    } catch (err) {
      console.error("Failed to toggle task:", err);
      if (err instanceof ApiError) {
        toast.error(err.userMessage);
      } else {
        toast.error("Failed to update task");
      }
    } finally {
      setIsToggling(false);
    }
  };

  const handleUpdateTask = async (taskId: number, title: string) => {
    if (!user?.id) return null;

    try {
      const updatedTask = await tasksApi.update(user.id, taskId, { title });
      setTask(updatedTask);
      setIsEditDialogOpen(false);
      toast.success("Task updated successfully");
      return updatedTask;
    } catch (err) {
      console.error("Failed to update task:", err);
      if (err instanceof ApiError) {
        toast.error(err.userMessage);
      } else {
        toast.error("Failed to update task");
      }
      return null;
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!user?.id) return false;

    try {
      await tasksApi.delete(user.id, taskId);
      toast.success("Task deleted successfully");
      router.push("/tasks");
      return true;
    } catch (err) {
      console.error("Failed to delete task:", err);
      if (err instanceof ApiError) {
        toast.error(err.userMessage);
      } else {
        toast.error("Failed to delete task");
      }
      return false;
    }
  };

  if (isLoading) {
    return <TaskDetailSkeleton />;
  }

  if (error === "not_found" || !task) {
    notFound();
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <p className="text-muted-foreground">{error}</p>
      </div>
    );
  }

  return (
    <>
      <TaskDetail
        task={task}
        onToggleComplete={handleToggleComplete}
        onEdit={() => setIsEditDialogOpen(true)}
        onDelete={() => setIsDeleteDialogOpen(true)}
        isToggling={isToggling}
      />

      {/* Edit Task Dialog */}
      <EditTaskDialog
        task={task}
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        onSubmit={handleUpdateTask}
      />

      {/* Delete Task Dialog */}
      <DeleteTaskDialog
        task={task}
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onConfirm={handleDeleteTask}
      />
    </>
  );
}
