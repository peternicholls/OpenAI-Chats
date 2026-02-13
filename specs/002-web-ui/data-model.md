# Data Model: Web UI

**Feature**: 002-web-ui  
**Date**: 2026-02-12  
**Purpose**: Define API contracts, frontend types, and UI state models

---

## Overview

This document defines the data models for the Web UI layer. The **backend data model is unchanged** from feature 001 (SQLite schema with Conversation, Message, Tag entities). This document focuses on:

1. **API Request/Response Models** (Pydantic schemas for FastAPI)
2. **Frontend TypeScript Types** (matching API contracts)
3. **UI State Models** (client-side state management)

---

## Backend API Models

### Pydantic Schemas (Python)

All API models are defined using Pydantic V2 for validation and serialization.

#### Base Models

```python
# api/models/responses.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ConversationSummary(BaseModel):
    """Conversation list item"""
    id: str = Field(..., description="OpenAI conversation ID")
    title: str | None = Field(None, description="Conversation title")
    create_time: float | None = Field(None, description="Unix timestamp")
    update_time: float | None = Field(None, description="Unix timestamp")
    message_count: int = Field(..., description="Number of messages")
    model: str | None = Field(None, alias="model_slug", description="Model used")
    tags: List[str] = Field(default_factory=list, description="Associated tags")

class Message(BaseModel):
    """Single message in a conversation"""
    id: str = Field(..., description="OpenAI message ID")
    role: str = Field(..., description="author role: user, assistant, system")
    content: str | None = Field(None, description="Message content")
    create_time: float | None = Field(None, description="Unix timestamp")

class ConversationDetail(BaseModel):
    """Full conversation with messages"""
    id: str
    title: str | None
    create_time: float | None
    update_time: float | None
    model: str | None
    message_count: int
    messages: List[Message]
    tags: List[str] = Field(default_factory=list)

class SearchResult(BaseModel):
    """Search result item with preview"""
    conversation_id: str
    title: str | None
    create_time: float | None
    match_count: int = Field(..., description="Number of matching messages")
    preview: str = Field(..., description="Snippet of matching content")
    relevance_score: float | None = Field(None, description="For semantic search")

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    total: int
    offset: int
    limit: int
    items: List  # Type varies by endpoint

class Tag(BaseModel):
    """Tag with usage count"""
    name: str
    count: int = Field(..., description="Number of conversations with this tag")

class ImportProgress(BaseModel):
    """Real-time import progress"""
    status: str = Field(..., description="pending, processing, complete, error")
    current: int = Field(0, description="Conversations processed")
    total: int = Field(0, description="Total conversations")
    percent: float = Field(0.0, description="Completion percentage")
    message: str | None = Field(None, description="Status message")

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = Field(None, description="Additional context")
```

#### Request Models

```python
# api/models/requests.py
from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    """Search query parameters"""
    query: str = Field(..., min_length=1, description="Search term")
    from_date: str | None = Field(None, description="ISO date or YYYY-MM-DD")
    to_date: str | None = Field(None, description="ISO date or YYYY-MM-DD")
    limit: int = Field(20, ge=1, le=100, description="Max results")
    search_type: str = Field("keyword", description="keyword, semantic, hybrid")

class ImportRequest(BaseModel):
    """Import archive request"""
    archive_path: str = Field(..., description="Path to ChatGPT export directory")
    # In production, this would likely be a file upload
    # For Docker, could be a mounted volume path

class TagRequest(BaseModel):
    """Add/remove tag"""
    tag_name: str = Field(..., min_length=1, max_length=50, description="Tag name")

class ExportRequest(BaseModel):
    """Export conversation"""
    format: str = Field(..., description="md, json, yaml, html, xml, csv, xlsx")
    # Response will be file download with appropriate Content-Type

class EmbeddingRequest(BaseModel):
    """Generate embeddings"""
    model: str = Field("text-embedding-3-small", description="OpenAI embedding model")
    batch_size: int = Field(100, ge=1, le=500, description="Messages per batch")
    estimate_only: bool = Field(False, description="Return cost estimate only")
```

---

## Frontend TypeScript Types

### Core Types

```typescript
// web/src/types/index.ts

export interface Conversation {
  id: string;
  title: string | null;
  create_time: number | null;
  update_time: number | null;
  message_count: number;
  model: string | null;
  tags: string[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string | null;
  create_time: number | null;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface SearchResult {
  conversation_id: string;
  title: string | null;
  create_time: number | null;
  match_count: number;
  preview: string;
  relevance_score?: number;
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
  status: 'pending' | 'processing' | 'complete' | 'error';
  current: number;
  total: number;
  percent: number;
  message?: string;
}

export interface APIError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

export type ExportFormat = 'md' | 'json' | 'yaml' | 'html' | 'xml' | 'csv' | 'xlsx';
export type SearchType = 'keyword' | 'semantic' | 'hybrid';
export type SortField = 'date' | 'title' | 'messages';
export type SortOrder = 'asc' | 'desc';
```

---

## UI State Models

### Application State

The app uses **React Server Components** for initial data fetch and **TanStack Query** for client-side data management. Minimal global state is needed.

