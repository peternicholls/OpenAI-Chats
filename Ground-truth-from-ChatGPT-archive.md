# Ground Truth from ChatGPT archive

This document captures the relevant content from the ChatGPT archive data that informs the parsing of the conversation structure and message types for both import in to the database and rendering in the frontend. It is intended to provide a clear reference for the observed data formats and structures that underpin the design of the frontend formatting feature. It serves as a reference for the original message content, attachment handling, and structured payloads that were observed in real user conversations.

## Downloaded Archive Data File
  - /PeterNicholls-ChatGPTArchive-2026-01-26-08-54-37.zip

## Extracted Files
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/chat.html
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/conversations.json
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/group_chats.json
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/message_feedback.json
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/shared_conversations.json
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/shopping.json
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/sora.json
  - /6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875/user.json

---

## Internal Processing Turn Types (Research: 2026-04-11)

### Finding

Conversations produced by reasoning/search-enabled models contain internal processing nodes alongside the user-visible message turns. These nodes are stored in `conversations.json` as mapping entries and imported into the `messages` table.

The **actual content** (reasoning text, executed code, search results) is **completely stripped by OpenAI in the export**. Every `parts[]` array for these nodes is empty — there is nothing to render or summarise.

### Node Types Observed (conversation: "Staving off Height Loss")

| `author_role` | `content_type` | `author.name` | `is_visually_hidden` | What it represents |
|---|---|---|---|---|
| `system` | `text` | — | `true` | System prompt / developer message |
| `user` | `user_editable_context` | — | `true` | User custom instructions (memory) |
| `assistant` | `text` | — | `false` | Preamble placeholder before thinking starts; empty parts |
| `assistant` | `thoughts` | — | `false` | Active reasoning turn; content stripped |
| `assistant` | `code` | — | `false` | Tool dispatch (web search); `search_queries` in metadata, content stripped |
| `tool` | `text` | `web.run` | `false` | Search execution; `search_model_queries` in metadata, results stripped |
| `tool` | `text` | `web.run` | `false` | Search results; `search_result_groups` in metadata, content stripped |
| `assistant` | `reasoning_recap` | — | `false` | End-of-reasoning marker; only `finished_duration_sec` in metadata |

### Infrastructure Status

- `is_hidden` (maps to `is_visually_hidden_from_conversation`) — stored in DB column, already filtered by `WHERE is_hidden = 0` in `db.get_messages()`. Covers `system` and `user_editable_context` nodes.
- `content_type` — stored in DB column `content_type TEXT DEFAULT 'text'`. Available for service-layer filtering.
- `author_role` — stored in DB column. Available for filtering.

**Gap**: `thoughts`, `reasoning_recap`, `code` (assistant), and empty `tool` nodes do **not** have `is_visually_hidden_from_conversation` set, so they pass through the existing `is_hidden = 0` filter and currently appear in the conversation view as `[No content]` bubbles.

### Suppression Rules (derived)

A message node is **not user-visible** and MUST be suppressed if any of the following is true:

1. `is_hidden = 1` — already handled by DB filter
2. `content_type IN ('thoughts', 'reasoning_recap', 'user_editable_context')` — internal process types
3. `author_role = 'system'` — system prompt nodes (not flagged hidden in all archive versions)
4. `author_role = 'assistant' AND content_type = 'code'` — tool dispatch nodes
5. `author_role = 'tool' AND (content IS NULL OR content = '')` — tool result nodes with stripped data

### Metadata Available (but content stripped)

- `assistant`/`code` nodes: `search_queries`, `reasoning_title`, `searched_display_string`
- `tool`/`web.run` nodes: `search_model_queries`, `search_result_groups`, `debug_sonic_thread_id`
- `reasoning_recap` nodes: `finished_duration_sec`

These metadata fields could support a future "show search activity" feature but are explicitly out of scope for sprint 004. Sprint 004 suppresses these turns entirely.

---

## Comprehensive Node Type Inventory — All Conversations (Research: 2026-04-11)

