"use client";

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { tasksApi } from "@/lib/api-client";
import { ApiError, NetworkError } from "@/types/api";
import type { TaskResponse } from "@/types/task";
import type { AsyncState } from "@/types/form";

interface UseTasksReturn {
  tasks: TaskResponse[];
  state: AsyncState;
  error: string | null;
  refetch: () => Promise<void>;
  createTask: (title: string) => Promise<TaskResponse | null>;
  updateTask: (taskId: number, title: string) => Promise<TaskResponse | null>;
  toggleComplete: (taskId: number) => Promise<TaskResponse | null>;
  deleteTask: (taskId: number) => Promise<boolean>;
}

export function useTasks(userId: string | undefined): UseTasksReturn {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [state, setState] = useState<AsyncState>("idle");
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    if (!userId) return;

    setState("loading");
    setError(null);

    try {
      const response = await tasksApi.list(userId);
      setTasks(response.tasks);
      setState("success");
    } catch (err) {
      console.error("Failed to fetch tasks:", err);
      if (err instanceof ApiError) {
        setError(err.userMessage);
        if (err.isUnauthorized || err.isForbidden) {
          toast.error("Session expired. Please log in again.");
        } else {
          toast.error(err.userMessage);
        }
      } else if (err instanceof NetworkError) {
        setError("Unable to connect to server. Please check your connection.");
        toast.error("Unable to connect to server");
      } else {
        setError("Failed to load tasks");
        toast.error("Failed to load tasks");
      }
      setState("error");
    }
  }, [userId]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = async (title: string): Promise<TaskResponse | null> => {
    if (!userId) return null;

    try {
      const newTask = await tasksApi.create(userId, { title });
      setTasks((prev) => [newTask, ...prev]);
      toast.success("Task created successfully");
      return newTask;
    } catch (err) {
      console.error("Failed to create task:", err);
      if (err instanceof ApiError) {
        toast.error(err.userMessage);
      } else if (err instanceof NetworkError) {
        toast.error("Unable to connect to server");
      } else {
        toast.error("Failed to create task");
      }
      return null;
    }
  };

  const updateTask = async (taskId: number, title: string): Promise<TaskResponse | null> => {
    if (!userId) return null;

    try {
      const updatedTask = await tasksApi.update(userId, taskId, { title });
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      toast.success("Task updated successfully");
      return updatedTask;
    } catch (err) {
      console.error("Failed to update task:", err);
      if (err instanceof ApiError) {
        toast.error(err.userMessage);
      } else if (err instanceof NetworkError) {
        toast.error("Unable to connect to server");
      } else {
        toast.error("Failed to update task");
      }
      return null;
    }
  };

  const toggleComplete = async (taskId: number): Promise<TaskResponse | null> => {
    if (!userId) return null;

    try {
      const updatedTask = await tasksApi.toggleComplete(userId, taskId);
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      toast.success(
        updatedTask.is_completed ? "Task marked complete" : "Task marked incomplete"
      );
      return updatedTask;
    } catch (err) {
      console.error("Failed to toggle task:", err);
      if (err instanceof ApiError) {
        toast.error(err.userMessage);
      } else if (err instanceof NetworkError) {
        toast.error("Unable to connect to server");
      } else {
        toast.error("Failed to update task");
      }
      return null;
    }
  };

  const deleteTask = async (taskId: number): Promise<boolean> => {
    if (!userId) return false;

    try {
      await tasksApi.delete(userId, taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
      toast.success("Task deleted successfully");
      return true;
    } catch (err) {
      console.error("Failed to delete task:", err);
      if (err instanceof ApiError) {
        toast.error(err.userMessage);
      } else if (err instanceof NetworkError) {
        toast.error("Unable to connect to server");
      } else {
        toast.error("Failed to delete task");
      }
      return false;
    }
  };

  return {
    tasks,
    state,
    error,
    refetch: fetchTasks,
    createTask,
    updateTask,
    toggleComplete,
    deleteTask,
  };
}
