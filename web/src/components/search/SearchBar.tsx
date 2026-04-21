"use client";

import { useState, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, X, Loader2 } from "lucide-react";
import { useDebounce } from "@/hooks/useDebounce";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface SearchBarProps {
    initialValue?: string;
    onSearch: (query: string) => void;
    isLoading?: boolean;
    placeholder?: string;
    debounceMs?: number;
}

export function SearchBar({
    initialValue = "",
    onSearch,
    isLoading = false,
    placeholder = "Search conversations and messages...",
    debounceMs = 500,
}: SearchBarProps) {
    const [inputValue, setInputValue] = useState(initialValue);
    const debouncedValue = useDebounce(inputValue, debounceMs);

    // Trigger search when debounced value changes
    useEffect(() => {
        onSearch(debouncedValue.trim());
    }, [debouncedValue, onSearch]);

    // Update input when initial value changes externally
    useEffect(() => {
        setInputValue(initialValue);
    }, [initialValue]);

    const handleClear = useCallback(() => {
        setInputValue("");
    }, []);

    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (e.key === "Escape") {
                handleClear();
            }
        },
        [handleClear]
    );

    return (
        <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                className="pl-9 pr-10"
                aria-label="Search"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                {isLoading && (
                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                )}
                {inputValue && !isLoading && (
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={handleClear}
                                aria-label="Clear search"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>Clear search</TooltipContent>
                    </Tooltip>
                )}
            </div>
        </div>
    );
}
