import { ClipboardList, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  onAddTask?: () => void;
}

export function EmptyState({ onAddTask }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-6">
        <ClipboardList className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-xl font-semibold mb-2">No tasks yet</h3>
      <p className="text-muted-foreground text-center mb-6 max-w-sm">
        Create your first task to get started with your todo list.
      </p>
      {onAddTask && (
        <Button onClick={onAddTask}>
          <Plus className="h-4 w-4 mr-2" />
          Add Task
        </Button>
      )}
    </div>
  );
}
