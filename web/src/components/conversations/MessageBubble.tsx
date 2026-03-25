import type { ReactNode } from "react";
import type { Message } from "@/types";
import { User, Bot, Terminal } from "lucide-react";

import { AttachmentAudio } from "@/components/conversations/AttachmentAudio";
import { AttachmentFile } from "@/components/conversations/AttachmentFile";
import { AttachmentImage } from "@/components/conversations/AttachmentImage";

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

const roleColors = {
    user: "bg-blue-50 dark:bg-blue-950/30",
    assistant: "bg-gray-50 dark:bg-gray-900/30",
    system: "bg-yellow-50 dark:bg-yellow-950/30",
    tool: "bg-purple-50 dark:bg-purple-950/30",
};

const roleLabels = {
    user: "You",
    assistant: "Assistant",
    system: "System",
    tool: "Tool",
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

function renderContent(message: Message): ReactNode {
    if (!message.content && message.attachments.length === 0) {
        return <span className="italic text-muted-foreground">[No content]</span>;
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

export function MessageBubble({ message }: { message: Message }) {
    const Icon = roleIcons[message.role] || Terminal;
    const bgColor = roleColors[message.role] || roleColors.system;
    const label = roleLabels[message.role] || message.role;

    return (
        <div className={`flex gap-3 rounded-lg p-4 ${bgColor}`} data-testid="message">
            <div className="mt-0.5 shrink-0">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-muted">
                    <Icon className="h-4 w-4" />
                </div>
            </div>
            <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center gap-2">
                    <span className="text-sm font-semibold">{label}</span>
                    {message.create_time && (
                        <span className="text-xs text-muted-foreground">
                            {formatTime(message.create_time)}
                        </span>
                    )}
                </div>
                <div className="prose prose-sm max-w-none space-y-3 dark:prose-invert">
                    {renderContent(message)}
                </div>
            </div>
        </div>
    );
}
