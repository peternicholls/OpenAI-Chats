import type { ReactNode } from "react";
import type { Message, RenderSegment } from "@/types";

import { Bot, Terminal, User } from "lucide-react";

import { AttachmentAudio } from "@/components/conversations/AttachmentAudio";
import { AttachmentFile } from "@/components/conversations/AttachmentFile";
import { AttachmentImage } from "@/components/conversations/AttachmentImage";
import { FallbackBlock } from "@/components/conversations/FallbackBlock";
import { MarkdownRenderer } from "@/components/conversations/MarkdownRenderer";
import { ThinkingBlock } from "@/components/conversations/ThinkingBlock";

const ATTACHMENT_TOKEN_RE = /\[\[ATTACHMENT:(\d+)\]\]/g;

function formatTime(timestamp: number | null): string {
    if (!timestamp) return "";
    return new Date(timestamp * 1000).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

const roleLabels = {
    user: "You",
    assistant: "Assistant",
    system: "System",
    tool: "Tool",
};

const roleIcons = {
    user: User,
    assistant: Bot,
    system: Terminal,
    tool: Terminal,
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

function renderLegacyContent(message: Message): ReactNode {
    if (!message.content && message.attachments.length === 0) {
        return <span className="text-sm italic text-muted-foreground">[No content]</span>;
    }

    const content = message.content ?? "";
    const parts = content.split(ATTACHMENT_TOKEN_RE);
    const rendered: ReactNode[] = [];
    const renderedAttachmentIndexes = new Set<number>();

    for (let index = 0; index < parts.length; index += 1) {
        const value = parts[index];
        if (!value) {
            continue;
        }

        if (index % 2 === 1) {
            const attachmentIndex = Number.parseInt(value, 10);
            renderedAttachmentIndexes.add(attachmentIndex);
            rendered.push(
                <div key={`attachment-${attachmentIndex}`}>
                    {renderAttachment(message, attachmentIndex)}
                </div>
            );
            continue;
        }

        rendered.push(
            <div key={`text-${index}`} className="whitespace-pre-wrap wrap-break-word">
                {value}
            </div>
        );
    }

    if (message.attachments.length > 0 && rendered.length === 0) {
        return message.attachments.map((_attachment, index) => (
            <div key={`attachment-only-${index}`}>{renderAttachment(message, index)}</div>
        ));
    }

    const trailingAttachments = message.attachments
        .map((attachment, index) => ({ attachment, index }))
        .filter(({ index }) => !renderedAttachmentIndexes.has(index));

    return (
        <>
            {rendered}
            {trailingAttachments.map(({ index }) => (
                <div key={`attachment-trailing-${index}`}>{renderAttachment(message, index)}</div>
            ))}
        </>
    );
}

function renderSegment(message: Message, segment: RenderSegment, index: number): ReactNode {
    if (segment.kind === "thinking") {
        return <ThinkingBlock key={`segment-thinking-${index}`} activityType={segment.activity_type} />;
    }

    if (segment.kind === "markdown") {
        return <MarkdownRenderer key={`segment-markdown-${index}`} text={segment.text} />;
    }

    if (segment.kind === "attachment") {
        if (!message.attachments[segment.attachment_index]) {
            return (
                <FallbackBlock
                    key={`segment-missing-attachment-${index}`}
                    label="Missing attachment"
                    text={`Attachment index ${segment.attachment_index} is not available in this message.`}
                />
            );
        }

        return (
            <div key={`segment-attachment-${index}`}>
                {renderAttachment(message, segment.attachment_index)}
            </div>
        );
    }

    return (
        <FallbackBlock
            key={`segment-fallback-${index}`}
            label={segment.fallback_label}
            text={segment.text}
        />
    );
}

function renderContent(message: Message): ReactNode {
    if (message.segments && message.segments.length > 0) {
        return message.segments.map((segment, index) => renderSegment(message, segment, index));
    }

    return renderLegacyContent(message);
}

export function MessageBubble({ message }: { message: Message }) {
    const Icon = roleIcons[message.role] || Terminal;
    const iconColor = roleIconColors[message.role] || roleIconColors.system;
    const label = roleLabels[message.role] || message.role;

    const bubbleColor = roleBubbleColors[message.role] || roleBubbleColors.assistant;

    return (
        <div className={`flex gap-3 rounded-lg p-3 ${bubbleColor}`} data-testid="message">
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
                    {renderContent(message)}
                </div>
            </div>
        </div>
    );
}
