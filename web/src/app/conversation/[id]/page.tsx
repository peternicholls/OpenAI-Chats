"use client";

import { useParams, useRouter } from "next/navigation";
import { useConversation } from "@/hooks/useConversations";
import { ConversationHeader } from "@/components/conversations/ConversationHeader";
import { AssistantTurn } from "@/components/conversations/AssistantTurn";
import { MessageBubble } from "@/components/conversations/MessageBubble";
import { DateSeparator } from "@/components/conversations/DateSeparator";
import type { Message } from "@/types";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ExportDialog } from "@/components/export/ExportDialog";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useState } from "react";
import { api } from "@/services/api";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queryKeys";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

type MessageTurn =
    | { type: "user-or-system"; message: Message }
    | { type: "assistant"; messages: Message[] };

function groupIntoTurns(messages: Message[]): MessageTurn[] {
    const turns: MessageTurn[] = [];
    let buffer: Message[] = [];

    for (const message of messages) {
        if (message.role === "user" || message.role === "system") {
            if (buffer.length > 0) {
                turns.push({ type: "assistant", messages: buffer });
                buffer = [];
            }
            turns.push({ type: "user-or-system", message });
        } else {
            buffer.push(message);
        }
    }

    if (buffer.length > 0) {
        turns.push({ type: "assistant", messages: buffer });
    }

    return turns;
}

export default function ConversationDetailPage() {
    const params = useParams();
    const router = useRouter();
    const queryClient = useQueryClient();
    const id = params.id as string;

    const { data: conversation, isLoading, error, refetch } = useConversation(id);
    const [showExport, setShowExport] = useState(false);
    const [showDelete, setShowDelete] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const handleToggleFavorite = async () => {
        try {
            const result = await api.toggleFavorite(id);
            queryClient.setQueryData(queryKeys.conversations.detail(id), (current: unknown) => {
                if (!current || typeof current !== "object") return current;
                return { ...(current as Record<string, unknown>), is_favorite: result.is_favorite };
            });
            queryClient.invalidateQueries({ queryKey: queryKeys.conversations.all });
            queryClient.invalidateQueries({ queryKey: queryKeys.favorites.all });
            toast.success(result.is_favorite ? "Added to favorites" : "Removed from favorites");
        } catch {
            toast.error("Failed to update favorite");
        }
    };

    const handleDelete = async () => {
        setIsDeleting(true);
        try {
            await api.deleteConversation(id);
            queryClient.invalidateQueries({ queryKey: queryKeys.conversations.all });
            toast.success("Conversation deleted");
            router.push("/");
        } catch {
            toast.error("Failed to delete conversation");
            setIsDeleting(false);
        }
    };

    if (isLoading) return <LoadingSpinner className="min-h-[50vh]" />;

    if (error || !conversation) {
        const message = (error as Error | undefined)?.message || "Conversation not found";
        const normalized = message.toLowerCase();
        const isNetworkError = normalized.includes("fetch") || normalized.includes("network");
        const isNotFound = normalized.includes("404") || normalized.includes("not found") || !conversation;

        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
                <p className="text-destructive">
                    {isNetworkError
                        ? "Network error while loading conversation"
                        : isNotFound
                            ? "Conversation not found"
                            : "Failed to load conversation"}
                </p>
                <p className="text-sm text-muted-foreground text-center max-w-md">{message}</p>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => router.push("/")}>
                        Back to conversations
                    </Button>
                    <Button onClick={() => refetch()}>Retry</Button>
                </div>
            </div>
        );
    }

    return (
        <article className="mx-auto max-w-4xl">
            <ConversationHeader
                conversation={conversation}
                onExport={() => setShowExport(true)}
                onDelete={() => setShowDelete(true)}
                onToggleFavorite={handleToggleFavorite}
                isFavorite={conversation.is_favorite}
            />

            <section className="flex flex-col gap-2">
                {groupIntoTurns(conversation.messages).map((turn, index, turns) => {
                    const elements: React.ReactNode[] = [];

                    const turnTime =
                        turn.type === "user-or-system"
                            ? turn.message.create_time
                            : (turns[index] as { type: "assistant"; messages: Message[] }).messages.find(
                                (m) => m.create_time
                            )?.create_time ?? null;

                    // Insert DateSeparator when calendar date changes between turns
                    if (index > 0 && turnTime) {
                        const prevTurn = turns[index - 1];
                        const prevTime =
                            prevTurn.type === "user-or-system"
                                ? prevTurn.message.create_time
                                : (prevTurn as { type: "assistant"; messages: Message[] }).messages
                                    .filter((m) => m.create_time)
                                    .at(-1)?.create_time ?? null;

                        if (prevTime) {
                            const currentDate = new Date(turnTime * 1000);
                            const prevDate = new Date(prevTime * 1000);
                            const dateChanged =
                                currentDate.getFullYear() !== prevDate.getFullYear() ||
                                currentDate.getMonth() !== prevDate.getMonth() ||
                                currentDate.getDate() !== prevDate.getDate();
                            if (dateChanged) {
                                const sepKey =
                                    turn.type === "user-or-system"
                                        ? `date-${turn.message.id}`
                                        : `date-${(turn as { type: "assistant"; messages: Message[] }).messages[0].id}`;
                                elements.push(<DateSeparator key={sepKey} date={currentDate} />);
                            }
                        }
                    }

                    if (turn.type === "user-or-system") {
                        elements.push(
                            <MessageBubble key={turn.message.id} message={turn.message} />
                        );
                    } else {
                        elements.push(
                            <AssistantTurn
                                key={`assistant-turn-${turn.messages[0].id}`}
                                messages={turn.messages}
                            />
                        );
                    }

                    return elements;
                })}
            </section>

            <ExportDialog
                conversationId={id}
                open={showExport}
                onOpenChange={setShowExport}
            />

            <AlertDialog open={showDelete} onOpenChange={(open) => !isDeleting && setShowDelete(open)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will permanently delete &quot;{conversation.title || "Untitled"}&quot; and all
                            its messages. This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDelete}
                            disabled={isDeleting}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                            {isDeleting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Deleting...
                                </>
                            ) : (
                                "Delete"
                            )}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </article>
    );
}
