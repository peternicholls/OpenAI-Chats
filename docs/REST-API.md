# OpenAI-Chats REST API Reference

This reference documents the current FastAPI surface used by the local web app.

## Base URLs

| Mode | Base URL |
|------|----------|
| Docker Compose | `http://localhost/api` |
| Direct backend development | `http://localhost:8000/api` |

Interactive OpenAPI docs are available when the backend is running directly:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Authentication

The shipped API is intended for trusted, single-user local deployment. It has no built-in authentication layer.

## Error Format

Most errors are returned as:

```json
{
  "detail": "Error message"
}
```

## Core Response Shapes

### Conversation Summary

```json
{
  "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
  "title": "Example conversation",
  "create_time": 1700000000,
  "update_time": 1700001000,
  "message_count": 24,
  "model": "gpt-4",
  "tags": ["research"],
  "is_favorite": false
}
```

### Import / Embedding Progress

```json
{
  "status": "processing",
  "current": 10,
  "total": 50,
  "percent": 20.0,
  "message": "Importing conversations..."
}
```

## Endpoints

### GET /api/health

Checks database connectivity.

Response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

### GET /api/conversations

Lists conversations.

Query parameters:

| Parameter | Description |
|-----------|-------------|
| `sort_by` | `date`, `title`, or `messages` |
| `order` | `asc` or `desc` |
| `limit` | page size |
| `offset` | pagination offset |
| `tag` | optional tag filter |

Response:

```json
{
  "total": 150,
  "offset": 0,
  "limit": 50,
  "items": []
}
```

### GET /api/conversations/{conversation_id}

Returns a conversation with its messages.

### DELETE /api/conversations/{conversation_id}

Deletes a conversation.

Returns `204 No Content` on success.

### POST /api/search

Search request body:

```json
{
  "query": "machine learning",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "limit": 20,
  "offset": 0,
  "search_type": "keyword"
}
```

`search_type` supports `keyword`, `semantic`, and `hybrid`.

Search result items currently use `preview` and `relevance_score`:

```json
{
  "conversation_id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
  "title": "ML Basics",
  "create_time": 1700000000,
  "match_count": 3,
  "preview": "...matching excerpt...",
  "relevance_score": 0.95
}
```

### GET /api/conversations/{conversation_id}/export

Exports one conversation.

Query parameters:

| Parameter | Description |
|-----------|-------------|
| `format` | `md`, `json`, `yaml`, `html`, `xml`, `csv`, or `xlsx` |

Returns a downloadable file.

### GET /api/export/batch

Exports multiple conversations in one response.

Query parameters:

| Parameter | Description |
|-----------|-------------|
| `ids` | comma-separated conversation IDs |
| `format` | export format |

### GET /api/tags

Lists tags with usage counts.

### GET /api/conversations/{conversation_id}/tags

Lists tags for one conversation.

### POST /api/conversations/{conversation_id}/tags

Request body:

```json
{
  "tag_name": "important"
}
```

### DELETE /api/conversations/{conversation_id}/tags/{tag_name}

Removes a tag.

### PUT /api/tags/{tag_name}

Renames a tag.

Request body:

```json
{
  "new_name": "renamed-tag"
}
```

### POST /api/conversations/{conversation_id}/favorite

Toggles favorite state.

Response:

```json
{
  "is_favorite": true
}
```

### GET /api/favorites

Lists favorited conversations using the same paginated shape as `/api/conversations`.

### POST /api/import

Starts an archive import from a ZIP upload.

Request type: `multipart/form-data` with field `file`

Constraints:

- ZIP only
- 500 MB max upload size

Response status: `202 Accepted`

Response body:

```json
{
  "status": "pending",
  "current": 0,
  "total": 0,
  "percent": 0.0,
  "message": "Import queued..."
}
```

### GET /api/import/progress

Returns the current import progress as JSON.

### GET /api/import/progress/stream

Streams import progress as Server-Sent Events.

### GET /api/embeddings/stats

Returns embedding coverage stats.

### GET /api/embeddings/estimate

Estimates embedding cost.

Optional query parameter:

| Parameter | Description |
|-----------|-------------|
| `model` | embedding model name |

### POST /api/embeddings/generate

Starts embedding generation.

Request body:

```json
{
  "model": "text-embedding-3-small",
  "batch_size": 100,
  "estimate_only": false,
  "max_cost": 5.0
}
```

### POST /api/embeddings/cancel

Requests cancellation of embedding generation.

### GET /api/embeddings/progress

Returns embedding progress as JSON.

### GET /api/embeddings/progress/stream

Streams embedding progress as Server-Sent Events.

### POST /api/embeddings/validate-key

Validates either a supplied OpenAI API key or the stored key.

Request body:

```json
{
  "api_key": "sk-..."
}
```

### GET /api/settings

Returns user settings.

Current fields:

```json
{
  "theme": "light",
  "default_export_format": "md",
  "openai_api_key": null,
  "sidebar_open": true,
  "embedding_model": "text-embedding-3-small",
  "items_per_page": 50
}
```

### PUT /api/settings

Updates any subset of settings.

Request body example:

```json
{
  "theme": "dark",
  "items_per_page": 25
}
```

## Rate Limiting

The app configures rate limiting at 100 requests per minute per IP by default.

## See Also

- [README.md](../README.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [API.md](API.md)
