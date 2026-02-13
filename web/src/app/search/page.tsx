"use client";

import { Suspense, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { useSearch } from "@/hooks/useSearch";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Pagination } from "@/components/common/Pagination";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Search, Clock, MessageSquare } from "lucide-react";
import type { SearchType } from "@/types";
import Link from "next/link";

const PAGE_SIZE = 20;

function SearchContent() {
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get("q") || "";

    const [inputValue, setInputValue] = useState(initialQuery);
    const [query, setQuery] = useState(initialQuery);
    const [searchType, setSearchType] = useState<SearchType>("keyword");
    const [offset, setOffset] = useState(0);

    const { data, isLoading, error } = useSearch({
        query,
        searchType,
        limit: PAGE_SIZE,
        offset,
        enabled: !!query,
    });

    const handleSubmit = useCallback(
        (e: React.FormEvent) => {
            e.preventDefault();
            if (inputValue.trim()) {
                setQuery(inputValue.trim());
                setOffset(0);
            }
        },
        [inputValue]
    );

    return (
        <>
            <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Search conversations and messages..."
                        className="pl-9"
                    />
                </div>
                <Select
                    value={searchType}
                    onValueChange={(v) => {
                        setSearchType(v as SearchType);
                        setOffset(0);
                    }}
                >
                    <SelectTrigger className="w-35">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="keyword">Keyword</SelectItem>
                        <SelectItem value="semantic">Semantic</SelectItem>
                        <SelectItem value="hybrid">Hybrid</SelectItem>
                    </SelectContent>
                </Select>
                <Button type="submit">Search</Button>
            </form>

            {!query ? (
                <div className="flex flex-col items-center justify-center min-h-[40vh] text-center">
                    <Search className="h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-lg text-muted-foreground">
                        Enter a search query to find conversations
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                        Search through your conversation history by keyword or semantic meaning
                    </p>
                </div>
            ) : isLoading ? (
                <LoadingSpinner className="min-h-[40vh]" />
            ) : error ? (
                <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4">
                    <p className="text-destructive">Search failed</p>
                    <p className="text-sm text-muted-foreground">{(error as Error).message}</p>
                </div>
            ) : data && data.items.length > 0 ? (
                <>
                    <p className="text-sm text-muted-foreground mb-4">
                        {data.total} result{data.total !== 1 ? "s" : ""} for &quot;{query}&quot;
                    </p>
                    <div className="grid gap-3">
                        {data.items.map((result) => (
                            <Link
                                key={result.conversation_id}
                                href={`/conversation/${result.conversation_id}`}
                            >
                                <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
                                    <CardContent className="p-4">
                                        <h3 className="font-medium">
                                            {result.title || "Untitled Conversation"}
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
                                            {result.preview}
                                        </p>
                                    </CardContent>
                                </Card>
                            </Link>
                        ))}
                    </div>
                    <Pagination
                        total={data.total}
                        offset={data.offset}
                        limit={data.limit}
                        onPageChange={setOffset}
                    />
                </>
            ) : (
                <div className="flex flex-col items-center justify-center min-h-[40vh] text-center">
                    <p className="text-lg text-muted-foreground">No results found</p>
                    <p className="text-sm text-muted-foreground mt-1">
                        Try a different search term or search type
                    </p>
                </div>
            )}
        </>
    );
}

export default function SearchPage() {
    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Search</h1>
            <Suspense fallback={<LoadingSpinner className="min-h-[40vh]" />}>
                <SearchContent />
            </Suspense>
        </div>
    );
}
