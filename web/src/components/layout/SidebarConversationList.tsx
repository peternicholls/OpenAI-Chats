"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowDownUp, MessageSquare, Star } from "lucide-react";
import { useInfiniteConversations } from "@/hooks/useConversations";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { Conversation, SortOrder } from "@/types";

const SIDEBAR_CONVERSATION_LIMIT = 100;

function formatDate(timestamp: number | null): string {
    if (!timestamp) return "Unknown date";
    return new Date(timestamp * 1000).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

interface SidebarConversationListProps {
    /** When set, list shows only the supplied conversations (e.g. favourites). */
    items?: Conversation[];
    /** Empty-state message override. */
    emptyMessage?: string;
    /** Heading text for screen readers. */
    ariaLabel?: string;
    /** Hide the order toggle (useful inside nested sections). */
    hideOrderToggle?: boolean;
    /** Compact row variant for nested sections. */
    compact?: boolean;
    /** Optional callback for navigation actions, used by the mobile drawer. */
    onNavigate?: () => void;
}

export function SidebarConversationList({
    items,
    emptyMessage = "No conversations yet.",
    ariaLabel = "Conversations",
    hideOrderToggle = false,
    compact = false,
    onNavigate,
}: SidebarConversationListProps) {
    const params = useParams();
    const searchParams = useSearchParams();
    const activeId = (params?.id as string | undefined) ?? null;
    const tagFilter = searchParams.get("tag") || undefined;

    const [order, setOrder] = useState<SortOrder>("desc");
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const loadMoreRef = useRef<HTMLDivElement>(null);

    // Only fetch when no explicit items have been supplied.
    const query = useInfiniteConversations(
        items
            ? {}
            : { sortBy: "date", order, limit: SIDEBAR_CONVERSATION_LIMIT, tag: tagFilter }
    );
    const fetched = useMemo(
        () => (items ? null : query.data?.pages.flatMap((page) => page.items) ?? null),
        [items, query.data?.pages]
    );
    const isLoading = items ? false : query.isLoading;
    const isFetchingNextPage = items ? false : query.isFetchingNextPage;
    const hasNextPage = items ? false : (query.hasNextPage ?? false);

    const conversations: Conversation[] | null = items
        ? [...items].sort((a, b) => {
            const at = a.create_time ?? 0;
            const bt = b.create_time ?? 0;
            return order === "desc" ? bt - at : at - bt;
        })
        : fetched;

    useEffect(() => {
        if (items || !loadMoreRef.current || !scrollContainerRef.current || !hasNextPage) {
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0]?.isIntersecting && !query.isFetchingNextPage) {
                    void query.fetchNextPage();
                }
            },
            {
                root: scrollContainerRef.current,
                rootMargin: "160px 0px",
            }
        );

        observer.observe(loadMoreRef.current);
        return () => observer.disconnect();
    }, [hasNextPage, items, query]);

    return (
        <div className="flex h-full min-h-0 flex-col">
            {!hideOrderToggle && (
                <div className="flex items-center justify-between gap-2 px-2 pb-1.5">
                    <span
                        id="sidebar-conversations-heading"
                        className="text-xs font-semibold uppercase tracking-wide text-muted-foreground"
                    >
                        {ariaLabel}
                    </span>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6"
                                onClick={() => setOrder((prev) => (prev === "desc" ? "asc" : "desc"))}
                                aria-label={
                                    order === "desc"
                                        ? "Sort oldest first"
                                        : "Sort newest first"
                                }
                            >
                                <ArrowDownUp className="h-3.5 w-3.5" aria-hidden="true" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent side="bottom">
                            {order === "desc" ? "Newest first" : "Oldest first"}
                        </TooltipContent>
                    </Tooltip>
                </div>
            )}

            <div
                ref={scrollContainerRef}
                role="list"
                aria-label={ariaLabel}
                className="sidebar-scrollbar flex-1 space-y-0.5 overflow-y-auto pr-1"
            >
                {isLoading ? (
                    <div className="space-y-1.5 px-2 py-2">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <Skeleton key={i} className="h-7 w-full" />
                        ))}
                    </div>
                ) : conversations && conversations.length > 0 ? (
                    conversations.map((conversation) => (
                        <SidebarConversationItem
                            key={conversation.id}
                            conversation={conversation}
                            isActive={conversation.id === activeId}
                            compact={compact}
                            onNavigate={onNavigate}
                        />
                    ))
                ) : (
                    <p className="px-3 py-4 text-xs text-muted-foreground">{emptyMessage}</p>
                )}
                {!items && conversations && conversations.length > 0 && (
                    <div ref={loadMoreRef} aria-hidden="true" className="h-4 w-full" data-testid="sidebar-load-more-sentinel" />
                )}
                {!items && isFetchingNextPage && (
                    <div className="space-y-1.5 px-2 py-2" data-testid="sidebar-loading-more">
                        {Array.from({ length: 2 }).map((_, i) => (
                            <Skeleton key={i} className="h-7 w-full" />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function SidebarConversationItem({
    conversation,
    isActive,
    compact,
    onNavigate,
}: {
    conversation: Conversation;
    isActive: boolean;
    compact: boolean;
    onNavigate?: () => void;
}) {
    const title = conversation.title?.trim() || "[Untitled]";
    const dateLabel = formatDate(conversation.create_time);
    const tooltipSummary = `${conversation.message_count} ${conversation.message_count === 1 ? "message" : "messages"}`;

    return (
        <Tooltip>
            <TooltipTrigger asChild>
                <Link
                    href={`/conversation/${conversation.id}`}
                    onClick={() => onNavigate?.()}
                    aria-current={isActive ? "page" : undefined}
                    className={cn(
                        "group/item relative flex flex-col gap-0.5 rounded-md px-2.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                        compact ? "py-1" : "py-1.5",
                        isActive
                            ? "bg-primary/10 text-primary"
                            : "text-foreground hover:bg-muted/60"
                    )}
                >
                    <span className="flex items-center gap-1.5">
                        {conversation.is_favorite && (
                            <Star className="h-3 w-3 shrink-0 fill-yellow-500 text-yellow-500" aria-label="Favourite" />
                        )}
                        <MessageSquare
                            className="h-3 w-3 shrink-0 text-muted-foreground/60 group-hover/item:text-muted-foreground"
                            aria-hidden="true"
                        />
                        <span className="flex-1 truncate text-[13px] font-medium leading-snug">
                            {title}
                        </span>
                    </span>
                    <span
                        className="ml-4.5 truncate text-[10.5px] text-muted-foreground/80 opacity-0 transition-opacity group-hover/item:opacity-100 group-focus-visible/item:opacity-100"
                        aria-hidden="true"
                    >
                        {dateLabel} · {conversation.message_count} msgs
                    </span>
                </Link>
            </TooltipTrigger>
            <TooltipContent side="right" align="start" className="max-w-64">
                <div className="space-y-1">
                    <div className="text-[12px] font-semibold leading-snug">{title}</div>
                    <div className="text-[11px] text-background/80">{dateLabel} · {tooltipSummary}</div>
                    {conversation.model && (
                        <div className="text-[11px] text-background/70">Model: {conversation.model}</div>
                    )}
                    {conversation.is_favorite && (
                        <div className="text-[11px] text-background/70">Favorited conversation</div>
                    )}
                </div>
            </TooltipContent>
        </Tooltip>
    );
}
