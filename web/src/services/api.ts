// API client service with fetch wrapper

import type {
    Conversation,
    ConversationDetail,
    PaginatedResponse,
    SearchResult,
    Tag,
    ImportProgress,
    ExportFormat,
    SearchType,
    UserSettings,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(
        path: string,
        options?: RequestInit
    ): Promise<T> {
        const res = await fetch(`${this.baseUrl}${path}`, {
            headers: {
                "Content-Type": "application/json",
                ...options?.headers,
            },
            ...options,
        });

        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: res.statusText }));
            throw new Error(error.detail || error.message || `API error: ${res.status}`);
        }

        if (res.status === 204) {
            return undefined as T;
        }

        return res.json();
    }

    // Conversations
    async listConversations(params: {
        sortBy?: string;
        order?: string;
        limit?: number;
        offset?: number;
        tag?: string;
    } = {}): Promise<PaginatedResponse<Conversation>> {
        const query = new URLSearchParams();
        if (params.sortBy) query.set("sort_by", params.sortBy);
        if (params.order) query.set("order", params.order);
        if (params.limit) query.set("limit", String(params.limit));
        if (params.offset) query.set("offset", String(params.offset));
        if (params.tag) query.set("tag", params.tag);
        return this.request(`/api/conversations?${query}`);
    }

    async getConversation(id: string): Promise<ConversationDetail> {
        return this.request(`/api/conversations/${id}`);
    }

    async deleteConversation(id: string): Promise<void> {
        return this.request(`/api/conversations/${id}`, { method: "DELETE" });
    }

    // Search
    async search(params: {
        query: string;
        fromDate?: string;
        toDate?: string;
        limit?: number;
        offset?: number;
        searchType?: SearchType;
    }): Promise<PaginatedResponse<SearchResult>> {
        return this.request("/api/search", {
            method: "POST",
            body: JSON.stringify({
                query: params.query,
                from_date: params.fromDate,
                to_date: params.toDate,
                limit: params.limit || 20,
                offset: params.offset || 0,
                search_type: params.searchType || "keyword",
            }),
        });
    }

    // Tags
    async listTags(): Promise<Tag[]> {
        return this.request("/api/tags");
    }

    async getConversationTags(conversationId: string): Promise<string[]> {
        return this.request(`/api/conversations/${conversationId}/tags`);
    }

    async addTag(conversationId: string, tagName: string): Promise<void> {
        return this.request(`/api/conversations/${conversationId}/tags`, {
            method: "POST",
            body: JSON.stringify({ tag_name: tagName }),
        });
    }

    async removeTag(conversationId: string, tagName: string): Promise<void> {
        return this.request(`/api/conversations/${conversationId}/tags/${tagName}`, {
            method: "DELETE",
        });
    }

    // Favorites
    async toggleFavorite(conversationId: string): Promise<{ is_favorite: boolean }> {
        return this.request(`/api/conversations/${conversationId}/favorite`, {
            method: "POST",
        });
    }

    async listFavorites(params: {
        sortBy?: string;
        order?: string;
        limit?: number;
        offset?: number;
    } = {}): Promise<PaginatedResponse<Conversation>> {
        const query = new URLSearchParams();
        if (params.sortBy) query.set("sort_by", params.sortBy);
        if (params.order) query.set("order", params.order);
        if (params.limit) query.set("limit", String(params.limit));
        if (params.offset) query.set("offset", String(params.offset));
        return this.request(`/api/favorites?${query}`);
    }

    // Import
    async uploadArchive(file: File): Promise<ImportProgress> {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${this.baseUrl}/api/import`, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: res.statusText }));
            throw new Error(error.detail || error.message || `Upload failed: ${res.status}`);
        }

        return res.json();
    }

    async getImportProgress(): Promise<ImportProgress> {
        return this.request("/api/import/progress");
    }

    // Export
    getExportUrl(conversationId: string, format: ExportFormat): string {
        return `${this.baseUrl}/api/conversations/${conversationId}/export?format=${format}`;
    }

    async exportConversation(conversationId: string, format: string): Promise<Blob> {
        const formatMap: Record<string, string> = {
            markdown: "md", json: "json", html: "html",
            csv: "csv", yaml: "yaml", xml: "xml", excel: "xlsx"
        };
        const apiFormat = formatMap[format] || format;
        const res = await fetch(this.getExportUrl(conversationId, apiFormat as ExportFormat));
        if (!res.ok) throw new Error(`Export failed: ${res.status}`);
        return res.blob();
    }

    // Embeddings
    async estimateEmbeddings(model?: string): Promise<{
        messages_to_embed: number;
        estimated_tokens: number;
        model: string;
        estimated_cost_usd: number;
        estimated_cost_display: string;
    }> {
        const query = model ? `?model=${model}` : "";
        return this.request(`/api/embeddings/estimate${query}`);
    }

    async generateEmbeddings(params: {
        model?: string;
        batchSize?: number;
    } = {}): Promise<ImportProgress> {
        return this.request("/api/embeddings/generate", {
            method: "POST",
            body: JSON.stringify({
                model: params.model || "text-embedding-3-small",
                batch_size: params.batchSize || 100,
            }),
        });
    }

    // Health
    async healthCheck(): Promise<{ status: string; database: string }> {
        return this.request("/api/health");
    }

    // Settings
    async getSettings(): Promise<UserSettings> {
        return this.request("/api/settings");
    }

    async updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
        return this.request("/api/settings", {
            method: "PUT",
            body: JSON.stringify(settings),
        });
    }
}

export const api = new APIClient(API_URL);
