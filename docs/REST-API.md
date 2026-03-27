# ChatGPT Archive - REST API Reference

Complete reference for the Web UI REST API endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure via Docker environment

## Authentication

The API is designed for single-user local deployment. No authentication is required by default.

## Response Format

All responses are JSON. Successful responses return HTTP 200-204. Errors return appropriate status codes with an error message:

```json
{
  "detail": "Error message description"
}
```

---

## Endpoints

### Health

#### GET /api/health

Check API health and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "api_version": "1.0.0"
}
```

**Status Codes:**
- `200`: API is healthy
- `500`: Service unavailable

---

### Conversations

#### GET /api/conversations

List conversations with pagination and filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sort_by` | string | `date` | Sort field: `date`, `title`, `messages` |
| `order` | string | `desc` | Sort order: `asc`, `desc` |
| `limit` | int | `50` | Results per page (1-100) |
| `offset` | int | `0` | Pagination offset |
| `tag` | string | — | Filter by tag name |

**Response:**
```json
{
  "total": 150,
  "offset": 0,
  "limit": 50,
  "items": [
    {
      "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
      "title": "Python Flask Tutorial",
      "create_time": 1700000000,
      "update_time": 1700001000,
      "model": "gpt-4",
      "message_count": 24,
      "tags": ["coding", "tutorial"],
      "is_favorite": false
    }
  ]
}
```

#### GET /api/conversations/{conversation_id}

Get conversation details with all messages.

**Response:**
```json
{
  "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
  "title": "Python Flask Tutorial",
  "create_time": 1700000000,
  "update_time": 1700001000,
  "model": "gpt-4",
  "message_count": 24,
  "tags": ["coding"],
  "is_favorite": false,
  "messages": [
    {
      "id": "msg-001",
      "role": "user",
      "content": "Help me build a Flask app",
      "create_time": 1700000000,
      "attachments": []
    },
    {
      "id": "msg-002",
      "role": "assistant",
      "content": "I'd be happy to help...\n[[ATTACHMENT:0]]",
      "create_time": 1700000001,
      "attachments": [
        {
          "type": "image",
          "url": "/api/media/6974cc29-45d8-8327-a6dc-ef1ef0a82f46/file_000000004f48620a9bfb06ccaa684b65",
          "filename": "sample-image.jpg",
          "mime_type": "image/jpeg",
          "width": 640,
          "height": 480,
          "size_bytes": 1234,
          "found": true
        }
      ]
    }
  ]
}
```

Messages may include `[[ATTACHMENT:n]]` placeholders in `content` so the frontend can preserve attachment order relative to text. `attachments` is always present and is an empty array for text-only messages.

Messages may also include a `segments` array for formatted transcript rendering. This is the preferred rendering contract for the web UI.

```json
{
  "kind": "markdown",
  "text": "# Heading\n\nSome prose",
  "attachment_index": null,
  "fallback_label": null
}
```

Segment rules:
- `markdown`: non-empty `text`; `attachment_index` and `fallback_label` are null
- `attachment`: `attachment_index` points into `attachments[]`; `text` and `fallback_label` are null
- `fallback`: non-empty `text` plus a non-empty `fallback_label` for unsupported or malformed content

Raw HTML and unsafe embedded payloads are returned as inert text inside markdown or fallback segments; the frontend does not execute them.

**Status Codes:**
- `200`: Success
- `404`: Conversation not found

#### DELETE /api/conversations/{conversation_id}

Delete a conversation and all its messages.

**Status Codes:**
- `204`: Successfully deleted
- `404`: Conversation not found

---

### Search

#### POST /api/search

Search conversations by keyword or semantic similarity.