> **Scope**: Derived from analysis of all conversations in the January 2026 archive export. Supersedes/extends the single-conversation observations above. Data produced by scanning every node across the full `conversations.json`.

### Key Correction to Earlier Finding

The earlier finding that *"every parts[] array for these nodes is empty"* was based on a single reasoning-heavy conversation. Across the full archive, **many tool nodes DO have content in parts[]**. Reasoning nodes (`thoughts`, `reasoning_recap`, `assistant/code`) remain fully stripped. The picture is more nuanced.

### Full Node Type Inventory

| `author_role` | `content_type` | Nodes w/ content | Nodes empty | `parts[]` content status | Key metadata fields |
|---|---|---|---|---|---|
| `user` | `text` | 14,452 | 32 | ✅ Main user messages | `attachments`, `model_slug`, `timestamp_` |
| `user` | `multimodal_text` | 611 | 0 | ✅ User messages with images/files | `attachments`, `image_send_uuid` |
| `user` | `user_editable_context` | 0 | 777 | ❌ Stripped — user memory/instructions | `is_visually_hidden_from_conversation`, `user_context_message_data` |
| `user` | `app_pairing_content` | 0 | 850 | ❌ Stripped — app pairing system nodes | `is_visually_hidden_from_conversation`, `app_pairing` |
| `assistant` | `text` | 16,529 | 1,575 | ✅ Main assistant responses | `model_slug`, `citations`, `content_references`, `finish_details` |
| `assistant` | `multimodal_text` | 49 | 0 | ✅ Assistant responses with images (DALL-E inline) | `citations`, `content_references` |
| `assistant` | `thoughts` | 0 | 5,176 | ❌ **Fully stripped** — reasoning text never present | `reasoning_group_id`, `reasoning_status`, `model_slug` |
| `assistant` | `code` | 0 | 6,241 | ❌ **Fully stripped** — tool dispatch nodes | `search_queries`, `reasoning_title`, `searched_display_string`, `model_slug` |
| `assistant` | `reasoning_recap` | 0 | 1,499 | ❌ **Fully stripped** — end-of-reasoning marker | `finished_duration_sec`, `reasoning_group_id`, `model_slug` |
| `system` | `text` | 0 | 4,308 | ❌ Stripped — system prompts | `is_visually_hidden_from_conversation`, `model_slug` |
| `tool` | `text` | 2,902 | 3,123 | ⚠️ **Partially present** — depends on `author.name` (see below) | `model_slug`, `search_result_groups`, `search_model_queries`, `finished_duration_sec`, `reasoning_title`, `canvas`, `citations` |
| `tool` | `multimodal_text` | 344 | 0 | ✅ File search results, DALL-E responses, image containers | `image_gen_title`, `retrieval_file_index`, `citations`, `content_references` |
| `tool` | `execution_output` | 0 | 1,087 | ❌ **parts[] empty** — code output is in `metadata.aggregate_result` | `aggregate_result`, `ada_visualizations`, `attachments` |
| `tool` | `code` | 0 | 453 | ❌ Stripped — web tool dispatch | `command`, `status` |
| `tool` | `computer_output` | 0 | 275 | ❌ Stripped — computer use output | `visited_risky_domain` |
| `tool` | `sonic_webpage` | 0 | 824 | ❌ Stripped — web page content | `command`, `debug_sonic_thread_id`, `status` |
| `tool` | `tether_browsing_display` | 0 | 1,800 | ❌ Stripped — browser display content | `_cite_metadata`, `display_title`, `display_url`, `n7jupd_url` |
| `tool` | `tether_quote` | 0 | 405 | ❌ Stripped — quoted browser content | `_cite_metadata`, `retrieval_file_index` |
| `tool` | `system_error` | 0 | 181 | ❌ Stripped — tool error payloads | `invoked_plugin`, `status`, `jit_plugin_data` |

### `tool/text` Content by `author.name`

The `tool/text` type is highly heterogeneous — content presence depends on which tool produced it:

