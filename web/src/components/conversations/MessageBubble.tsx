"use client";

import { useState } from "react";
import type { ReactNode } from "react";
import type { Message, RenderSegment } from "@/types";

import { Bot, Terminal, User } from "lucide-react";

import { AttachmentAudio } from "@/components/conversations/AttachmentAudio";
import { AttachmentFile } from "@/components/conversations/AttachmentFile";
import { AttachmentImage } from "@/components/conversations/AttachmentImage";
import { FallbackBlock } from "@/components/conversations/FallbackBlock";
import { MarkdownRenderer } from "@/components/conversations/MarkdownRenderer";
import { ThinkingBlock } from "@/components/conversations/ThinkingBlock";
import { TurnActions } from "@/components/conversations/TurnActions";
import {
    getCollapsedUserPromptText,
    getMessageRawText,
    shouldCollapseLongUserPrompt,
} from "@/components/conversations/turnContent";

const ATTACHMENT_TOKEN_RE = /\[\[ATTACHMENT:(\d+)\]\]/g;

function formatTime(timestamp: number | null): string {
    if (!timestamp) return "";
    return new Date(timestamp * 1000).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

const roleIcons = {
    user: User,
    assistant: Bot,
    system: Terminal,
    tool: Terminal,
};
const roleLabels = {
    user: "You",
    assistant: "Assistant",
    system: "System",
    tool: "Tool",
};

const roleBubbleColors = {
    user: "bg-blue-50 dark:bg-blue-950/20",
    assistant: "bg-gray-50 dark:bg-gray-900/20",
    system: "bg-yellow-50/60 dark:bg-yellow-950/10",
    tool: "bg-violet-50/60 dark:bg-violet-950/10",
};

const roleIconColors = {
    user: "bg-blue-200 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300",
    assistant: "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
    system: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
    tool: "bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300",
};

const plainTextBodyClassName = "whitespace-pre-wrap wrap-break-word text-[14px] leading-[1.55] text-foreground";

function renderAttachment(message: Message, index: number): ReactNode {
    const attachment = message.attachments[index];
    if (!attachment) {
        return null;
    }

    if (attachment.type === "image") {
        return <AttachmentImage attachment={attachment} />;
    }
    if (attachment.type === "audio") {
        return <AttachmentAudio attachment={attachment} />;
    }
    return <AttachmentFile attachment={attachment} />;
}

type RenderedPart =
    | { kind: "node"; node: ReactNode; key: string }
    | { kind: "attachment"; attachmentIndex: number; key: string };

function renderAttachmentGroup(message: Message, attachmentIndexes: number[], key: string): ReactNode {
    return (
        <div key={key} className="flex flex-wrap gap-3" data-testid="attachment-inline-group">
            {attachmentIndexes.map((attachmentIndex) => (
                <div key={`attachment-group-${attachmentIndex}`}>
                    {renderAttachment(message, attachmentIndex)}
                </div>
            ))}
        </div>
    );
}

function coalesceRenderedParts(message: Message, parts: RenderedPart[]): ReactNode[] {
    const coalesced: ReactNode[] = [];
    let pendingImageIndexes: number[] = [];
    let pendingGroupKey: string | null = null;

    const flushPendingImages = () => {
        if (pendingImageIndexes.length === 0 || pendingGroupKey === null) {
            return;
        }

        coalesced.push(renderAttachmentGroup(message, pendingImageIndexes, pendingGroupKey));
        pendingImageIndexes = [];
        pendingGroupKey = null;
    };

    for (const part of parts) {
        if (part.kind === "attachment" && message.attachments[part.attachmentIndex]?.type === "image") {
            pendingImageIndexes.push(part.attachmentIndex);
            pendingGroupKey ??= part.key;
            continue;
        }

        flushPendingImages();

        if (part.kind === "attachment") {
            coalesced.push(
                <div key={part.key}>
                    {renderAttachment(message, part.attachmentIndex)}
                </div>
            );
            continue;
        }

        coalesced.push(part.node);
    }

    flushPendingImages();
    return coalesced;
}

function renderLegacyContent(message: Message, textOverride?: string | null): ReactNode {
    if (!message.content && message.attachments.length === 0) {
        return <span className="text-sm italic text-muted-foreground">[No content]</span>;
    }

    const content = textOverride ?? message.content ?? "";
    const parts = content.split(ATTACHMENT_TOKEN_RE);
    const renderedParts: RenderedPart[] = [];
    const renderedAttachmentIndexes = new Set<number>();

    for (let index = 0; index < parts.length; index += 1) {
        const value = parts[index];
        if (!value) {
            continue;
        }

        if (index % 2 === 1) {
            const attachmentIndex = Number.parseInt(value, 10);
            renderedAttachmentIndexes.add(attachmentIndex);
            renderedParts.push({
                kind: "attachment",
                attachmentIndex,
                key: `attachment-${attachmentIndex}`,
            });
            continue;
        }

        renderedParts.push({
            kind: "node",
            key: `text-${index}`,
            node: (
                <div key={`text-${index}`} className={plainTextBodyClassName}>
                    {value}
                </div>
            ),
        });
    }

    if (message.attachments.length > 0 && renderedParts.length === 0) {
        return coalesceRenderedParts(
            message,
            message.attachments.map((_attachment, index) => ({
                kind: "attachment" as const,
                attachmentIndex: index,
                key: `attachment-only-${index}`,
            }))
        );
    }

    const trailingAttachments = message.attachments
        .map((attachment, index) => ({ attachment, index }))
        .filter(({ index }) => !renderedAttachmentIndexes.has(index));

    const rendered = coalesceRenderedParts(message, renderedParts);
    const trailingAttachmentParts: RenderedPart[] = trailingAttachments.map(({ index }) => ({
        kind: "attachment",
        attachmentIndex: index,
        key: `attachment-trailing-${index}`,
    }));

    return (
        <>
            {rendered}
            {coalesceRenderedParts(message, trailingAttachmentParts)}
        </>
    );
}

function renderSegmentPart(message: Message, segment: RenderSegment, index: number): RenderedPart {
    if (segment.kind === "thinking") {
        // ThinkingBlocks are only meaningful on assistant turns; guard against
        // backend-emitted thinking segments leaking onto user/system messages.
        return {
            kind: "node",
            key: `segment-thinking-${index}`,
            node: message.role !== "assistant"
                ? null
                : <ThinkingBlock key={`segment-thinking-${index}`} activityType={segment.activity_type} />,
        };
    }

    if (segment.kind === "markdown") {
        return {
            kind: "node",
            key: `segment-markdown-${index}`,
            node: <MarkdownRenderer key={`segment-markdown-${index}`} text={segment.text} />,
        };
    }

    if (segment.kind === "attachment") {
        if (!message.attachments[segment.attachment_index]) {
            return {
                kind: "node",
                key: `segment-missing-attachment-${index}`,
                node: (
                    <FallbackBlock
                        key={`segment-missing-attachment-${index}`}
                        label="Missing attachment"
                        text={`Attachment index ${segment.attachment_index} is not available in this message.`}
                    />
                ),
            };
        }

        return {
            kind: "attachment",
            attachmentIndex: segment.attachment_index,
            key: `segment-attachment-${index}`,
        };
    }

    return {
        kind: "node",
        key: `segment-fallback-${index}`,
        node: (
            <FallbackBlock
                key={`segment-fallback-${index}`}
                label={segment.fallback_label}
                text={segment.text}
            />
        ),
    };
}

function renderContent(message: Message, textOverride?: string | null): ReactNode {
    if (message.segments && message.segments.length > 0) {
        return coalesceRenderedParts(
            message,
            message.segments.map((segment, index) => renderSegmentPart(message, segment, index))
        );
    }

    return renderLegacyContent(message, textOverride);
}

export function MessageBubble({
    message,
    enableLongPromptTruncation = true,
}: {
    message: Message;
    enableLongPromptTruncation?: boolean;
}) {
    const Icon = roleIcons[message.role] || Terminal;
    const iconColor = roleIconColors[message.role] || roleIconColors.system;
    const label = roleLabels[message.role] || message.role;
    const bubbleColor = roleBubbleColors[message.role] || roleBubbleColors.assistant;
    const rawTurnText = getMessageRawText(message);
    // Allow truncation for user messages with no attachments, whether they have
    // segments or not — real messages always carry a single markdown segment.
    const isTextOnlyUserMessage =
        message.role === "user" &&
        message.attachments.length === 0 &&
        (!message.segments || message.segments.every((s) => s.kind === "markdown"));
    const collapsibleLongPrompt =
        isTextOnlyUserMessage &&
        shouldCollapseLongUserPrompt(message, enableLongPromptTruncation);
    const [isExpanded, setIsExpanded] = useState(false);
    const displayText = getCollapsedUserPromptText(rawTurnText);
    const renderedBody =
        collapsibleLongPrompt && !isExpanded ? (
            <div className={plainTextBodyClassName}>{displayText}</div>
        ) : (
            renderContent(message)
        );

    return (
        <div
            className={`flex gap-3 rounded-lg p-3 ${bubbleColor}`}
            data-testid="message"
        >
            <div className="mt-0.5 shrink-0">
                <div className={`flex h-7 w-7 items-center justify-center rounded-full ${iconColor}`}>
                    <Icon className="h-3.5 w-3.5" />
                </div>
            </div>
            <div className="min-w-0 flex-1">
                <div className="mb-2 flex items-baseline gap-2">
                    <span className="text-sm font-semibold text-foreground">{label}</span>
                    {message.create_time && (
                        <time
                            className="text-xs text-muted-foreground/70"
                            dateTime={new Date(message.create_time * 1000).toISOString()}
                        >
                            {formatTime(message.create_time)}
                        </time>
                    )}
                </div>
                <div className="space-y-3">
                    {renderedBody}
                </div>
                {collapsibleLongPrompt && (
                    <div className="mt-3">
                        <button
                            type="button"
                            className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                            onClick={() => setIsExpanded((current) => !current)}
                        >
                            {isExpanded ? "Show less" : "Read more"}
                        </button>
                    </div>
                )}
                <div className="mt-3 flex justify-end">
                    <TurnActions text={rawTurnText} />
                </div>
            </div>
        </div>
    );
}
