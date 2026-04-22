// API client service with fetch wrapper

import type {
    Conversation,
    ConversationDetail,
    Message,
    PaginatedResponse,
    SearchResult,
    Tag,
    ImportProgress,
    ExportFormat,
    SearchType,
    UserSettings,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// In the browser, always use a relative base so API calls go to the same
// origin the page was loaded from (e.g. 127.0.0.1, LAN IP, or localhost).
// NEXT_PUBLIC_API_URL is baked at build time and hardcodes a hostname, so
// using it directly from the browser breaks access from any other host.
// On the server side (SSR) we keep the absolute URL so Next.js can reach
// the API container by name rather than going through nginx.
const BROWSER_API_BASE = typeof window !== "undefined" ? "" : API_URL;
export const API_BASE_URL = BROWSER_API_BASE;

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

    private normalizeMessage(message: Message): Message {
        return {
            ...message,
            segments: message.segments ?? [],
        };
    }

    private normalizeConversationDetail(conversation: ConversationDetail): ConversationDetail {
        return {
            ...conversation,
            messages: conversation.messages.map((message) => this.normalizeMessage(message)),
        };
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
        const conversation = await this.request<ConversationDetail>(`/api/conversations/${id}`);
        return this.normalizeConversationDetail(conversation);
    }

    getMediaUrl(path: string): string {
        if (path.startsWith("http://") || path.startsWith("https://")) {
            return path;
        }
        return `${this.baseUrl}${path}`;
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

    async renameTag(oldName: string, newName: string): Promise<void> {
        return this.request(`/api/tags/${encodeURIComponent(oldName)}`, {
            method: "PUT",
            body: JSON.stringify({ new_name: newName }),
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
        return this.uploadArchiveWithProgress(file);
    }

    async uploadArchiveWithProgress(
        file: File,
        onProgress?: (percent: number) => void
    ): Promise<ImportProgress> {
        const formData = new FormData();
        formData.append("file", file);

        return new Promise<ImportProgress>((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open("POST", `${this.baseUrl}/api/import`);

            xhr.upload.onprogress = (event) => {
                if (!onProgress || !event.lengthComputable) return;
                const percent = (event.loaded / event.total) * 100;
                onProgress(percent);
            };

            xhr.onload = () => {
                let payload: unknown = null;
                try {
                    payload = xhr.responseText ? JSON.parse(xhr.responseText) : null;
                } catch {
                    payload = null;
                }

                if (xhr.status >= 200 && xhr.status < 300) {
                    onProgress?.(100);
                    resolve(payload as ImportProgress);
                    return;
                }

                const errorPayload = payload as { detail?: string; message?: string } | null;
                reject(
                    new Error(
                        errorPayload?.detail ||
                        errorPayload?.message ||
                        `Upload failed: ${xhr.status}`
                    )
                );
            };

            xhr.onerror = () => {
                reject(new Error("Network error while uploading archive"));
            };

            xhr.send(formData);
        });
    }

    async getImportProgress(): Promise<ImportProgress> {
        return this.request("/api/import/progress");
    }

    // Export
    getExportUrl(conversationId: string, format: ExportFormat): string {
        return `${this.baseUrl}/api/conversations/${conversationId}/export?format=${format}`;
    }

    getBatchExportUrl(conversationIds: string[], format: ExportFormat): string {
        return `${this.baseUrl}/api/export/batch?ids=${conversationIds.join(",")}&format=${format}`;
    }

    async exportConversation(conversationId: string, format: string): Promise<Blob> {
        const formatMap: Record<string, string> = {
            markdown: "md", json: "json", html: "html",
            csv: "csv", yaml: "yaml", xml: "xml", excel: "xlsx"
        };
        const apiFormat = formatMap[format] || format;
        const res = await fetch(this.getExportUrl(conversationId, apiFormat as ExportFormat));
        if (!res.ok) {
            const error = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(error.detail || `Export failed: ${res.status}`);
        }
        return res.blob();
    }

    async exportBatch(conversationIds: string[], format: string): Promise<Blob> {
        const formatMap: Record<string, string> = {
            markdown: "md", json: "json", html: "html",
            csv: "csv", yaml: "yaml", xml: "xml", excel: "xlsx"
        };
        const apiFormat = formatMap[format] || format;
        const res = await fetch(this.getBatchExportUrl(conversationIds, apiFormat as ExportFormat));
        if (!res.ok) {
            const error = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(error.detail || `Batch export failed: ${res.status}`);
        }
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
        maxCost?: number;
    } = {}): Promise<ImportProgress> {
        return this.request("/api/embeddings/generate", {
            method: "POST",
            body: JSON.stringify({
                model: params.model || "text-embedding-3-small",
                batch_size: params.batchSize || 100,
                max_cost: params.maxCost,
            }),
        });
    }

    async validateEmbeddingsKey(apiKey?: string): Promise<{ valid: boolean; message: string }> {
        return this.request("/api/embeddings/validate-key", {
            method: "POST",
            body: JSON.stringify({ api_key: apiKey }),
        });
    }

    async getEmbeddingStats(): Promise<{ total: number; withEmbeddings: number }> {
        return this.request("/api/embeddings/stats");
    }

    async cancelEmbeddingGeneration(): Promise<{ cancelled: boolean; message: string }> {
        return this.request("/api/embeddings/cancel", { method: "POST" });
    }

    getEmbeddingsProgressStreamUrl(): string {
        return `${this.baseUrl}/api/embeddings/progress/stream`;
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

export const api = new APIClient(BROWSER_API_BASE);