| `author.name` | Nodes w/ content | Notes |
|---|---|---|
| `container.exec` | 436 | Python/code execution stdout/stderr |
| `bio` | 166 | Memory tool — what ChatGPT stored about the user |
| `canmore.update_textdoc` | 166 | Canvas document content after update |
| `canmore.create_textdoc` | 40 | Canvas document initial content |
| `oboe` | 298 | Async task runner results |
| `file_search` | 142 | File search results |
| `t2uay3k.sj1i4kz` | 212 | Custom GPT tool responses |
| `hevy_com__jit_plugin.*` | 176 | Hevy fitness API responses |
| `web.run` | 93 | Web search results (only a fraction — rest stripped) |
| `a8km123` | 819 | (Internal tool, identity unknown) |
| `web.run` | 2,212 | ❌ Empty — web search results stripped |
| `research_kickoff_tool.*` | 54 | ❌ Empty — research task nodes |

### Critical Finding: `execution_output` Code Results Live in Metadata

For `tool/execution_output` nodes (1,087 total), the **actual code execution output is NOT in `parts[]`** — it is in `metadata.aggregate_result`. This field contains a structured object with:
- `code` — the Python code that was run
- `messages` — stdout/stderr output lines
- `status` — execution status (`"success"` / `"error"`)
- `run_id` — execution identifier

Additionally, `metadata.ada_visualizations` may contain chart/visualisation metadata and `metadata.attachments` lists any files produced.

The current importer completely misses this content because it only reads `parts[]`.

### `author.name` Not Currently Stored

The `author.name` field (e.g. `"canmore"`, `"container.exec"`, `"python"`, `"web.run"`, `"bio"`, `"dalle.text2im"`) is distinct from `author.role` and is the primary identifier for tool nodes. It is **not imported** by the current importer, so tool nodes are indistinguishable in the DB beyond their `content_type`.

### Non-String `parts[]` Entries

For `multimodal_text` nodes (both `user` and `tool`), `parts[]` entries are **dicts**, not strings. Example for a DALL-E response:
```json
{
  "asset_pointer": "file-abc123",
  "size_bytes": 204800,
  "width": 1024,
  "height": 1024,
  "metadata": {"dalle": {"gen_id": "...", "prompt": "..."}}
}
```
The current importer calls `str(p)` on these, producing an ugly Python dict repr rather than valid JSON. This must be fixed to `json.dumps(p)` for non-string parts.

### Import Gaps Summary

| Gap | Impact | Sprint |
|---|---|---|
| `author.name` not stored | Can't distinguish tool types in DB | 005 |
| `metadata` dict not stored | Loses search_queries, finished_duration_sec, aggregate_result, citations, content_references, etc. | 005 |
| `execution_output` code results (in `metadata.aggregate_result`) not imported | Code execution output permanently lost | 005 |
| Non-string `parts[]` serialised as Python repr not JSON | Multimodal/image parts malformed in DB | 005 |
| Inline cite tokens in `assistant/text` parts | 1,087 messages store raw `\ue200cite\ue202...\ue201` markers; resolution data in `metadata.content_references` lost without metadata blob | 005 (store raw + metadata; render later) |
| `thoughts`/`reasoning_recap`/`assistant code` content stripped by OpenAI | Irretrievable — no fix possible | N/A |

### Inline Citation Tokens (Research: 2026-04-12)

**1,087 messages** (out of ~19,900 `assistant/text` nodes with metadata) contain inline citation reference markers embedded in the `parts[]` text string. These are Unicode **Private Use Area** characters forming a structured token:

```
\ue200cite\ue202{ref_id}\ue201
```

Multiple ref IDs can be combined in one token (comma-like grouping):
```
\ue200cite\ue202turn2search4\ue202turn2news26\ue202turn0search1\ue201
```

