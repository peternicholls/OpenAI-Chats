# Data Model: Inline Media

**Phase**: 1 — Design  
**Date**: 2026-02-25

> No database schema changes. All entities are runtime-derived.

---

## Entities

### Attachment (runtime, not persisted)

Derived at API response time by parsing message content. Returned as part of the `Message` response object.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"image" \| "audio" \| "file"` | Media category, derived from MIME type |
| `url` | `string` | Relative API URL to retrieve the file: `/api/media/{conv_id}/{file_id}` or `/api/media/root/{file_id}` |
| `filename` | `string` | Original filename from the archive (e.g. `Screenshot 2025-05-23 at 22.17.46.png`) |
| `mime_type` | `string \| null` | MIME type derived from file extension (e.g. `image/jpeg`, `audio/wav`, `application/pdf`) |
| `width` | `integer \| null` | Pixel width (images only, from asset pointer metadata) |
| `height` | `integer \| null` | Pixel height (images only, from asset pointer metadata) |
| `size_bytes` | `integer \| null` | File size in bytes (from asset pointer metadata where available) |
| `found` | `boolean` | Whether the file exists on disk; `false` triggers placeholder display |

### AssetPointer (internal parsing model, not in API response)

Intermediate parsed representation of a content part, used only within `media_service.py`.

| Field | Type | Description |
|-------|------|-------------|
| `scheme` | `"sediment" \| "file-service"` | URI scheme |
| `raw_uri` | `string` | Full original URI string |
| `hex_id` | `string \| null` | Hex ID for `sediment://` pointers |
| `short_id` | `string \| null` | Short alphanumeric ID for `file-service://` pointers |
| `content_type` | `string` | OpenAI content_type (e.g. `image_asset_pointer`) |
| `metadata` | `dict` | Full metadata dict from content part (width, height, dalle, etc.) |

---

## Modified Entities

### Message (API response — extended)

Extends the existing `Message` Pydantic model. **No DB changes.**

| Field | Type | Before | After |
|-------|------|--------|-------|
| `id` | `string` | ✅ existing | unchanged |
| `role` | `string` | ✅ existing | unchanged |
| `content` | `string \| null` | ✅ existing | unchanged (retains text parts, asset pointer dicts stripped) |
| `create_time` | `float \| null` | ✅ existing | unchanged |
| `attachments` | `Attachment[]` | not present | **NEW** — empty array for text-only messages |

---

## State Transitions

### Attachment Resolution (per message, per request)

```
raw DB content string
  → extract asset pointer dicts (ast.literal_eval)
  → parse scheme + ID from 'asset_pointer' field
  → locate file on disk (scandir match)
  → build Attachment with resolved URL and metadata
  → return alongside cleaned text content
```

### Import Flow (modified)

```
ZIP upload
  → extract to temp dir (existing)
  → import conversations.json to DB (existing)
  → copy media files to CHATGPT_ARCHIVE_DIR (NEW — merge, no delete)
  → clean up temp dir (existing)
```

---

## Validation Rules

- `conv_id` path parameter: must match `^[0-9a-f-]{36}$` (UUID format) before any filesystem operation
- `file_id` path parameter (sediment): must match `^file_[0-9a-f]+$`
- `file_id` path parameter (root): must match `^file-[A-Za-z0-9]+$`
- Resolved filesystem path must be `is_relative_to(CHATGPT_ARCHIVE_DIR)` — enforced before `FileResponse` is returned
- All validation failures return `400 Bad Request` (not `404`) to avoid leaking directory structure information

---

## File Layout (permanent media store)

```
CHATGPT_ARCHIVE_DIR/           # default: ~/.chatgpt-archive/media/
├── conversations.json          # (optionally copied — not required for media serving)
├── {conv_id_1}/
│   ├── image/
│   │   └── file_{hex_id}-{uuid}.{ext}
│   └── audio/
│       └── file_{hex_id}-{uuid}.{ext}
├── {conv_id_2}/
│   └── image/
│       └── ...
├── file-{short_id}-{original_name}.{ext}   # root-level files
└── ...
```
