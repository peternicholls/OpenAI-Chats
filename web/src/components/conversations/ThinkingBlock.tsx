"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, CircleHelp } from "lucide-react";

const activityLabels = {
    reasoning: "Reasoning",
    search: "Searched the web",
    both: "Reasoning and web search",
} as const;

export type ActivityType = keyof typeof activityLabels;

export function ThinkingBlock({ activityType }: { activityType: ActivityType }) {
    const [expanded, setExpanded] = useState(false);
    const label = activityLabels[activityType] ?? activityLabels.reasoning;

    return (
        <div
            data-testid="thinking-block"
            className={`rounded-md bg-muted text-[12.5px] font-medium text-muted-foreground ${expanded ? "flex w-full flex-col" : "inline-flex flex-col"
                }`}
        >
            <button
                type="button"
                onClick={() => setExpanded((prev) => !prev)}
                className="flex items-center gap-1.5 px-3 py-1 transition-colors hover:text-foreground"
            >
                <CircleHelp className="h-3.5 w-3.5 shrink-0" />
                {label}
                {expanded ? (
                    <ChevronUp className="h-3 w-3 shrink-0" />
                ) : (
                    <ChevronDown className="h-3 w-3 shrink-0" />
                )}
            </button>
            {expanded && (
                <p className="px-3 pb-2.5 pt-0 text-[12.5px] italic leading-relaxed text-muted-foreground/75">
                    Detailed reasoning content is not included in the ChatGPT export format.
                </p>
            )}
        </div>
    );
}
