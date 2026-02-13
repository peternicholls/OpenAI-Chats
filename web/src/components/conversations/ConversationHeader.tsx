"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Download, Trash2 } from "lucide-react";
import type { ConversationDetail } from "@/types";

function formatDate(timestamp: number | null): string {
    if (!timestamp) return "Unknown";
    return new Date(timestamp * 1000).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

interface ConversationHeaderProps {
    conversation: ConversationDetail;
    onExport?: () => void;
    onDelete?: () => void;
}

export function ConversationHeader({
    conversation,
    onExport,
    onDelete,
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
                <span>{conversation.message_count} messages</span>
                {conversation.model && <span>{conversation.model}</span>}
            </div>
            {conversation.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                    {conversation.tags.map((tag) => (
                        <Badge key={tag} variant="secondary">
                            {tag}
                        </Badge>
                    ))}
                </div>
            )}
        </div>
    );
}
