"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Tags } from "lucide-react";
import { useTags } from "@/hooks/useTags";
import { Badge } from "@/components/ui/badge";
import { CollapsibleSection } from "@/components/layout/CollapsibleSection";
import { cn } from "@/lib/utils";

export function SidebarTagsSection({ onNavigate }: { onNavigate?: () => void } = {}) {
    const router = useRouter();
    const searchParams = useSearchParams();
    const activeTag = searchParams.get("tag");
    const { data: tags } = useTags();

    if (!tags || tags.length === 0) {
        return null;
    }

    const handleTagClick = (name: string) => {
        onNavigate?.();
        if (activeTag === name) {
            router.push("/");
        } else {
            router.push(`/?tag=${encodeURIComponent(name)}`);
        }
    };

    return (
        <CollapsibleSection
            sectionId="tags"
            title="Tags"
            icon={<Tags className="h-3.5 w-3.5" aria-hidden="true" />}
            count={tags.length}
        >
            <div className="flex flex-wrap gap-1 px-2">
                {tags.map((tag) => {
                    const isActive = activeTag === tag.name;
                    return (
                        <button
                            key={tag.name}
                            type="button"
                            onClick={() => handleTagClick(tag.name)}
                            className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-full"
                            aria-pressed={isActive}
                        >
                            <Badge
                                variant={isActive ? "default" : "secondary"}
                                className={cn(
                                    "cursor-pointer text-[11px]",
                                    isActive && "bg-primary text-primary-foreground"
                                )}
                            >
                                {tag.name}
                                <span className="ml-1 opacity-60">({tag.count})</span>
                            </Badge>
                        </button>
                    );
                })}
            </div>
        </CollapsibleSection>
    );
}
