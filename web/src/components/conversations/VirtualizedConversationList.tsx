"use client";

import { useRef, useCallback } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { ConversationCard } from "./ConversationCard";
import type { Conversation } from "@/types";

interface VirtualizedConversationListProps {
    conversations: Conversation[];
    selectable?: boolean;
    selectedIds?: Set<string>;
    onSelectChange?: (id: string, selected: boolean) => void;
    estimatedItemHeight?: number;
}

/**
 * Virtualized conversation list for rendering 5000+ items efficiently.
 * Uses @tanstack/react-virtual for windowing - only renders visible items.
 * Achieves <16ms frame time for smooth scrolling (SC-009 requirement).
 */
export function VirtualizedConversationList({
    conversations,
    selectable = false,
    selectedIds = new Set(),
    onSelectChange,
    estimatedItemHeight = 100,
}: VirtualizedConversationListProps) {
    const parentRef = useRef<HTMLDivElement>(null);

    const virtualizer = useVirtualizer({
        count: conversations.length,
        getScrollElement: () => parentRef.current,
        estimateSize: useCallback(() => estimatedItemHeight, [estimatedItemHeight]),
        overscan: 5, // Render 5 extra items above/below viewport for smooth scrolling
    });

    const items = virtualizer.getVirtualItems();

    return (
        <div
            ref={parentRef}
            className="h-[calc(100vh-200px)] overflow-auto"
            style={{
                contain: "strict", // Performance optimization for layout containment
            }}
        >
            <div
                style={{
                    height: `${virtualizer.getTotalSize()}px`,
                    width: "100%",
                    position: "relative",
                }}
            >
                {items.map((virtualItem) => {
                    const conversation = conversations[virtualItem.index];
                    return (
                        <div
                            key={virtualItem.key}
                            data-index={virtualItem.index}
                            ref={virtualizer.measureElement}
                            style={{
                                position: "absolute",
                                top: 0,
                                left: 0,
                                width: "100%",
                                transform: `translateY(${virtualItem.start}px)`,
                            }}
                        >
                            <div className="pb-3">
                                <ConversationCard
                                    conversation={conversation}
                                    selectable={selectable}
                                    isSelected={selectedIds.has(conversation.id)}
                                    onSelectChange={onSelectChange}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
