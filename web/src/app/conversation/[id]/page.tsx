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
import { useState } from "react";
import { api } from "@/services/api";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queryKeys";
import { toast } from "sonner";

export default function ConversationDetailPage() {
    const params = useParams();
    const router = useRouter();
    const queryClient = useQueryClient();
    const id = params.id as string;

    const { data: conversation, isLoading, error } = useConversation(id);
    const [showExport, setShowExport] = useState(false);
    const [showDelete, setShowDelete] = useState(false);

    const handleDelete = async () => {
        try {
            await api.deleteConversation(id);
            queryClient.invalidateQueries({ queryKey: queryKeys.conversations.all });
            toast.success("Conversation deleted");
            router.push("/");
        } catch {
            toast.error("Failed to delete conversation");
        }
    };

    if (isLoading) return <LoadingSpinner className="min-h-[50vh]" />;

    if (error || !conversation) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
                <p className="text-destructive">Conversation not found</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto">
            <ConversationHeader
                conversation={conversation}
                onExport={() => setShowExport(true)}
                onDelete={() => setShowDelete(true)}
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

            <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will permanently delete &quot;{conversation.title || "Untitled"}&quot; and all
                            its messages. This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                            Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
