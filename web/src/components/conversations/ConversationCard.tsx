"use client";

import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { FavoriteButton } from "@/components/favorites/FavoriteButton";
import type { Conversation } from "@/types";

function formatDate(timestamp: number | null): string {
    if (!timestamp) return "Unknown date";
    return new Date(timestamp * 1000).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

interface ConversationCardProps {
    conversation: Conversation;
    selectable?: boolean;
    isSelected?: boolean;
    onSelectChange?: (id: string, selected: boolean) => void;
}

export function ConversationCard({
    conversation,
    selectable = false,
    isSelected = false,
    onSelectChange,
}: ConversationCardProps) {
    const handleCheckboxClick = (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        onSelectChange?.(conversation.id, !isSelected);
    };

    return (
        <Link href={`/conversation/${conversation.id}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-2">
                        {selectable && (
                            <div onClick={handleCheckboxClick} className="shrink-0 pt-0.5">
                                <Checkbox
                                    checked={isSelected}
                                    aria-label={`Select ${conversation.title || "conversation"}`}
                                />
                            </div>
                        )}
                        <div className="flex-1 min-w-0">
                            <CardTitle className="text-base font-medium line-clamp-1">
                                {conversation.title || "[Untitled]"}
                            </CardTitle>
                            <CardDescription>
                                {formatDate(conversation.create_time)} &middot;{" "}
                                {conversation.message_count} messages
                                {conversation.model && (
                                    <> &middot; {conversation.model}</>
                                )}
                            </CardDescription>
                        </div>
                        <FavoriteButton
                            conversationId={conversation.id}
                            isFavorite={conversation.is_favorite}
                            size="icon"
                            className="h-8 w-8"
                        />
                    </div>
                </CardHeader>
                {conversation.tags.length > 0 && (
                    <CardContent className="pt-0 pb-3">
                        <div className="flex flex-wrap gap-1">
                            {conversation.tags.map((tag) => (
                                <Badge key={tag} variant="secondary" className="text-xs">
                                    {tag}
                                </Badge>
                            ))}
                        </div>
                    </CardContent>
                )}
            </Card>
        </Link>
    );
}
