"use client";

import { useState } from "react";
import { format } from "date-fns";
import { CalendarIcon, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import type { SearchType } from "@/types";

interface SearchFiltersProps {
    searchType: SearchType;
    onSearchTypeChange: (type: SearchType) => void;
    fromDate?: Date;
    toDate?: Date;
    onFromDateChange: (date: Date | undefined) => void;
    onToDateChange: (date: Date | undefined) => void;
}

export function SearchFilters({
    searchType,
    onSearchTypeChange,
    fromDate,
    toDate,
    onFromDateChange,
    onToDateChange,
}: SearchFiltersProps) {
    const [fromOpen, setFromOpen] = useState(false);
    const [toOpen, setToOpen] = useState(false);

    return (
        <div className="flex flex-wrap items-center gap-2">
            {/* Search Type Selector */}
            <Select
                value={searchType}
                onValueChange={(v) => onSearchTypeChange(v as SearchType)}
            >
                <SelectTrigger className="w-32">
                    <SelectValue placeholder="Search type" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="keyword">Keyword</SelectItem>
                    <SelectItem value="semantic">Semantic</SelectItem>
                    <SelectItem value="hybrid">Hybrid</SelectItem>
                </SelectContent>
            </Select>

            {/* From Date Picker */}
            <Popover open={fromOpen} onOpenChange={setFromOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        className={cn(
                            "w-36 justify-start text-left font-normal",
                            !fromDate && "text-muted-foreground"
                        )}
                    >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {fromDate ? format(fromDate, "MMM d, yyyy") : "From date"}
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                        mode="single"
                        selected={fromDate}
                        onSelect={(date) => {
                            onFromDateChange(date);
                            setFromOpen(false);
                        }}
                        disabled={(date) =>
                            date > new Date() || (toDate ? date > toDate : false)
                        }
                        initialFocus
                    />
                </PopoverContent>
            </Popover>

            {/* To Date Picker */}
            <Popover open={toOpen} onOpenChange={setToOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        className={cn(
                            "w-36 justify-start text-left font-normal",
                            !toDate && "text-muted-foreground"
                        )}
                    >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {toDate ? format(toDate, "MMM d, yyyy") : "To date"}
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                        mode="single"
                        selected={toDate}
                        onSelect={(date) => {
                            onToDateChange(date);
                            setToOpen(false);
                        }}
                        disabled={(date) =>
                            date > new Date() || (fromDate ? date < fromDate : false)
                        }
                        initialFocus
                    />
                </PopoverContent>
            </Popover>

            {/* Clear Dates Button */}
            {(fromDate || toDate) && (
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                        onFromDateChange(undefined);
                        onToDateChange(undefined);
                    }}
                    className="h-9 px-2"
                >
                    <X className="h-4 w-4 mr-1" />
                    Clear dates
                </Button>
            )}
        </div>
    );
}
