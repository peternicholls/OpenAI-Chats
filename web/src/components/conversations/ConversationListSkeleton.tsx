import { Skeleton } from "@/components/ui/skeleton";

export function ConversationListSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-3">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="rounded-lg border p-4 space-y-3">
          <div className="flex items-center justify-between gap-4">
            <Skeleton className="h-5 w-2/3" />
            <Skeleton className="h-4 w-12" />
          </div>
          <Skeleton className="h-4 w-1/2" />
          <div className="flex gap-2">
            <Skeleton className="h-5 w-16" />
            <Skeleton className="h-5 w-14" />
          </div>
        </div>
      ))}
    </div>
  );
}