```typescript
// web/src/types/state.ts

export interface SearchFilters {
  query: string;
  fromDate?: string;  // YYYY-MM-DD
  toDate?: string;    // YYYY-MM-DD
  searchType: SearchType;
  tags?: string[];
}

export interface ListFilters {
  sortBy: SortField;
  order: SortOrder;
  limit: number;
  offset: number;
  tag?: string;
}

export interface UIState {
  // Managed via React Query - no global state needed for data
  // Local UI state only:
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeView: 'list' | 'search' | 'conversation' | 'import' | 'settings';
}

export interface ImportState {
  // Managed by component, polling for progress
  isImporting: boolean;
  progress: ImportProgress | null;
  error: string | null;
}
```

### React Query Keys

```typescript
// web/src/hooks/queryKeys.ts

export const queryKeys = {
  conversations: {
    all: ['conversations'] as const,
    list: (filters: ListFilters) => ['conversations', 'list', filters] as const,
    detail: (id: string) => ['conversations', 'detail', id] as const,
  },
  search: {
    all: ['search'] as const,
    query: (filters: SearchFilters) => ['search', 'query', filters] as const,
  },
  tags: {
    all: ['tags'] as const,
    list: () => ['tags', 'list'] as const,
    forConversation: (id: string) => ['tags', 'conversation', id] as const,
  },
  import: {
    progress: () => ['import', 'progress'] as const,
  },
} as const;
```

---

## API Endpoints

All endpoints are RESTful and return JSON (except export, which returns file downloads).

### Conversations

| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| `GET` | `/api/conversations` | Query params: `sort_by`, `order`, `limit`, `offset`, `tag` | `PaginatedResponse<ConversationSummary>` | List conversations |
| `GET` | `/api/conversations/{id}` | - | `ConversationDetail` | Get conversation by ID |
| `DELETE` | `/api/conversations/{id}` | - | `204 No Content` | Delete conversation |

### Search

| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| `POST` | `/api/search` | `SearchRequest` | `PaginatedResponse<SearchResult>` | Search conversations |

### Tags

| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| `GET` | `/api/tags` | - | `List[Tag]` | List all tags |
| `GET` | `/api/conversations/{id}/tags` | - | `List[string]` | Get tags for conversation |
| `POST` | `/api/conversations/{id}/tags` | `TagRequest` | `204 No Content` | Add tag |
| `DELETE` | `/api/conversations/{id}/tags/{tag}` | - | `204 No Content` | Remove tag |

### Import

| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| `POST` | `/api/import` | `ImportRequest` (or file upload) | `ImportProgress` | Start import |
| `GET` | `/api/import/progress` | - | `ImportProgress` | Get import status |

### Export

| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| `GET` | `/api/conversations/{id}/export` | Query param: `format` | File download | Export conversation |

### Embeddings

| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| `POST` | `/api/embeddings/generate` | `EmbeddingRequest` | `ImportProgress` | Generate embeddings |
| `GET` | `/api/embeddings/estimate` | Query params: `model` | Cost estimate object | Estimate embedding cost |

---

## Validation Rules

### Conversation
- `id`: UUID format (from OpenAI), required
- `title`: Optional, max 500 characters
- `create_time`, `update_time`: Unix timestamp (float), optional

### Message
- `role`: Must be one of: "user", "assistant", "system"
- `content`: Optional (can be null for system placeholders), max 1MB

### Search
- `query`: Required, 1-500 characters
- `from_date`, `to_date`: ISO date format or YYYY-MM-DD
- `limit`: 1-100 (default 20)
- `search_type`: One of "keyword", "semantic", "hybrid"

### Tag
- `tag_name`: Required, 1-50 characters, alphanumeric + hyphens/underscores
- No special characters or spaces

### Export
- `format`: Must be one of: md, json, yaml, html, xml, csv, xlsx

---

## State Transitions

### Import Flow

```
IDLE → START_IMPORT → PROCESSING → COMPLETE
                    ↘             ↗
                      ERROR ------
```

1. **IDLE**: No import in progress
2. **START_IMPORT**: User selects archive, sends `POST /api/import`
3. **PROCESSING**: Backend processes, frontend polls `/api/import/progress` every 2s
4. **COMPLETE**: Import finished, show summary
5. **ERROR**: Import failed, show error message

### Search Flow

```
IDLE → TYPING → DEBOUNCE (500ms) → SEARCH → RESULTS
                                           ↘ ERROR
```

1. **IDLE**: Search input empty
2. **TYPING**: User types, no API call yet
3. **DEBOUNCE**: Wait 500ms after last keystroke
4. **SEARCH**: Send `POST /api/search`
5. **RESULTS**: Display results
6. **ERROR**: Show error message

---

## Data Relationships

```
Conversation (1) ───< (N) Message
      │
      │ (M) ───< (N)
      │
     Tag
```

- One Conversation has many Messages (1:N)
- One Conversation has many Tags (M:N via junction table - handled by backend)
- Messages belong to exactly one Conversation

**No changes** to existing database schema from feature 001.

---

## Storage Considerations

### SQLite Database (Backend)
- Location: `/data/chats.db` in Docker container
- Persisted via Docker volume: `archive-data:/data`
- Access: Backend API only (frontend never accesses DB directly)

### Browser Storage (Frontend)
- **LocalStorage**: UI preferences (theme, sidebar state)
- **No sensitive data**: All conversation data fetched from API
- **React Query cache**: In-memory only, not persisted

---

## Summary

- **Backend models**: Pydantic schemas for type-safe API
- **Frontend types**: TypeScript interfaces matching API contracts
- **State management**: React Query for server state, minimal local UI state
- **Validation**: Pydantic on backend, TypeScript on frontend
- **No database changes**: Reuses existing SQLite schema from feature 001
