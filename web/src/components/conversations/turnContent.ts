import type { Message } from "@/types";

export const LONG_USER_PROMPT_COLLAPSE_THRESHOLD = 500;

export function getMessageRawText(message: Message): string {
    return message.content ?? "";
}

export function getTurnRawText(messages: Message[]): string {
    return messages
        .map((message) => getMessageRawText(message).trim())
        .filter((text) => text.length > 0)
        .join("\n\n");
}

export function shouldCollapseLongUserPrompt(
    message: Message,
    enabled: boolean,
    threshold = LONG_USER_PROMPT_COLLAPSE_THRESHOLD
): boolean {
    return enabled && message.role === "user" && (message.content?.length ?? 0) > threshold;
}

export function getCollapsedUserPromptText(
    text: string,
    threshold = LONG_USER_PROMPT_COLLAPSE_THRESHOLD
): string {
    return `${text.slice(0, threshold).trimEnd()}...`;
}