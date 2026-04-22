"use client";

import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";
import { queryKeys } from "@/hooks/queryKeys";
import type { ListFilters, Conversation, PaginatedResponse } from "@/types";

function buildConversationListParams(filters: Partial<ListFilters> = {}, offset = 0) {
    return {
        sortBy: filters.sortBy || "date",
        order: filters.order || "desc",
        limit: filters.limit || 50,
        offset,
        tag: filters.tag,
    };
}

export function useConversations(filters: Partial<ListFilters> = {}) {
    return useQuery<PaginatedResponse<Conversation>>({
        queryKey: queryKeys.conversations.list(filters),
        queryFn: () => api.listConversations(buildConversationListParams(filters, filters.offset || 0)),
    });
}

export function useInfiniteConversations(filters: Partial<ListFilters> = {}) {
    return useInfiniteQuery<PaginatedResponse<Conversation>>({
        queryKey: queryKeys.conversations.infiniteList(filters),
        initialPageParam: filters.offset || 0,
        queryFn: ({ pageParam }) => api.listConversations(buildConversationListParams(filters, pageParam as number)),
        getNextPageParam: (lastPage) => {
            const nextOffset = lastPage.offset + lastPage.items.length;
            return nextOffset < lastPage.total ? nextOffset : undefined;
        },
    });
}

export function useConversation(id: string) {
    return useQuery({
        queryKey: queryKeys.conversations.detail(id),
        queryFn: () => api.getConversation(id),
        enabled: !!id,
    });
}
