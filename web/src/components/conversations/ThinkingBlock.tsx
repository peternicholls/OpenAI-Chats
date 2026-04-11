"use client";

import { useState } from "react";
import { ChevronRight } from "lucide-react";

const activityLabels = {
    reasoning: "Reasoned about this",
    search: "Searched the web",
    both: "Reasoned and searched the web",
} as const;

export type ActivityType = keyof typeof activityLabels;

export function ThinkingBlock({ activityType }: { activityType: ActivityType }) {
    const [expanded, setExpanded] = useState(false);
    const label = activityLabels[activityType] ?? activityLabels.reasoning;

    return (
        <div data-testid="thinking-block">
            <button
                type="button"
                onClick={() => setExpanded((prev) => !prev)}
                className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
                <ChevronRight
                    className={`h-3 w-3 shrink-0 transition-transform duration-200 ${expanded ? "rotate-90" : ""}`}
                />
                {label}
            </button>
            {expanded && (
                <div className="mt-2 rounded-lg border border-border bg-muted/30 px-4 py-3 text-xs leading-5 text-muted-foreground">
                    Detailed reasoning and search content is not included in the ChatGPT export format.
                </div>
            )}
        </div>
    );
}
