"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Pencil,
  Trash2,
  Calendar,
  Clock,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { TaskResponse } from "@/types/task";

interface TaskDetailProps {
  task: TaskResponse;
  onToggleComplete: (taskId: number) => Promise<void>;
  onEdit: () => void;
  onDelete: () => void;
  isToggling?: boolean;
}

export function TaskDetail({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
  isToggling = false,
}: TaskDetailProps) {
  const router = useRouter();

  const handleToggle = async () => {
    if (isToggling) return;
    await onToggleComplete(task.id);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button
        variant="ghost"
        onClick={() => router.push("/tasks")}
        className="min-h-[44px] -ml-2"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Tasks
      </Button>

      {/* Task Card */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4 flex-1">
              <div className="flex items-center justify-center min-h-[44px] min-w-[44px] mt-1">
                {isToggling ? (
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                ) : (
                  <Checkbox
                    checked={task.is_completed}
                    onCheckedChange={handleToggle}
                    className="h-6 w-6"
                    aria-label={`Mark task as ${task.is_completed ? "incomplete" : "complete"}`}
                  />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <CardTitle
                  className={cn(
                    "text-xl sm:text-2xl break-words",
                    task.is_completed && "line-through text-muted-foreground"
                  )}
                >
                  {task.title}
                </CardTitle>
                <Badge
                  variant={task.is_completed ? "secondary" : "default"}
                  className="mt-2"
                >
                  {task.is_completed ? "Completed" : "In Progress"}
                </Badge>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Timestamps */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex items-start gap-3 text-sm">
              <Calendar className="h-4 w-4 mt-0.5 text-muted-foreground" />
              <div>
                <p className="text-muted-foreground">Created</p>
                <p className="font-medium">{formatDate(task.created_at)}</p>
              </div>
            </div>
            <div className="flex items-start gap-3 text-sm">
              <Clock className="h-4 w-4 mt-0.5 text-muted-foreground" />
              <div>
                <p className="text-muted-foreground">Last Updated</p>
                <p className="font-medium">{formatDate(task.updated_at)}</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t">
            <Button
              variant="outline"
              onClick={onEdit}
              className="flex-1 min-h-[44px]"
            >
              <Pencil className="h-4 w-4 mr-2" />
              Edit Task
            </Button>
            <Button
              variant="destructive"
              onClick={onDelete}
              className="flex-1 min-h-[44px]"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Task
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
