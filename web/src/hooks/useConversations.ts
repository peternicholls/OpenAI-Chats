"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";
import { queryKeys } from "@/hooks/queryKeys";
import type { ListFilters, Conversation, PaginatedResponse } from "@/types";

export function useConversations(filters: Partial<ListFilters> = {}) {
    return useQuery<PaginatedResponse<Conversation>>({
        queryKey: queryKeys.conversations.list(filters),
        queryFn: () =>
            api.listConversations({
                sortBy: filters.sortBy || "date",
                order: filters.order || "desc",
                limit: filters.limit || 50,
                offset: filters.offset || 0,
                tag: filters.tag,
            }),
    });
}

export function useConversation(id: string) {
    return useQuery({
        queryKey: queryKeys.conversations.detail(id),
        queryFn: () => api.getConversation(id),
        enabled: !!id,
    });
}
