"use client";

import Link from "next/link";
import Highlighter from "react-highlight-words";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, MessageSquare } from "lucide-react";
import type { SearchResult } from "@/types";

interface SearchResultsProps {
    results: SearchResult[];
    query: string;
    total: number;
}

/**
 * Extracts search words from a query string for highlighting.
 * Splits on whitespace and filters out empty strings.
 */
function getSearchWords(query: string): string[] {
    return query
        .split(/\s+/)
        .map((word) => word.trim())
        .filter((word) => word.length > 0);
}

export function SearchResults({ results, query, total }: SearchResultsProps) {
    const searchWords = getSearchWords(query);

    return (
        <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
                {total} result{total !== 1 ? "s" : ""} for &quot;{query}&quot;
            </p>
            <div className="grid gap-3">
                {results.map((result) => (
                    <Link
                        key={result.conversation_id}
                        href={`/conversation/${result.conversation_id}`}
                    >
                        <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
                            <CardContent className="p-4">
                                <h3 className="font-medium">
                                    <Highlighter
                                        searchWords={searchWords}
                                        autoEscape={true}
                                        textToHighlight={result.title || "Untitled Conversation"}
                                        highlightClassName="bg-yellow-200 dark:bg-yellow-800 dark:text-yellow-100 rounded px-0.5"
                                    />
                                </h3>
                                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                                    {result.create_time && (
                                        <span className="flex items-center gap-1">
                                            <Clock className="h-3 w-3" />
                                            {new Date(result.create_time * 1000).toLocaleDateString()}
                                        </span>
                                    )}
                                    <span className="flex items-center gap-1">
                                        <MessageSquare className="h-3 w-3" />
                                        {result.match_count} match{result.match_count !== 1 ? "es" : ""}
                                    </span>
                                    {result.relevance_score != null && (
                                        <Badge variant="secondary" className="text-xs">
                                            Score: {result.relevance_score.toFixed(2)}
                                        </Badge>
                                    )}
                                </div>
                                <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                                    <Highlighter
                                        searchWords={searchWords}
                                        autoEscape={true}
                                        textToHighlight={result.preview}
                                        highlightClassName="bg-yellow-200 dark:bg-yellow-800 dark:text-yellow-100 rounded px-0.5"
                                    />
                                </p>
                            </CardContent>
                        </Card>
                    </Link>
                ))}
            </div>
        </div>
    );
}
