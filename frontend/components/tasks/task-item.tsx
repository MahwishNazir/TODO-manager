"use client";

import { useState } from "react";
import Link from "next/link";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, Pencil, Trash2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { TaskResponse } from "@/types/task";

interface TaskItemProps {
  task: TaskResponse;
  onToggleComplete: (taskId: number) => Promise<void>;
  onEdit: (task: TaskResponse) => void;
  onDelete: (task: TaskResponse) => void;
  isDeleting?: boolean;
}

export function TaskItem({ task, onToggleComplete, onEdit, onDelete, isDeleting = false }: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);

  const handleToggle = async () => {
    if (isToggling) return;
    setIsToggling(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const formattedDate = new Date(task.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <Card
      className={cn(
        "p-4 transition-all hover:shadow-md",
        isDeleting && "animate-fade-out opacity-0 scale-95"
      )}
    >
      <div className="flex items-center gap-4">
        <div className="flex items-center justify-center min-h-[44px] min-w-[44px]">
          {isToggling ? (
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          ) : (
            <Checkbox
              checked={task.is_completed}
              onCheckedChange={handleToggle}
              className="h-5 w-5"
              aria-label={`Mark "${task.title}" as ${task.is_completed ? "incomplete" : "complete"}`}
            />
          )}
        </div>

        <Link href={`/tasks/${task.id}`} className="flex-1 min-w-0">
          <div className="space-y-1">
            <p
              className={cn(
                "font-medium truncate transition-all",
                task.is_completed && "line-through text-muted-foreground"
              )}
            >
              {task.title}
            </p>
            <p className="text-xs text-muted-foreground">
              Created {formattedDate}
            </p>
          </div>
        </Link>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="min-h-[44px] min-w-[44px]"
              aria-label="Task options"
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(task)}>
              <Pencil className="h-4 w-4 mr-2" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete(task)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </Card>
  );
}
