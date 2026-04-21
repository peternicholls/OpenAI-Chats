"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTags, useRenameTag } from "@/hooks/useTags";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tags, X, Pencil, Check } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface TagListProps {
    className?: string;
}

export function TagList({ className }: TagListProps) {
    const router = useRouter();
    const searchParams = useSearchParams();
    const activeTag = searchParams.get("tag");
    const { data: tags, isLoading } = useTags();
    const { mutateAsync: renameTag } = useRenameTag();

    const [editingTag, setEditingTag] = useState<string | null>(null);
    const [editValue, setEditValue] = useState("");

    const handleTagClick = (tagName: string) => {
        if (editingTag) return; // Ignore click when editing
        if (activeTag === tagName) {
            router.push("/");
        } else {
            router.push(`/?tag=${encodeURIComponent(tagName)}`);
        }
    };

    const handleClearFilter = () => {
        router.push("/");
    };

    const startEditing = (tagName: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setEditingTag(tagName);
        setEditValue(tagName);
    };

    const commitRename = async () => {
        if (!editingTag) return;
        const newName = editValue.trim();
        if (newName && newName !== editingTag) {
            try {
                await renameTag({ oldName: editingTag, newName });
                if (activeTag === editingTag) {
                    router.push(`/?tag=${encodeURIComponent(newName)}`);
                }
                toast.success(`Renamed tag "${editingTag}" to "${newName}"`);
            } catch (err) {
                const message = err instanceof Error ? err.message : "Failed to rename tag";
                toast.error(message);
            }
        }
        setEditingTag(null);
        setEditValue("");
    };

    const cancelEditing = () => {
        setEditingTag(null);
        setEditValue("");
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
                    <div key={tag.name} className="flex items-center gap-0.5 group">
                        {editingTag === tag.name ? (
                            <div className="flex items-center gap-1">
                                <Input
                                    value={editValue}
                                    onChange={(e) => setEditValue(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") commitRename();
                                        if (e.key === "Escape") cancelEditing();
                                    }}
                                    className="h-6 text-xs w-28 px-1"
                                    autoFocus
                                />
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-5 w-5 p-0"
                                            onClick={commitRename}
                                            aria-label="Confirm rename"
                                        >
                                            <Check className="h-3 w-3" />
                                        </Button>
                                    </TooltipTrigger>
                                    <TooltipContent>Confirm rename</TooltipContent>
                                </Tooltip>
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-5 w-5 p-0"
                                            onClick={cancelEditing}
                                            aria-label="Cancel rename"
                                        >
                                            <X className="h-3 w-3" />
                                        </Button>
                                    </TooltipTrigger>
                                    <TooltipContent>Cancel rename</TooltipContent>
                                </Tooltip>
                            </div>
                        ) : (
                            <>
                                <Badge
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
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-5 w-5 p-0 opacity-0 transition-opacity group-hover:opacity-100"
                                            onClick={(e) => startEditing(tag.name, e)}
                                            aria-label={`Rename tag ${tag.name}`}
                                        >
                                            <Pencil className="h-3 w-3" />
                                        </Button>
                                    </TooltipTrigger>
                                    <TooltipContent>Rename {tag.name}</TooltipContent>
                                </Tooltip>
                            </>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
