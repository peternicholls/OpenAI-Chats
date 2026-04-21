"use client";

import { useState, type ReactNode } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import { cn } from "@/lib/utils";

interface ExpandableInfoBlockProps {
    testId: string;
    label: string;
    details: string;
    icon: ReactNode;
    collapsedClassName: string;
    expandedClassName?: string;
    buttonClassName: string;
    detailsClassName: string;
    ariaLabel: string;
}

export function ExpandableInfoBlock({
    testId,
    label,
    details,
    icon,
    collapsedClassName,
    expandedClassName,
    buttonClassName,
    detailsClassName,
    ariaLabel,
}: ExpandableInfoBlockProps) {
    const [expanded, setExpanded] = useState(false);

    return (
        <div
            data-testid={testId}
            className={cn(
                "rounded-md text-[12.5px] font-medium",
                expanded ? "flex w-full flex-col" : "inline-flex flex-col",
                collapsedClassName,
                expandedClassName
            )}
        >
            <button
                type="button"
                onClick={() => setExpanded((prev) => !prev)}
                className={cn("flex items-center gap-1.5 px-3 py-1 transition-colors", buttonClassName)}
                aria-label={ariaLabel}
                aria-expanded={expanded}
            >
                {icon}
                {label}
                {expanded ? (
                    <ChevronUp className="h-3 w-3 shrink-0" />
                ) : (
                    <ChevronDown className="h-3 w-3 shrink-0" />
                )}
            </button>
            {expanded && <p className={detailsClassName}>{details}</p>}
        </div>
    );
}