**Token anatomy:**
- `\ue200` — open marker
- `\ue202` — delimiter (separates `cite` keyword from ref IDs, and ref IDs from each other)
- `\ue201` — close marker
- ref ID format: `turn{N}view{M}` / `turn{N}search{M}` / `turn{N}news{M}`

**Resolution data** — in `metadata.content_references` (array, web search citations) and `metadata.citations` (array, file/document citations). The `content_references` items have:
- `matched_text` — the raw token (e.g. `\ue200cite\ue202turn5view0\ue201`)
- `start_idx` / `end_idx` — **byte** offsets into the parts text string
- `alt` — pre-formatted markdown replacement string (e.g. `([Margaret Thatcher Foundation](https://...))`)
- `items[]` — structured citation objects: `title`, `url`, `pub_date`, `attribution`
- `safe_urls[]` — resolved URL list

The `citations` items (file/document search) have:
- `start_ix` / `end_ix` — **character** offsets (not byte — distinct from `content_references`)
- `citation_format_type` — `"berry_file_search"` (uploaded file) or `"tether_v4"` (web page via code interpreter)
- `metadata.name` / `metadata.title` — file name or page title
- `metadata.text` — quoted excerpt from the source
- `metadata.extra.cited_message_id` — links to the tool message that performed retrieval

**Import strategy:** Store `parts[]` text verbatim (cite markers intact). The `metadata` blob (FR-012b) captures `content_references` and `citations` for later resolution. Citation rendering is a display-layer concern (deferred to a future sprint).

**Current importer behaviour:** The raw text (with `\ue200`/`\ue201` markers) is stored in `content`. The markers are invisible in some renderers and appear as replacement characters (?) in others. The metadata containing the resolution is currently lost (fixed by FR-012b).

---

## Message Branching — Edited Messages (Research: 2026-04-11)

### Finding

When a user edits a previously-sent message in ChatGPT, the original message is **not overwritten**. Instead, a new sibling node is added to the tree alongside the original, and `current_node` (a top-level field on the conversation object) is updated to point to the last message of the new active path.

The `conversations.json` mapping is therefore a **tree, not a linear list**. Any node can have multiple children (siblings = edit versions). The "real" conversation is the path obtained by walking **from `current_node` backwards via `parent` links to the root**.

### Evidence (conversation: "Legacy PHP code update." — 544a9c4c)

- `current_node`: `adcb48ac-f690-45c9-a8b5-a227e2ce946b`
- Active path: **34 nodes** (walk from current_node to root)
- Inactive branch nodes: **31 nodes** (alternative edit versions, never part of the canonical conversation)
- Branch points found: **4** — all caused by the user re-editing their initial message multiple times

### Why `weight` Does NOT Distinguish Branches

All inactive branch nodes in this conversation have `weight=1.0` — identical to active-path nodes.  
`weight=0.0` only marks internal tool/system nodes (not user edits).  
**Weight cannot be used to filter out abandoned branches.**

### What the App Currently Does Wrong

`extract_messages_from_mapping()` iterates `mapping.items()` — **all 65 nodes** — with no path-awareness. All branches are imported into the database. `get_conversation_messages()` then returns all non-hidden messages ordered by DB insertion id, so multiple versions of the same user message appear consecutively: "multiple consecutive user turns" is the visible symptom of unfiltered branching.

### Correct Behaviour

The canonical conversation timeline is the **active path only** — nodes reachable by traversing `parent` from `current_node` back to root. Branch nodes (alternative edit versions) must be excluded from the rendered transcript.

### Fix Required (out of scope Sprint 004, log for Sprint 005+)

1. Store `current_node` on the conversation row (new column `current_node_id TEXT`)
2. In `extract_messages_from_mapping()`, compute the active path set by walking `current_node → root` before iterating, and skip any node whose `openai_id` is not in the active set
3. Re-import or migration script to prune existing branch nodes from the DB

### Suppression Rule (to add)

A message node is **not user-visible** and MUST be suppressed if it is not on the active path from `current_node` to root. This is determined at import time, not query time, since the `current_node` is only available in the raw JSON.