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
    attachments: Attachment[];
    segments?: RenderSegment[];
}

export interface MarkdownSegment {
    kind: "markdown";
    text: string;
    attachment_index: null;
    fallback_label: null;
}

export interface AttachmentSegment {
    kind: "attachment";
    text: null;
    attachment_index: number;
    fallback_label: null;
}

export interface FallbackSegment {
    kind: "fallback";
    text: string;
    attachment_index: null;
    fallback_label: string;
}

export interface ThinkingSegment {
    kind: "thinking";
    activity_type: "reasoning" | "search" | "both";
    text: null;
    attachment_index: null;
    fallback_label: null;
}

export type RenderSegment = MarkdownSegment | AttachmentSegment | FallbackSegment | ThinkingSegment;

export interface Attachment {
    type: "image" | "audio" | "file";
    url: string;
    filename: string;
    mime_type: string | null;
    width: number | null;
    height: number | null;
    size_bytes: number | null;
    found: boolean;
}

export interface ConversationDetail {
    id: string;
    title: string | null;
    create_time: number | null;
    update_time: number | null;
    model: string | null;
    message_count: number;
    visible_message_count?: number | null;
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
    sidebar_collapsed: boolean;
    embedding_model: string;
    items_per_page: number;
    archive_media_dir?: string | null;
    code_line_numbers: boolean;
    long_prompt_truncation: boolean;
}

export interface EmbeddingEstimate {
    messages_to_embed: number;
    total_characters: number;
    estimated_tokens: number;
    model: string;
    price_per_million_tokens: number;
    estimated_cost_usd: number;
    estimated_cost_display: string;
}
