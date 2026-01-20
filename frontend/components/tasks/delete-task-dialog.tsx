"use client";

import { useState } from "react";
import { Loader2, AlertTriangle } from "lucide-react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import type { TaskResponse } from "@/types/task";

interface DeleteTaskDialogProps {
  task: TaskResponse | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (taskId: number) => Promise<boolean>;
}

export function DeleteTaskDialog({
  task,
  open,
  onOpenChange,
  onConfirm,
}: DeleteTaskDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleConfirm() {
    if (!task) return;

    setIsDeleting(true);
    try {
      await onConfirm(task.id);
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-full bg-destructive/10 flex items-center justify-center">
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <AlertDialogTitle>Delete Task</AlertDialogTitle>
          </div>
          <AlertDialogDescription className="pt-2">
            Are you sure you want to delete{" "}
            <span className="font-medium text-foreground">
              &quot;{task?.title}&quot;
            </span>
            ? This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              "Delete"
            )}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
