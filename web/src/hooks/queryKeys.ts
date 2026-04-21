export const queryKeys = {
    conversations: {
        all: ["conversations"] as const,
        list: (filters: Record<string, unknown>) => ["conversations", "list", filters] as const,
        infiniteList: (filters: Record<string, unknown>) => ["conversations", "infinite-list", filters] as const,
        detail: (id: string) => ["conversations", "detail", id] as const,
    },
    search: {
        all: ["search"] as const,
        results: (filters: Record<string, unknown>) => ["search", "results", filters] as const,
    },
    tags: {
        all: ["tags"] as const,
        byConversation: (id: string) => ["tags", "conversation", id] as const,
    },
    favorites: {
        all: ["favorites"] as const,
    },
    import: {
        progress: ["import", "progress"] as const,
    },
    settings: {
        all: ["settings"] as const,
    },
    embeddings: {
        estimate: (model?: string) => ["embeddings", "estimate", model] as const,
    },
};