**Request Body:**
```json
{
  "query": "machine learning tutorial",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "limit": 20,
  "offset": 0,
  "search_type": "keyword"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | **Yes** | Search query |
| `from_date` | string | No | Filter from date (YYYY-MM-DD) |
| `to_date` | string | No | Filter to date (YYYY-MM-DD) |
| `limit` | int | No | Max results (default: 20) |
| `offset` | int | No | Pagination offset (default: 0) |
| `search_type` | string | No | `keyword`, `semantic`, or `hybrid` (default: keyword) |

**Response:**
```json
{
  "total": 5,
  "offset": 0,
  "limit": 20,
  "items": [
    {
      "conversation_id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
      "title": "ML Basics",
      "snippet": "...discusses **machine learning** concepts...",
      "match_count": 3,
      "create_time": 1700000000,
      "score": 0.95
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid query syntax
- `422`: Missing required fields

---

### Export

#### GET /api/export/{conversation_id}

Export a conversation in the specified format.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | string | **Yes** | Export format |

**Supported Formats:**
- `md` - Markdown
- `json` - JSON
- `yaml` - YAML
- `html` - HTML with styling
- `xml` - XML
- `csv` - CSV (flat message list)
- `xlsx` - Excel spreadsheet

**Response:** File download with appropriate Content-Type and Content-Disposition headers.

**Status Codes:**
- `200`: Success (file download)
- `404`: Conversation not found or invalid format

#### GET /api/export

Export multiple conversations.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | string | **Yes** | Comma-separated conversation IDs |
| `format` | string | **Yes** | Export format |

**Example:**
```
GET /api/export?ids=abc-123,def-456,ghi-789&format=json
```

**Response:** Combined export file or ZIP archive.

---

### Tags

#### GET /api/tags

List all tags with conversation counts.

**Response:**
```json
[
  {
    "name": "coding",
    "count": 15
  },
  {
    "name": "tutorial",
    "count": 8
  }
]
```

#### GET /api/conversations/{conversation_id}/tags

Get tags for a specific conversation.

**Response:**
```json
["coding", "python", "tutorial"]
```

#### POST /api/conversations/{conversation_id}/tags

Add a tag to a conversation.

**Request Body:**
```json
{
  "tag_name": "important"
}
```

**Tag Name Rules:**
- Max 50 characters
- Alphanumeric, hyphens, underscores only
- Case-insensitive (stored lowercase)

**Status Codes:**
- `204`: Tag added
- `400`: Invalid tag name
- `404`: Conversation not found

#### DELETE /api/conversations/{conversation_id}/tags/{tag_name}

Remove a tag from a conversation.

**Status Codes:**
- `204`: Tag removed
- `404`: Conversation or tag not found

---

### Favorites

#### POST /api/conversations/{conversation_id}/favorite

Toggle favorite status for a conversation.

**Response:**
```json
{
  "conversation_id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
  "is_favorite": true
}
```

#### GET /api/favorites

List all favorited conversations.

**Response:** Same format as `GET /api/conversations`, filtered to favorites only.

---

### Import

#### POST /api/import

Import a ChatGPT export archive.

**Request:** `multipart/form-data` with file field `file`.

**Constraints:**
- Max file size: 500MB
- Accepted types: `.zip`

**Response:**
```json
{
  "import_id": "import-abc123",
  "status": "started"
}
```

**Status Codes:**
- `202`: Import queued and running in background
- `400`: Invalid file type or corrupt archive
- `413`: File exceeds 500MB limit

#### GET /api/import/progress

Read the current import progress state.

**Response:**
```json
{
  "status": "processing",
  "current": 50,
  "total": 100,
  "percent": 50.0,
  "message": "Importing conversations..."
}
```

**Event Fields:**
- `status`: `pending`, `processing`, `completed`, `failed`
- `current`: Current progress count
- `total`: Total items
- `message`: Human-readable status
- `error`: Error message (when status=failed)

---

### Media

#### GET /api/media/{conv_id}/{file_id}

Serve a conversation-scoped image or audio file referenced by a `sediment://` asset pointer.

**Path Rules:**
- `conv_id` must be a UUID-like OpenAI conversation ID
- `file_id` must match `file_<hex>`

**Status Codes:**
- `200`: Media file returned
- `400`: Invalid conversation or file identifier
- `404`: File not found in the configured archive media directory

#### GET /api/media/root/{file_id}

Serve a root-level archive file referenced by a `file-service://` asset pointer.

**Behavior:**
- Returns the detected MIME type
- Adds `Content-Disposition: attachment` so browsers can open or download the file with the original archive filename

**Status Codes:**
- `200`: File returned
- `400`: Invalid file identifier
- `404`: File not found

---

### Embeddings

#### GET /api/embeddings/estimate

Estimate cost for generating embeddings.

**Response:**
```json
{
  "total_messages": 5000,
  "messages_to_embed": 4500,
  "already_embedded": 500,
  "estimated_tokens": 450000,
  "estimated_cost": 0.009,
  "estimated_cost_display": "$0.01",
  "model": "text-embedding-3-small"
}
```

#### POST /api/embeddings/generate

Start embedding generation.

**Request Body:**
```json
{
  "max_cost": 5.00
}
```

**Response:**
```json
{
  "task_id": "embed-abc123",
  "status": "started"
}
```

#### GET /api/embeddings/progress

Server-Sent Events stream for embedding progress.

**Response:** SSE stream similar to import progress.

#### POST /api/embeddings/cancel

Cancel embedding generation.

**Status Codes:**
- `200`: Cancellation requested
- `400`: No active embedding task

---

### Settings

#### GET /api/settings

Get current user settings.

**Response:**
```json
{
  "openai_api_key": "sk-...",
  "embedding_model": "text-embedding-3-small",
  "items_per_page": 50,
  "theme": "system",
  "sidebar_open": true,
  "default_export_format": "md",
  "archive_media_dir": "/path/to/extracted/archive"
}
```

#### PUT /api/settings

Update user settings.

**Request Body:**
```json
{
  "openai_api_key": "sk-...",
  "items_per_page": 25,
  "archive_media_dir": "/path/to/extracted/archive"
}
```

**Note:** API key is encrypted at rest. `archive_media_dir` is optional and overrides the default media location for inline attachments.

**Status Codes:**
- `200`: Settings updated
- `400`: Invalid settings value

---

## Rate Limiting

The API enforces rate limiting:
- **100 requests per minute** per IP address
- Returns `429 Too Many Requests` when exceeded

**Response Headers:**
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

---

## Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid input |
| `404` | Not Found - Resource doesn't exist |
| `422` | Validation Error - Missing/invalid fields |
| `429` | Rate Limited - Too many requests |
| `500` | Server Error - Internal error |

---

## OpenAPI Schema

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## See Also

- [README.md](../README.md) - Quick start
- [DEPLOYMENT.md](DEPLOYMENT.md) - Docker deployment
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [API.md](API.md) - Python library API
