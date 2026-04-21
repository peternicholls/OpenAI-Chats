"use client";

import { Wrench } from "lucide-react";

import { ExpandableInfoBlock } from "@/components/conversations/ExpandableInfoBlock";

export function ToolBlock({ count = 1 }: { count?: number }) {
    const label = count === 1 ? "Tool call" : `${count} tool calls`;
    const details =
        count === 1
            ? "Tool call details are not included in the ChatGPT export format."
            : `${count} tool calls were grouped here because detailed tool output is not included in the ChatGPT export format.`;

    return (
        <ExpandableInfoBlock
            testId="tool-block"
            label={label}
            details={details}
            icon={<Wrench className="h-3.5 w-3.5 shrink-0" />}
            collapsedClassName="bg-violet-100/70 text-violet-700 dark:bg-violet-950/20 dark:text-violet-400"
            buttonClassName="hover:text-violet-800 dark:hover:text-violet-300"
            detailsClassName="px-3 pb-2.5 pt-0 text-[12.5px] italic leading-relaxed text-violet-600/70 dark:text-violet-400/70"
            ariaLabel={count === 1 ? "Toggle tool call details" : `Toggle ${count} tool call details`}
        />
    );
}
