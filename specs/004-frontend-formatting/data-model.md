# Data Model: Frontend Formatting

**Phase**: 1 — Design  
**Date**: 2026-03-25

This feature introduces no database schema changes. All entities below are response-time or UI-runtime models.

---

## Entities

### RenderSegment

Ordered user-visible segment derived from a message's stored content.

| Field | Type | Description |
|-------|------|-------------|
| `kind` | `"markdown" | "attachment" | "fallback"` | Segment rendering category |
| `text` | `string | null` | Markdown or fallback body; null for attachment segments |
| `attachment_index` | `integer | null` | Index into `Message.attachments`; set only for attachment segments |
| `fallback_label` | `string | null` | Short label for fallback blocks, such as `Unsupported content` or `Malformed attachment payload` |

**Validation rules**:
- `markdown` segments require non-empty `text`, null `attachment_index`, null or empty `fallback_label`.
- `attachment` segments require non-null `attachment_index`, null `text`, null `fallback_label`.
- `fallback` segments require non-empty `text` and non-empty `fallback_label`.
- Segment order must match the original reading order in the message source content.

### FormattedMessage

Extension of the existing API `Message` object used by the conversation view.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Existing OpenAI message ID |
| `role` | `"user" | "assistant" | "system" | "tool"` | Existing message role |
| `content` | `string | null` | Legacy text content retained for compatibility |
| `create_time` | `number | null` | Existing timestamp |
| `attachments` | `Attachment[]` | Existing attachment metadata from feature 003 |
| `segments` | `RenderSegment[]` | New ordered render contract for the frontend |

**Validation rules**:
- `segments` may be empty only when a message has no content and no attachments.
- Any `attachment_index` must resolve to an existing attachment in `attachments[]`.
- When a message includes both prose and attachments, `segments[]` must preserve the original interleaving.

### Attachment

Existing runtime attachment model reused from feature 003.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"image" | "audio" | "file"` | Media presentation category |
| `url` | `string` | API URL for the attachment |
| `filename` | `string` | Display filename |
| `mime_type` | `string | null` | Detected MIME type |
| `width` | `integer | null` | Image width when available |
| `height` | `integer | null` | Image height when available |
| `size_bytes` | `integer | null` | File size when known |
| `found` | `boolean` | Whether the underlying file exists |

### StructuredContentPayload

Internal parsing concept representing dict-like or JSON-like content extracted from stored message text.

| Field | Type | Description |
|-------|------|-------------|
| `raw_text` | `string` | Original serialized payload text from the archive-derived message content |
| `classification` | `"attachment_metadata" | "unsupported" | "malformed"` | Parser outcome |
| `attachment_index` | `integer | null` | Set if the payload maps to an existing resolved attachment |
| `fallback_label` | `string | null` | Human-readable fallback title when the payload cannot be cleanly rendered as prose or attachment |

---

## State Transitions

### Message Formatting Pipeline

```text
raw stored message content
  -> detect known attachment payload lines
  -> resolve attachments with existing media service
  -> classify remaining content into markdown prose or structured payload blocks
  -> emit ordered RenderSegment[]
  -> render in MessageBubble using markdown, attachment, and fallback components
```

### Fallback Classification

```text
structured payload text
  -> recognized attachment pointer? yes -> attachment segment
  -> safely recognized supported prose? yes -> markdown segment
  -> malformed or unsupported structured payload -> fallback segment
```

---

## Invariants

- The archive and database remain unchanged; formatting is derived at read time.
- Render segments must never reorder content relative to the stored message.
- Unsupported content must remain visible in some readable form.
- Plain text messages without markdown must remain readable when routed through the new renderer.
- The frontend must not execute raw HTML, script content, or arbitrary embedded payload data.
