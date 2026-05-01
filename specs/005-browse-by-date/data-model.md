# Data Model: Browse Chats by Date

## Overview

The feature reuses the existing `conversations` records in SQLite and adds derived read models for calendar browsing, date-range narrowing, alternate date sorting, and unknown-date handling. No new persistence tables are required.

## Core Source Entity

### ConversationRecord

Represents the existing stored conversation metadata used by all browse and search flows.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `openai_id` | string | `conversations.openai_id` | Stable user-facing identifier |
| `title` | string \| null | `conversations.title` | Shown in summaries and lists |
| `create_time` | number \| null | `conversations.create_time` | Canonical initiated timestamp for calendar placement |
| `update_time` | number \| null | `conversations.update_time` | Optional alternate recency timestamp for sort order |
| `message_count` | number | derived query | Existing summary field |
| `model_slug` | string \| null | `conversations.model_slug` | Existing summary field |
| `tags` | string[] | derived query | Existing summary field |
| `is_favorite` | boolean | `conversations.is_favorite` | Existing summary field |

**Validation rules**
- `openai_id` must remain unique and preserved from the archive.
- `create_time` may be null; null values may not be mapped to a dated calendar cell.
- `update_time` may be null; when absent, updated-date sort must fall back to deterministic null ordering rather than inferred values.

## Derived Read Models

### CalendarPeriod

Represents the currently visible window in the separate date-browsing mode.

| Field | Type | Notes |
|-------|------|-------|
| `period_unit` | enum(`month`, `week`) | Controls adjacent navigation granularity |
| `period_start` | date | Inclusive local date |
| `period_end` | date | Inclusive local date |
| `timezone` | string | Viewer-local IANA timezone |
| `range_start` | date \| null | Optional range filter lower bound |
| `range_end` | date \| null | Optional range filter upper bound |

**Validation rules**
- `period_start <= period_end`
- `range_start <= range_end` when both are present
- `timezone` must be a valid IANA timezone string

### CalendarDayBucket

Represents one dated cell in the calendar response.

| Field | Type | Notes |
|-------|------|-------|
| `date` | date | Local calendar day derived from `create_time` |
| `conversation_count` | number | Count of conversations initiated on that day |
| `has_conversations` | boolean | UI convenience flag |
| `is_selected` | boolean | Optional echo of current selected day |
| `is_in_range` | boolean | Optional echo of active date range |

**Validation rules**
- `conversation_count >= 0`
- `has_conversations` must equal `conversation_count > 0`

### DateBrowseResult

Represents the paginated conversation list for a selected calendar day.

| Field | Type | Notes |
|-------|------|-------|
| `selected_date` | date | Requested local calendar day |
| `timezone` | string | Viewer-local IANA timezone |
| `items` | ConversationSummary[] | Conversations for that day |
| `total` | number | Total matches for the day |
| `offset` | number | Pagination offset |
| `limit` | number | Page size |

**Validation rules**
- Only conversations whose initiated date resolves to `selected_date` may appear.
- Pagination must be stable under deterministic ordering.

### UnknownDateGroup

Represents conversations that cannot be assigned a reliable initiated date.

| Field | Type | Notes |
|-------|------|-------|
| `label` | string | Fixed display label such as `Unknown date` |
| `items` | ConversationSummary[] | Conversations with null or invalid initiated timestamp |
| `total` | number | Total size of the group |
| `offset` | number | Pagination offset |
| `limit` | number | Page size |

**Validation rules**
- Members must not appear in any `CalendarDayBucket` response.
- No fallback date may be synthesized from `update_time`.

### DateSortRule

Represents the active ordering basis in non-date search modes.

| Field | Type | Notes |
|-------|------|-------|
| `sort_by` | enum(`relevance`, `initiated_date`, `updated_date`, `title`, `messages`) | Expanded from current list/search behavior |
| `order` | enum(`asc`, `desc`) | Current direction |
| `label` | string | Human-readable UI label |

**Validation rules**
- `relevance` remains valid only where semantic or keyword search returns ranked results.
- `initiated_date` and `updated_date` must be explicitly labeled in the UI and API payloads.

## Relationships

- One `CalendarPeriod` contains many `CalendarDayBucket` entries.
- One `CalendarDayBucket` can expose many `ConversationRecord` summaries through `DateBrowseResult`.
- One `UnknownDateGroup` contains `ConversationRecord` summaries excluded from dated buckets.
- One `DateSortRule` applies to either search results or general conversation lists outside the dedicated date mode.

## State Transitions

### DateBrowseState

| From | Event | To |
|------|-------|----|
| `idle` | User switches into date mode | `period_loaded` |
| `period_loaded` | User selects a calendar day | `day_selected` |
| `period_loaded` | User opens unknown-date group | `unknown_group_selected` |
| `day_selected` | User changes range | `period_loaded` with updated filters |
| `day_selected` | User navigates adjacent period | `period_loaded` for next/previous period |
| `unknown_group_selected` | User returns to dated calendar | `period_loaded` |

## API Payload Notes

- `ConversationSummary` continues to expose both `create_time` and `update_time` so the client can label initiated date vs last updated date consistently.
- Calendar responses should avoid embedding full transcript content; they only need counts, dates, and paginated summaries.
- The unknown-date group should be a first-class API response rather than a special-case empty date.
