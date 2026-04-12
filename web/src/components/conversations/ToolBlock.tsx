"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Wrench } from "lucide-react";

export function ToolBlock() {
    const [expanded, setExpanded] = useState(false);

    return (
        <div
            data-testid="tool-block"
            className={`rounded-md bg-violet-100/70 dark:bg-violet-950/20 text-[12.5px] font-medium text-violet-700 dark:text-violet-400 ${expanded ? "flex w-full flex-col" : "inline-flex flex-col"
                }`}
        >
            <button
                type="button"
                onClick={() => setExpanded((prev) => !prev)}
                className="flex items-center gap-1.5 px-3 py-1 transition-colors hover:text-violet-800 dark:hover:text-violet-300"
            >
                <Wrench className="h-3.5 w-3.5 shrink-0" />
                Tool call
                {expanded ? (
                    <ChevronUp className="h-3 w-3 shrink-0" />
                ) : (
                    <ChevronDown className="h-3 w-3 shrink-0" />
                )}
            </button>
            {expanded && (
                <p className="px-3 pb-2.5 pt-0 text-[12.5px] italic leading-relaxed text-violet-600/70 dark:text-violet-400/70">
                    Tool call details are not included in the ChatGPT export format.
                </p>
            )}
        </div>
    );
}
