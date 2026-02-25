"use client";

import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
    total: number;
    offset: number;
    limit: number;
    onPageChange: (newOffset: number) => void;
}

export function Pagination({ total, offset, limit, onPageChange }: PaginationProps) {
    const currentPage = Math.floor(offset / limit) + 1;
    const totalPages = Math.ceil(total / limit);

    if (totalPages <= 1) return null;

    return (
        <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-muted-foreground">
                Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
            </p>
            <div className="flex items-center gap-2">
                <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage <= 1}
                    onClick={() => onPageChange(Math.max(0, offset - limit))}
                >
                    <ChevronLeft className="h-4 w-4" />
                    Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                    Page {currentPage} of {totalPages}
                </span>
                <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage >= totalPages}
                    onClick={() => onPageChange(offset + limit)}
                >
                    Next
                    <ChevronRight className="h-4 w-4" />
                </Button>
            </div>
        </div>
    );
}
