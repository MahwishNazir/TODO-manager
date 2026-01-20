"use client";

import { useState } from "react";
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
import { createTaskSchema, type CreateTaskInput } from "@/lib/validations";
import { TASK_TITLE } from "@/lib/constants";
import type { TaskResponse } from "@/types/task";

interface CreateTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (title: string) => Promise<TaskResponse | null>;
}

export function CreateTaskDialog({
  open,
  onOpenChange,
  onSubmit,
}: CreateTaskDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<CreateTaskInput>({
    resolver: zodResolver(createTaskSchema),
    defaultValues: {
      title: "",
    },
  });

  const title = form.watch("title");
  const remainingChars = TASK_TITLE.MAX_LENGTH - (title?.length || 0);

  async function handleSubmit(data: CreateTaskInput) {
    setIsSubmitting(true);
    try {
      const result = await onSubmit(data.title);
      if (result) {
        form.reset();
      }
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
          <DialogTitle>Create Task</DialogTitle>
          <DialogDescription>
            Add a new task to your list. Click save when you&apos;re done.
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
                    Creating...
                  </>
                ) : (
                  "Create Task"
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
