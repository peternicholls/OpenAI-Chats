"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Star } from "lucide-react";
import { TagEditor } from "@/components/tags/TagEditor";
import type { ConversationDetail } from "@/types";

function formatDate(timestamp: number | null): string {
    if (!timestamp) return "Unknown";
    return new Date(timestamp * 1000).toLocaleDateString("en-GB", {
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
    onToggleFavorite?: () => void;
    isFavorite?: boolean;
}

export function ConversationHeader({
    conversation,
    onExport,
    onToggleFavorite,
    isFavorite,
}: ConversationHeaderProps) {
    const visibleMessageCount = conversation.messages
        ? conversation.messages.filter((m) => m.role === "user" || m.role === "assistant").length
        : conversation.message_count;

    return (
        <header className="mb-8 flex flex-col gap-3">
            <div className="flex items-center gap-2">
                <Link href="/">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <h1 className="text-[17px] font-bold tracking-[-0.015em] leading-[1.3] flex-1 line-clamp-2">
                    {conversation.title || "[Untitled]"}
                </h1>
                <div className="flex items-center gap-1.5">
                    {onToggleFavorite && (
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={onToggleFavorite}
                            className={`h-8 w-8 ${isFavorite ? "text-yellow-500" : "text-muted-foreground"}`}
                        >
                            <Star className={`h-4 w-4 ${isFavorite ? "fill-current" : ""}`} />
                        </Button>
                    )}
                    {onExport && (
                        <Button variant="ghost" size="icon" onClick={onExport} className="h-8 w-8 text-muted-foreground">
                            <Download className="h-4 w-4" />
                        </Button>
                    )}

                </div>
            </div>
            <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[12.5px] text-muted-foreground">
                <span>{formatDate(conversation.create_time)}</span>
                {conversation.update_time && !isSameDay(conversation.create_time, conversation.update_time) && (
                    <>
                        <span aria-hidden>·</span>
                        <span className="italic text-muted-foreground/70">Updated {formatDate(conversation.update_time)}</span>
                    </>
                )}
                <span aria-hidden>·</span>
                <span>{visibleMessageCount} messages</span>
                {conversation.model && (
                    <>
                        <span aria-hidden>·</span>
                        <span>{conversation.model}</span>
                    </>
                )}
            </div>
            <TagEditor
                conversationId={conversation.id}
                tags={conversation.tags}
            />
        </header>
    );
}
