"use client";

import { useState, useRef, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Plus, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { useAddTag, useRemoveTag, useTags } from "@/hooks/useTags";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface TagEditorProps {
    conversationId: string;
    tags: string[];
    className?: string;
    maxTags?: number;
}

const TAG_PATTERN = /^[a-zA-Z0-9_-]+$/;
const MAX_TAG_LENGTH = 50;

export function TagEditor({
    conversationId,
    tags,
    className,
    maxTags = 10,
}: TagEditorProps) {
    const searchParams = useSearchParams();
    const activeTagFilter = searchParams.get("tag");

    const [open, setOpen] = useState(false);
    const [inputValue, setInputValue] = useState("");
    const [showSuggestions, setShowSuggestions] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const { data: allTags } = useTags();
    const { mutateAsync: addTag, isPending: isAdding } = useAddTag(conversationId);
    const { mutateAsync: removeTag, isPending: isRemoving } = useRemoveTag(conversationId);

    // Filter suggestions based on input
    const suggestions = allTags
        ?.filter(
            (t) =>
                t.name.toLowerCase().includes(inputValue.toLowerCase()) &&
                !tags.includes(t.name)
        )
        .slice(0, 5) ?? [];

    const validateTag = (tag: string): string | null => {
        if (!tag.trim()) {
            return "Tag cannot be empty";
        }
        if (tag.length > MAX_TAG_LENGTH) {
            return `Tag must be ${MAX_TAG_LENGTH} characters or less`;
        }
        if (!TAG_PATTERN.test(tag)) {
            return "Tag can only contain letters, numbers, hyphens, and underscores";
        }
        if (tags.includes(tag.toLowerCase())) {
            return "Tag already exists";
        }
        if (tags.length >= maxTags) {
            return `Maximum ${maxTags} tags allowed`;
        }
        return null;
    };

    const handleAddTag = async (tagName: string) => {
        const cleanTag = tagName.trim().toLowerCase();
        const error = validateTag(cleanTag);
        if (error) {
            toast.error(error);
            return;
        }

        try {
            await addTag(cleanTag);
            setInputValue("");
            setShowSuggestions(false);
            toast.success(`Added tag "${cleanTag}"`);
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to add tag";
            toast.error(message);
        }
    };

    const handleRemoveTag = async (tagName: string) => {
        // Warn if removing tag that matches active filter and it's the only matching tag
        if (activeTagFilter && tagName === activeTagFilter && tags.filter(t => t === activeTagFilter).length === 1) {
            toast.info(
                "Removing this tag will hide this conversation from the current filtered view",
                { duration: 4000 }
            );
        }

        try {
            await removeTag(tagName);
            toast.success(`Removed tag "${tagName}"`);
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to remove tag";
            toast.error(message);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleAddTag(inputValue);
        } else if (e.key === "Escape") {
            setOpen(false);
        }
    };

    useEffect(() => {
        if (open && inputRef.current) {
            inputRef.current.focus();
        }
    }, [open]);

    return (
        <div className={cn("flex flex-wrap items-center gap-1", className)}>
            {tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs gap-1 pr-1">
                    {tag}
                    <button
                        onClick={() => handleRemoveTag(tag)}
                        disabled={isRemoving}
                        className="ml-1 hover:bg-muted rounded-full p-0.5"
                        aria-label={`Remove tag ${tag}`}
                    >
                        <X className="h-3 w-3" />
                    </button>
                </Badge>
            ))}
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        size="sm"
                        className="h-6 px-2 text-xs"
                        disabled={tags.length >= maxTags}
                    >
                        <Plus className="h-3 w-3 mr-1" />
                        Add Tag
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-64 p-2" align="start">
                    <div className="space-y-2">
                        <Input
                            ref={inputRef}
                            placeholder="Enter tag name..."
                            value={inputValue}
                            onChange={(e) => {
                                setInputValue(e.target.value);
                                setShowSuggestions(e.target.value.length > 0);
                            }}
                            onKeyDown={handleKeyDown}
                            onFocus={() => setShowSuggestions(inputValue.length > 0)}
                            disabled={isAdding}
                            className="h-8"
                        />
                        {showSuggestions && suggestions.length > 0 && (
                            <div className="border rounded-md">
                                {suggestions.map((tag) => (
                                    <button
                                        key={tag.name}
                                        onClick={() => handleAddTag(tag.name)}
                                        className="w-full px-2 py-1.5 text-left text-sm hover:bg-muted flex justify-between items-center"
                                    >
                                        <span>{tag.name}</span>
                                        <span className="text-xs text-muted-foreground">
                                            ({tag.count})
                                        </span>
                                    </button>
                                ))}
                            </div>
                        )}
                        <p className="text-xs text-muted-foreground">
                            Press Enter to add. Letters, numbers, hyphens, underscores only.
                        </p>
                    </div>
                </PopoverContent>
            </Popover>
        </div>
    );
}
