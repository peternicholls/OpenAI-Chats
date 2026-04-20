import type { ReactNode } from "react";
import type { Message, RenderSegment } from "@/types";

import { Bot } from "lucide-react";

import { AttachmentAudio } from "@/components/conversations/AttachmentAudio";
import { AttachmentFile } from "@/components/conversations/AttachmentFile";
import { AttachmentImage } from "@/components/conversations/AttachmentImage";
import { FallbackBlock } from "@/components/conversations/FallbackBlock";
import { MarkdownRenderer } from "@/components/conversations/MarkdownRenderer";
import { ThinkingBlock } from "@/components/conversations/ThinkingBlock";
import { TurnActions } from "@/components/conversations/TurnActions";
import { ToolBlock } from "@/components/conversations/ToolBlock";
import { getTurnRawText } from "@/components/conversations/turnContent";

function formatTime(timestamp: number | null): string {
    if (!timestamp) return "";
    return new Date(timestamp * 1000).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

function renderSegment(message: Message, segment: RenderSegment, index: number): ReactNode {
    if (segment.kind === "thinking") {
        return <ThinkingBlock key={`seg-thinking-${index}`} activityType={segment.activity_type} />;
    }

    if (segment.kind === "markdown") {
        return <MarkdownRenderer key={`seg-markdown-${index}`} text={segment.text} />;
    }

    if (segment.kind === "attachment") {
        const attachment = message.attachments[segment.attachment_index];
        if (!attachment) {
            return (
                <FallbackBlock
                    key={`seg-attachment-missing-${index}`}
                    label="Missing attachment"
                    text={`Attachment index ${segment.attachment_index} is not available in this message.`}
                />
            );
        }
        const node =
            attachment.type === "image" ? (
                <AttachmentImage attachment={attachment} />
            ) : attachment.type === "audio" ? (
                <AttachmentAudio attachment={attachment} />
            ) : (
                <AttachmentFile attachment={attachment} />
            );
        return <div key={`seg-attachment-${index}`}>{node}</div>;
    }

    return (
        <FallbackBlock
            key={`seg-fallback-${index}`}
            label={segment.fallback_label}
            text={segment.text}
        />
    );
}

function renderMessageContribution(message: Message): ReactNode {
    // Assistant with segments — render them (ThinkingBlocks + markdown + attachments)
    if (message.segments && message.segments.length > 0) {
        return (
            <div className="space-y-3">
                {message.segments.map((segment, i) => renderSegment(message, segment, i))}
            </div>
        );
    }

    // Assistant with plain text content (legacy path)
    if (message.content) {
        return <MarkdownRenderer text={message.content} />;
    }

    // Empty assistant message — show a reasoning pill (content not in export format)
    return <ThinkingBlock activityType="reasoning" />;
}

function buildTurnPieces(messages: Message[]): Array<{ id: string; node: ReactNode }> {
    const pieces: Array<{ id: string; node: ReactNode }> = [];
    let toolClusterCount = 0;
    let toolClusterStartId: string | null = null;

    const flushToolCluster = () => {
        if (toolClusterCount === 0 || !toolClusterStartId) {
            return;
        }

        pieces.push({
            id: `tool-cluster-${toolClusterStartId}`,
            node: <ToolBlock count={toolClusterCount} />,
        });
        toolClusterCount = 0;
        toolClusterStartId = null;
    };

    for (const message of messages) {
        if (message.role === "tool") {
            toolClusterCount += 1;
            toolClusterStartId ??= message.id;
            continue;
        }

        flushToolCluster();
        pieces.push({ id: message.id, node: renderMessageContribution(message) });
    }

    flushToolCluster();
    return pieces;
}

export function AssistantTurn({ messages }: { messages: Message[] }) {
    const timestamp = messages.find((m) => m.create_time)?.create_time ?? null;
    const rawTurnText = getTurnRawText(messages);
    const pieces = buildTurnPieces(messages);

    if (pieces.length === 0) return null;

    return (
        <div
            className="flex gap-3 rounded-lg p-3 bg-gray-50 dark:bg-gray-900/20"
            data-testid="message"
        >
            <div className="mt-0.5 shrink-0">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                    <Bot className="h-3.5 w-3.5" />
                </div>
            </div>
            <div className="min-w-0 flex-1">
                <div className="mb-2 flex items-baseline gap-2">
                    <span className="text-sm font-semibold text-foreground">Assistant</span>
                    {timestamp && (
                        <time
                            className="text-xs text-muted-foreground/70"
                            dateTime={new Date(timestamp * 1000).toISOString()}
                        >
                            {formatTime(timestamp)}
                        </time>
                    )}
                </div>
                <div className="space-y-3">
                    {pieces.map((p) => (
                        <div key={p.id}>{p.node}</div>
                    ))}
                </div>
                <div className="mt-3 flex justify-end">
                    <TurnActions text={rawTurnText} />
                </div>
            </div>
        </div>
    );
}
