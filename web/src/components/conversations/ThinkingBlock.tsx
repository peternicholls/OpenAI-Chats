"use client";

import { CircleHelp } from "lucide-react";

import { ExpandableInfoBlock } from "@/components/conversations/ExpandableInfoBlock";

const activityLabels = {
    reasoning: "Reasoning",
    search: "Searched the web",
    both: "Reasoning and web search",
} as const;

export type ActivityType = keyof typeof activityLabels;

export function ThinkingBlock({ activityType }: { activityType: ActivityType }) {
    const label = activityLabels[activityType] ?? activityLabels.reasoning;

    return (
        <ExpandableInfoBlock
            testId="thinking-block"
            label={label}
            details="Detailed reasoning content is not included in the ChatGPT export format."
            icon={<CircleHelp className="h-3.5 w-3.5 shrink-0" />}
            collapsedClassName="bg-muted text-muted-foreground"
            buttonClassName="hover:text-foreground"
            detailsClassName="px-3 pb-2.5 pt-0 text-[12.5px] italic leading-relaxed text-muted-foreground/75"
            ariaLabel={`Toggle ${label.toLowerCase()} details`}
        />
    );
}
