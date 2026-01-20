import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";

export function TaskSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-4">
        <Skeleton className="h-5 w-5 rounded" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/4" />
        </div>
        <Skeleton className="h-8 w-20" />
      </div>
    </Card>
  );
}

export function TaskListSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <TaskSkeleton key={i} />
      ))}
    </div>
  );
}
