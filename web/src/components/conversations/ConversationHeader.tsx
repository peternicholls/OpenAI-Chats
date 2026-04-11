"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Trash2, Star } from "lucide-react";
import { TagEditor } from "@/components/tags/TagEditor";
import type { ConversationDetail } from "@/types";

function formatDate(timestamp: number | null): string {
    if (!timestamp) return "Unknown";
    return new Date(timestamp * 1000).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

function isSameDay(t1: number | null, t2: number | null): boolean {
    if (!t1 || !t2) return false;
    const d1 = new Date(t1 * 1000);
    const d2 = new Date(t2 * 1000);
    return d1.getFullYear() === d2.getFullYear()
        && d1.getMonth() === d2.getMonth()
        && d1.getDate() === d2.getDate();
}

interface ConversationHeaderProps {
    conversation: ConversationDetail;
    onExport?: () => void;
    onDelete?: () => void;
    onToggleFavorite?: () => void;
    isFavorite?: boolean;
}

export function ConversationHeader({
    conversation,
    onExport,
    onDelete,
    onToggleFavorite,
    isFavorite,
}: ConversationHeaderProps) {
    return (
        <div className="flex flex-col gap-3 mb-6">
            <div className="flex items-center gap-2">
                <Link href="/">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <h1 className="text-xl font-bold flex-1 line-clamp-1">
                    {conversation.title || "[Untitled]"}
                </h1>
                <div className="flex items-center gap-2">
                    {onToggleFavorite && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onToggleFavorite}
                            className={isFavorite ? "text-yellow-500" : ""}
                        >
                            <Star className={`h-4 w-4 mr-1 ${isFavorite ? "fill-current" : ""}`} />
                            {isFavorite ? "Favorited" : "Favorite"}
                        </Button>
                    )}
                    {onExport && (
                        <Button variant="outline" size="sm" onClick={onExport}>
                            <Download className="h-4 w-4 mr-1" />
                            Export
                        </Button>
                    )}
                    {onDelete && (
                        <Button variant="outline" size="sm" onClick={onDelete} className="text-destructive">
                            <Trash2 className="h-4 w-4 mr-1" />
                            Delete
                        </Button>
                    )}
                </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{formatDate(conversation.create_time)}</span>
                {conversation.update_time && !isSameDay(conversation.create_time, conversation.update_time) && (
                    <span>Updated {formatDate(conversation.update_time)}</span>
                )}
                <span>{conversation.message_count} messages</span>
                {conversation.model && <span>{conversation.model}</span>}
            </div>
            <TagEditor
                conversationId={conversation.id}
                tags={conversation.tags}
            />
        </div>
    );
}
