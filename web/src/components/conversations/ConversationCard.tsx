"use client";

import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Conversation } from "@/types";
import { Star } from "lucide-react";

function formatDate(timestamp: number | null): string {
    if (!timestamp) return "Unknown date";
    return new Date(timestamp * 1000).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

export function ConversationCard({ conversation }: { conversation: Conversation }) {
    return (
        <Link href={`/conversation/${conversation.id}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                        <CardTitle className="text-base font-medium line-clamp-1">
                            {conversation.title || "[Untitled]"}
                        </CardTitle>
                        {conversation.is_favorite && (
                            <Star className="h-4 w-4 text-yellow-500 fill-yellow-500 flex-shrink-0" />
                        )}
                    </div>
                    <CardDescription>
                        {formatDate(conversation.create_time)} &middot;{" "}
                        {conversation.message_count} messages
                        {conversation.model && (
                            <> &middot; {conversation.model}</>
                        )}
                    </CardDescription>
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
