"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { updateTaskSchema, type UpdateTaskInput } from "@/lib/validations";
import { TASK_TITLE } from "@/lib/constants";
import type { TaskResponse } from "@/types/task";

interface EditTaskDialogProps {
  task: TaskResponse | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (taskId: number, title: string) => Promise<TaskResponse | null>;
}

export function EditTaskDialog({
  task,
  open,
  onOpenChange,
  onSubmit,
}: EditTaskDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<UpdateTaskInput>({
    resolver: zodResolver(updateTaskSchema),
    defaultValues: {
      title: "",
    },
  });

  // Reset form when task changes
  useEffect(() => {
    if (task) {
      form.reset({ title: task.title });
    }
  }, [task, form]);

  const title = form.watch("title");
  const remainingChars = TASK_TITLE.MAX_LENGTH - (title?.length || 0);

  async function handleSubmit(data: UpdateTaskInput) {
    if (!task) return;

    setIsSubmitting(true);
    try {
      await onSubmit(task.id, data.title);
    } finally {
      setIsSubmitting(false);
    }
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      form.reset();
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Task</DialogTitle>
          <DialogDescription>
            Make changes to your task. Click save when you&apos;re done.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Task Title</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter task title..."
                      autoFocus
                      disabled={isSubmitting}
                      {...field}
                    />
                  </FormControl>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <FormMessage />
                    <span
                      className={
                        remainingChars < 50 ? "text-destructive" : undefined
                      }
                    >
                      {remainingChars} characters remaining
                    </span>
                  </div>
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  "Save Changes"
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
