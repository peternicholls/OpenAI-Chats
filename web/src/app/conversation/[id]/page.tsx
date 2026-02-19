"use client";

import { useParams, useRouter } from "next/navigation";
import { useConversation } from "@/hooks/useConversations";
import { ConversationHeader } from "@/components/conversations/ConversationHeader";
import { MessageBubble } from "@/components/conversations/MessageBubble";
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
import { useState, useEffect } from "react";
import { api } from "@/services/api";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queryKeys";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export default function ConversationDetailPage() {
    const params = useParams();
    const router = useRouter();
    const queryClient = useQueryClient();
    const id = params.id as string;

    const { data: conversation, isLoading, error, refetch } = useConversation(id);
    const [showExport, setShowExport] = useState(false);
    const [showDelete, setShowDelete] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [isFavorite, setIsFavorite] = useState(false);

    // Sync local favorite state with conversation data
    useEffect(() => {
        if (conversation) {
            setIsFavorite(conversation.is_favorite);
        }
    }, [conversation]);

    const handleToggleFavorite = async () => {
        try {
            const result = await api.toggleFavorite(id);
            setIsFavorite(result.is_favorite);
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
        <div className="max-w-4xl mx-auto">
            <ConversationHeader
                conversation={conversation}
                onExport={() => setShowExport(true)}
                onDelete={() => setShowDelete(true)}
                onToggleFavorite={handleToggleFavorite}
                isFavorite={isFavorite}
            />

            <div className="space-y-2">
                {conversation.messages.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                ))}
            </div>

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
        </div>
    );
}
