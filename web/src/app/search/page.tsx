"use client";

import { Suspense, useState, useCallback, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { format } from "date-fns";
import { useSearch } from "@/hooks/useSearch";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Pagination } from "@/components/common/Pagination";
import { SearchBar, SearchFilters, SearchResults } from "@/components/search";
import { Search } from "lucide-react";
import type { SearchType } from "@/types";

const PAGE_SIZE = 20;

function SearchContent() {
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get("q") || "";

    const [query, setQuery] = useState(initialQuery);
    const [searchType, setSearchType] = useState<SearchType>("keyword");
    const [fromDate, setFromDate] = useState<Date | undefined>(undefined);
    const [toDate, setToDate] = useState<Date | undefined>(undefined);
    const [offset, setOffset] = useState(0);

    // Format dates for API (ISO string format)
    const fromDateStr = useMemo(
        () => (fromDate ? format(fromDate, "yyyy-MM-dd") : undefined),
        [fromDate]
    );
    const toDateStr = useMemo(
        () => (toDate ? format(toDate, "yyyy-MM-dd") : undefined),
        [toDate]
    );

    const { data, isLoading, error } = useSearch({
        query,
        searchType,
        fromDate: fromDateStr,
        toDate: toDateStr,
        limit: PAGE_SIZE,
        offset,
        enabled: !!query,
    });

    const handleSearch = useCallback((newQuery: string) => {
        setQuery(newQuery);
        setOffset(0);
    }, []);

    const handleSearchTypeChange = useCallback((type: SearchType) => {
        setSearchType(type);
        setOffset(0);
    }, []);

    const handleFromDateChange = useCallback((date: Date | undefined) => {
        setFromDate(date);
        setOffset(0);
    }, []);

    const handleToDateChange = useCallback((date: Date | undefined) => {
        setToDate(date);
        setOffset(0);
    }, []);

    return (
        <>
            {/* Search Bar with 500ms debounce */}
            <div className="mb-4">
                <SearchBar
                    initialValue={initialQuery}
                    onSearch={handleSearch}
                    isLoading={isLoading}
                    debounceMs={500}
                />
            </div>

            {/* Filters: Search Type and Date Range */}
            <div className="mb-6">
                <SearchFilters
                    searchType={searchType}
                    onSearchTypeChange={handleSearchTypeChange}
                    fromDate={fromDate}
                    toDate={toDate}
                    onFromDateChange={handleFromDateChange}
                    onToDateChange={handleToDateChange}
                />
            </div>

            {/* Results Area */}
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
                    <SearchResults
                        results={data.items}
                        query={query}
                        total={data.total}
                    />
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
                        Try a different search term, date range, or search type
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
