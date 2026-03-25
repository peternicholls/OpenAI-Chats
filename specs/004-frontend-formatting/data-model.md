# Data Model: Frontend Formatting

**Phase**: 1 — Design  
**Date**: 2026-03-25

> No database schema changes. All additions are runtime response models and internal parsing models.

## Entities

### RenderSegment (runtime, API response)

Represents one ordered piece of a rendered message.

| Field | Type | Description |
|-------|------|-------------|
| `kind` | `"markdown" \| "attachment" \| "fallback"` | Segment classification for rendering |
| `text` | `string \| null` | Markdown or fallback text payload |
| `attachment_index` | `integer \| null` | Index into `Message.attachments` when `kind = "attachment"` |
| `fallback_label` | `string \| null` | Short label explaining unsupported or malformed structured content |

### FormattedMessage (runtime, API response)

Extends the existing `Message` response with ordered segments.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | OpenAI message ID |
| `role` | `string` | Author role |
| `content` | `string \| null` | Backward-compatible raw/cleaned content fallback |
| `create_time` | `float \| null` | Message timestamp |
| `attachments` | `Attachment[]` | Existing resolved media attachments from feature 003 |
| `segments` | `RenderSegment[]` | Ordered frontend rendering contract |

### StructuredContentPayload (internal)

Represents a parsed non-prose content part from stored archive content.

| Field | Type | Description |
|-------|------|-------------|
| `raw_text` | `string` | Original stored line or block |
| `content_type` | `string \| null` | Source content type if recognized |
| `asset_pointer` | `string \| null` | Pointer URI if present |
| `metadata` | `dict` | Parsed metadata payload |
| `recognized` | `boolean` | Whether the payload maps cleanly to known UI behavior |

## Relationships

- `FormattedMessage.segments` is the ordered source of truth for rendering.
- `attachment` segments refer to `FormattedMessage.attachments` by `attachment_index`.
- `StructuredContentPayload` is an internal parser model used to derive `RenderSegment` and `Attachment` data.

## State Transitions

### Runtime Formatting Flow

```text
stored message content
  -> split into raw prose / structured lines
  -> parse known structured payloads
  -> resolve attachments where applicable
  -> build ordered RenderSegment[]
  -> return Message + attachments + segments
```

### Frontend Rendering Flow

```text
ConversationDetail.messages[]
  -> MessageBubble receives segments
  -> markdown segments render through safe markdown component
  -> attachment segments render existing attachment UI
  -> fallback segments render readable plain blocks
```

## Validation Rules

- `segments` MUST preserve the original reading order of all renderable content within a message.
- `attachment_index` MUST reference a valid item in `attachments` when `kind = "attachment"`.
- `markdown` segments MUST contain only user-visible text content, not raw transport payloads.
- Unsupported structured payloads MUST become `fallback` segments instead of being dropped silently.
- Text-only messages SHOULD produce a single `markdown` segment for the common fast path.
