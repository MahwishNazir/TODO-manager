import Link from "next/link";
import { Button } from "@/components/ui/button";
import { FileQuestion, ArrowLeft } from "lucide-react";

export default function TaskNotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
        <FileQuestion className="h-10 w-10 text-muted-foreground" />
      </div>
      <h2 className="text-2xl font-semibold mb-2">Task Not Found</h2>
      <p className="text-muted-foreground text-center mb-6 max-w-sm">
        The task you&apos;re looking for doesn&apos;t exist or you don&apos;t have
        permission to view it.
      </p>
      <Button asChild>
        <Link href="/tasks">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Tasks
        </Link>
      </Button>
    </div>
  );
}
