// TypeScript types matching API contracts

export interface Conversation {
    id: string;
    title: string | null;
    create_time: number | null;
    update_time: number | null;
    message_count: number;
    model: string | null;
    tags: string[];
    is_favorite: boolean;
}

export interface Message {
    id: string;
    role: "user" | "assistant" | "system" | "tool";
    content: string | null;
    create_time: number | null;
}

export interface ConversationDetail {
    id: string;
    title: string | null;
    create_time: number | null;
    update_time: number | null;
    model: string | null;
    message_count: number;
    messages: Message[];
    tags: string[];
    is_favorite: boolean;
}

export interface SearchResult {
    conversation_id: string;
    title: string | null;
    create_time: number | null;
    match_count: number;
    preview: string;
    relevance_score: number | null;
}

export interface PaginatedResponse<T> {
    total: number;
    offset: number;
    limit: number;
    items: T[];
}

export interface Tag {
    name: string;
    count: number;
}

export interface ImportProgress {
    status: "pending" | "processing" | "complete" | "error" | "idle" | "cancelled";
    current: number;
    total: number;
    percent: number;
    message: string | null;
}

export interface APIError {
    error: string;
    message: string;
    details?: Record<string, unknown>;
}

export type ExportFormat = "markdown" | "json" | "yaml" | "html" | "xml" | "csv" | "excel";
export type ExportFormatCode = "md" | "json" | "yaml" | "html" | "xml" | "csv" | "xlsx";
export type SearchType = "keyword" | "semantic" | "hybrid";
export type SortField = "date" | "title" | "messages";
export type SortOrder = "asc" | "desc";

export interface SearchFilters {
    query: string;
    searchType?: SearchType;
    fromDate?: string;
    toDate?: string;
    limit?: number;
    offset?: number;
}

export interface ListFilters {
    sortBy?: SortField;
    order?: SortOrder;
    limit?: number;
    offset?: number;
    tag?: string;
}

export interface UserSettings {
    openai_api_key: string;
    default_export_format: ExportFormatCode;
    theme: "light" | "dark" | "system";
    sidebar_open: boolean;
    embedding_model: string;
}

export interface EmbeddingEstimate {
    total_messages: number;
    estimated_tokens: number;
    estimated_cost_usd: number;
    model: string;
}
