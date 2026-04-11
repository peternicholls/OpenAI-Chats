# Ground Truth from ChatGPT archive

This document captures the relevant content from the ChatGPT archive data that informed the design of the frontend formatting feature. It serves as a reference for the original message content, attachment handling, and structured payloads that were observed in real user conversations.

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