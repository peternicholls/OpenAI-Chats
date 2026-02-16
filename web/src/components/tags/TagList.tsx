"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useTags } from "@/hooks/useTags";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tags, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface TagListProps {
    className?: string;
}

export function TagList({ className }: TagListProps) {
    const router = useRouter();
    const searchParams = useSearchParams();
    const activeTag = searchParams.get("tag");
    const { data: tags, isLoading } = useTags();

    const handleTagClick = (tagName: string) => {
        if (activeTag === tagName) {
            // Remove filter
            router.push("/");
        } else {
            // Apply filter
            router.push(`/?tag=${encodeURIComponent(tagName)}`);
        }
    };

    const handleClearFilter = () => {
        router.push("/");
    };

    if (isLoading) {
        return (
            <div className={cn("space-y-2", className)}>
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Tags className="h-4 w-4" />
                    <span>Tags</span>
                </div>
                <div className="space-y-1">
                    {[1, 2, 3].map((i) => (
                        <div
                            key={i}
                            className="h-6 bg-muted animate-pulse rounded"
                        />
                    ))}
                </div>
            </div>
        );
    }

    if (!tags || tags.length === 0) {
        return (
            <div className={cn("space-y-2", className)}>
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Tags className="h-4 w-4" />
                    <span>Tags</span>
                </div>
                <p className="text-xs text-muted-foreground pl-6">
                    No tags yet. Add tags to conversations to organize them.
                </p>
            </div>
        );
    }

    return (
        <div className={cn("space-y-2", className)}>
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Tags className="h-4 w-4" />
                    <span>Tags</span>
                </div>
                {activeTag && (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleClearFilter}
                        className="h-6 px-2 text-xs"
                    >
                        <X className="h-3 w-3 mr-1" />
                        Clear
                    </Button>
                )}
            </div>
            <div className="flex flex-wrap gap-1 pl-6">
                {tags.map((tag) => (
                    <Badge
                        key={tag.name}
                        variant={activeTag === tag.name ? "default" : "secondary"}
                        className={cn(
                            "cursor-pointer transition-colors text-xs",
                            activeTag === tag.name && "bg-primary text-primary-foreground"
                        )}
                        onClick={() => handleTagClick(tag.name)}
                    >
                        {tag.name}
                        <span className="ml-1 opacity-60">({tag.count})</span>
                    </Badge>
                ))}
            </div>
        </div>
    );
}
