import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";
import { queryKeys } from "./queryKeys";

export function useTags() {
    return useQuery({
        queryKey: queryKeys.tags.all,
        queryFn: () => api.listTags(),
    });
}

export function useConversationTags(conversationId: string) {
    return useQuery({
        queryKey: queryKeys.tags.byConversation(conversationId),
        queryFn: () => api.getConversationTags(conversationId),
        enabled: !!conversationId,
    });
}

export function useAddTag(conversationId: string) {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (name: string) => api.addTag(conversationId, name),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.tags.byConversation(conversationId) });
            queryClient.invalidateQueries({ queryKey: queryKeys.tags.all });
            queryClient.invalidateQueries({ queryKey: queryKeys.conversations.all });
        },
    });
}

export function useRemoveTag(conversationId: string) {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (name: string) => api.removeTag(conversationId, name),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.tags.byConversation(conversationId) });
            queryClient.invalidateQueries({ queryKey: queryKeys.tags.all });
            queryClient.invalidateQueries({ queryKey: queryKeys.conversations.all });
        },
    });
}
