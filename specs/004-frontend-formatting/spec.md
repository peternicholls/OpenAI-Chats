# Feature Specification: Frontend Formatting

**Feature Branch**: `004-frontend-formatting`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Render conversation content like ChatGPT so markdown and structured asset parts display as formatted UI instead of raw markdown or raw JSON/dict payloads"

## Clarifications

### Session 2026-03-25

- Q: Which markdown scope should the initial implementation support? → A: Common ChatGPT markdown: headings, emphasis, lists, links, blockquotes, inline code, fenced code blocks.

### Session 2026-04-11 (Part 1)

- Q: Should LaTeX-style math blocks (`\[...\]`, `\(...\)`) receive rendered output or fall back to plain text? → A: Math rendering is in scope for sprint 004. The archive uses `\[...\]` for display math and `\(...\)` for inline math. These MUST be rendered with KaTeX via `remark-math` and `rehype-katex`. A delimiter-normalisation pre-pass is required because the archive does not use `$`/`$$` delimiters.

### Session 2026-04-11 (Part 2)

- Q: How should internal AI reasoning/search turns (assistant `thoughts`, tool dispatch, `web.run`, `reasoning_recap`) be handled in the conversation view? They currently render as `[No content]` bubbles because their content is stripped by OpenAI in the export. → A: Do NOT suppress them entirely. Show a collapsed `ThinkingBlock` in the conversation view at the point where the thinking activity occurred. The block indicates activity type (reasoning, web search, or both) with an appropriate label. Users can expand it; the expanded view acknowledges that the detailed content is not available in the export. This preserves the conversation context (you can see that the AI was thinking/searching) without visual noise.
- Q: Should query titles, duration ("Thought for 31s"), or search sources appear in the thinking block? → A: These metadata fields (`reasoning_title`, `finished_duration_sec`, `search_result_groups`) are not persisted from the importer in the current schema and cannot be shown without a schema change. Sprint 004 implements a minimal `ThinkingBlock` using only `content_type` and `author_role` (already in the DB). Richer summaries are a post-sprint enhancement.

### Session 2026-04-11 (Part 3)

- Q: The conversation header currently shows date+time, message count, and model. How should these be improved? → A:
  - **Header time**: The time in the header does not reliably match the first message turn (it is the conversation object creation time, not the first message time). Drop the time; show the start date only.
  - **Multi-day conversations**: Conversations can span many days. The header MUST show both start date and last-updated date (already stored as `update_time`; omit "Updated" label if the date is the same as start). Inside the conversation view, inline date separators MUST be inserted between message groups whenever the calendar date changes — this is the standard pattern (iMessage, Slack) and lets users orient themselves without cluttering every message bubble.
  - **Message count**: The current count includes hidden system nodes, thinking/tool turns, and empty bootstrap placeholders. The count MUST reflect only user-visible messages (applying the same suppression predicate as FR-015/FR-016). Message numbering on bubbles is not required and would add clutter.
  - **Per-message model**: `metadata.model_slug` exists per message in the raw JSON but is not imported into the DB. Per-message model badges cannot be shown without a schema migration and importer change. This is explicitly **out of scope for sprint 004**; the conversation-level `model_slug` label in the header remains as-is. A future sprint should add a `model_slug TEXT NULL` column to the `messages` table and import it, then display it as a small badge on assistant turns where it differs from the conversation default.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Read Formatted Messages (Priority: P1)

As a user reviewing a conversation, I want markdown-style message content to render as readable formatted content so I can consume answers the way they appeared in ChatGPT instead of mentally parsing raw markdown syntax.

**Why this priority**: Raw markdown is currently visible in normal conversation reading, which directly degrades the core experience for nearly every conversation.

**Independent Test**: Open a conversation containing headings, lists, emphasis, links, blockquotes, inline code, and fenced code blocks. The conversation view should display formatted content rather than literal markdown markers, and text-only conversations should remain readable.

**Acceptance Scenarios**:

1. **Given** a message containing supported markdown patterns, **When** the conversation is opened, **Then** the message is rendered as formatted content instead of showing raw markdown markers.
2. **Given** a message containing inline and block code, **When** the conversation is opened, **Then** code is visually distinct from surrounding prose and remains readable.
3. **Given** a plain-text message with no markdown, **When** the conversation is opened, **Then** the message remains unchanged in meaning and order.
4. **Given** a message containing `\[...\]` display math or `\(...\)` inline math, **When** the conversation is opened, **Then** the mathematical notation renders as formatted output rather than raw LaTeX source.

---

### User Story 2 - Hide Raw Structured Payloads (Priority: P2)

As a user viewing a multimodal conversation, I want structured content parts such as asset payloads and message metadata to appear as polished message blocks or attachment UI so I do not see raw Python-style dicts or JSON-like blobs in the transcript.

**Why this priority**: This is the remaining visible gap after inline media support. The feature is not complete from a user perspective while payload objects still leak into the interface.

**Independent Test**: Open a conversation that currently shows raw asset-pointer dictionaries. The conversation view should replace those payloads with readable UI elements or suppress them when they are only transport metadata.

**Acceptance Scenarios**:

1. **Given** a message containing structured content payloads related to attachments or generated assets, **When** the conversation is opened, **Then** the user sees readable attachment or content blocks instead of raw dict text.
2. **Given** a message containing both prose and structured parts, **When** the conversation is opened, **Then** the prose remains in the correct order around the rendered structured content.

---

### User Story 3 - Graceful Rendering Fallbacks (Priority: P3)

As a user opening older or unusual conversations, I want unsupported or malformed content to degrade gracefully so the conversation stays readable even when exact formatting cannot be reproduced.

**Why this priority**: It protects archive reliability and prevents formatting work from making edge-case conversations unreadable.

**Independent Test**: Open conversations with malformed markdown, unsupported structured payloads, or partial attachment metadata. The UI should still show a readable fallback instead of blank sections or broken layout.

**Acceptance Scenarios**:

1. **Given** malformed markdown or unsupported structured content, **When** the conversation is opened, **Then** the system shows a readable fallback without exposing broken layout or crashing the page.
2. **Given** missing metadata for a structured content part, **When** the conversation is opened, **Then** the user still sees an understandable representation of the message content.

---

### Edge Cases

- A single message mixes paragraphs, markdown, attachment placeholders, and structured payloads in alternating order.
- A conversation contains malformed markdown that cannot be fully interpreted.
- A structured content block is present for an attachment that is missing on disk.
- A message includes literal braces or code examples that resemble JSON or Python dicts but are intended to be shown as content.
- Very long code blocks, tables, or quoted sections must remain readable on both desktop and mobile layouts.
- A message contains a `\begin{...}...\end{...}` LaTeX environment block; KaTeX parse errors from unsupported environments MUST be caught and the block rendered as a labeled fallback rather than breaking the message.
- A message contains internal ChatGPT citation tokens — Private Use Area character sequences of the form `\uE200cite\uE202turnNsearchM\uE201`, `\uE200cite\uE202turnNviewM\uE201`, and `\uE200filecite\uE202turnNfileM\uE201` — which carry no user-facing meaning and MUST be stripped before rendering so they do not appear as junk characters.
- A conversation produced by a thinking/search-enabled model contains internal processing turns (assistant `thoughts`, tool dispatch `code`, `web.run` results, `reasoning_recap`) alongside the user-visible turns. OpenAI strips all content from these nodes in the archive export — `parts[]` is always empty. These turns MUST NOT appear as `[No content]` bubbles. Instead, consecutive processing turns within a single AI response exchange MUST be collapsed into a single `ThinkingBlock` segment that is rendered inline in the conversation at the point the activity occurred. `system` and `user_editable_context` nodes (those with `is_visually_hidden_from_conversation = true`) are suppressed entirely and produce no output.
- A conversation spans multiple calendar days. The conversation view MUST insert an inline date separator (a subtle centred label showing the date) between message groups whenever the calendar date changes. The separator must derive its date from `message.create_time` and appear only when the date of the current message differs from the date of the previous rendered message.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The conversation view MUST render the initial supported markdown set as formatted message content rather than displaying raw markdown syntax.
- **FR-001a**: The initial supported markdown set MUST include headings, emphasis, lists, links, blockquotes, inline code, and fenced code blocks.
- **FR-002**: The conversation view MUST preserve the original reading order of prose, attachments, and other structured content parts within each message.
- **FR-003**: The system MUST avoid displaying raw asset-pointer dictionaries, transport payloads, or similar structured metadata when a user-facing rendering is available.
- **FR-004**: Users MUST be able to distinguish prose, code, quotes, lists, links, and attachment-related content through semantic rendering and visible styling differences in the conversation view.
- **FR-005**: The system MUST provide readable fallback rendering for malformed or unsupported markdown and structured content instead of showing a broken or blank message area.
- **FR-006**: The system MUST preserve text meaning when formatting is applied, including line breaks and code content.
- **FR-007**: The system MUST render formatted content in the conversation view with readable code overflow handling, correct content order, and readable attachment and fallback presentation.
- **FR-008**: The system MUST keep text-only and plain-message conversations readable without introducing visual regressions.
- **FR-009**: The system MUST treat already-resolved media attachments from feature 003 as input content to be presented cleanly, not redefined as a new attachment system.
- **FR-010**: The system MUST avoid executing unsafe embedded content while rendering message formatting.
- **FR-011**: The system MUST support generated assistant content and imported historical content with the same formatting behavior when they use the same message structures.
- **FR-012**: Tables and raw HTML MAY fall back to plain readable output in this feature phase and are not required to receive full rich rendering.
- **FR-013**: The conversation view MUST render LaTeX-style display math (`\[...\]`) and inline math (`\(...\)`) as formatted mathematical notation. A pre-processing step MUST normalise these delimiters to `$$`/`$` before the markdown pipeline so that the KaTeX rendering library can interpret them correctly.
- **FR-014**: The conversation view MUST strip ChatGPT internal citation tokens — PUA sequences matching `\uE200(file)?cite(\uE202turnN(search|view|file)M)+\uE201` — from message text during the pre-processing step so they do not appear as junk characters in the rendered transcript. The surrounding prose MUST remain intact after removal.
- **FR-015**: The system MUST suppress nodes that are explicitly marked hidden from the conversation view. Suppression applies to any message node where `metadata.is_visually_hidden_from_conversation = true` (covers `system` and `user_editable_context` nodes). Suppressed nodes produce no output segment and are not returned to the frontend.
- **FR-016**: The system MUST group consecutive internal processing turns within a single AI response exchange into a `thinking` segment and attach it to the response's message object. A node is an internal processing turn if: `content_type IN ('thoughts', 'reasoning_recap')`, `author_role = 'assistant' AND content_type = 'code'` (tool-dispatch), or `author_role = 'tool' AND (content IS NULL OR content = '')` (tool-result with stripped data). Empty assistant bootstrap nodes (`author_role = 'assistant' AND content_type = 'text' AND content IS NULL OR content = ''`) MUST be suppressed entirely (they carry no information even as a thinking indicator).
- **FR-017**: The `ThinkingBlock` UI component MUST default to a collapsed state. The collapsed label MUST indicate the type of activity: "Reasoning" for reasoning-only exchanges, "Searched the web" for exchanges that included web search tool calls, or "Reasoning and web search" when both are present. When expanded, the block MUST display an honest disclosure that detailed content is not available in this export format.
- **FR-018**: The conversation header MUST display the start date only (not the time). When `update_time` falls on a different calendar date than `create_time`, the header MUST also show a last-updated date in the form "Updated [date]". Time values MUST NOT appear in the header.
- **FR-019**: The conversation view MUST render an inline date separator between message groups whenever the calendar date of a rendered message differs from the calendar date of the preceding rendered message. The separator must derive its date from the individual message `create_time`. It MUST NOT appear before the first message.
- **FR-020**: The message count displayed in the conversation header MUST reflect only user-visible messages — those that would produce at least one render segment after applying the suppression and grouping rules from FR-015 and FR-016. Hidden system nodes, assistant bootstrap placeholders, and internal processing turns that are folded into a `ThinkingBlock` MUST NOT contribute to the count. The `ThinkingBlock` itself counts as one visible element for its parent assistant message, not as additional messages.
- **FR-021**: Image attachments MUST be displayed as thumbnails in the conversation view. A thumbnail MUST be small enough not to dominate the message bubble. Clicking a thumbnail MUST open a modal overlay showing the full-size image, the filename, any available metadata (dimensions, file size, MIME type), a download button, and a close button. Clicking outside the modal content area OR pressing Escape OR clicking the close button MUST dismiss the modal. The filename and metadata MUST appear only inside the modal, not in the inline thumbnail view.

### Key Entities *(include if feature involves data)*

- **Formatted Message**: A conversation message after presentation rules have been applied, including readable prose, formatted markdown, attachment blocks, thinking blocks, and fallbacks.
- **Renderable Segment**: A user-visible segment inside a message, such as prose, code, quote, list, attachment block, thinking block, or fallback block, kept in original message order.
- **Structured Content Payload**: Non-prose message content imported from the archive, such as asset metadata or multimodal content parts, which may need transformation before display.
- **ThinkingBlock**: A collapsible UI element representing one or more consecutive internal AI processing turns (reasoning, web search, tool use) within a single response exchange. Content is not recoverable from the export; the block surfaces that activity occurred and its type.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: In acceptance fixtures covering supported markdown patterns, 100% of target messages display formatted output rather than raw markdown markers.
- **SC-002**: In acceptance fixtures covering structured content payloads, 100% of supported asset-related payloads display as readable UI blocks instead of raw dict or JSON-like text.
- **SC-003**: Text, attachment blocks, and structured-content fallbacks remain in original order for 100% of mixed-content acceptance scenarios.
- **SC-004**: Text-only conversations load with no visible formatting regression in the existing conversation validation suite.
- **SC-006**: In acceptance fixtures containing generated assistant content and imported historical content with equivalent message structures, 100% of cases produce the same segment types in the same order.
- **SC-007**: In malicious-content acceptance fixtures containing raw HTML or script-like payloads, 100% of cases render inert readable output or fallback UI without executing embedded content.
- **SC-008**: In acceptance fixtures containing display-math (`\[...\]`) and inline-math (`\(...\)`) content, 100% of cases render as formatted mathematical notation rather than raw LaTeX source.
- **SC-009**: In acceptance fixtures containing PUA citation token sequences, 100% of cases produce rendered message text with no visible citation tokens; the surrounding prose remains intact and readable.
- **SC-010**: In acceptance fixtures derived from conversations containing internal processing turns: (a) 0% of rendered content shows a `[No content]` bubble; (b) a `ThinkingBlock` element is present in the conversation view at the point where reasoning or search activity occurred; (c) the block is collapsed by default and expands on interaction; (d) `system` and `user_editable_context` turns produce no rendered element.
- **SC-011**: In acceptance fixtures containing conversations that span multiple calendar dates: (a) at least one inline date separator is present in the rendered conversation view between message groups from different dates; (b) the separator date matches the `create_time` of the first message in the later group; (c) no separator appears before the first message.
- **SC-012**: In acceptance fixtures containing image attachments: (a) the inline thumbnail is smaller than 200 × 150 px in its rendered bounding box; (b) clicking the thumbnail opens the modal overlay; (c) the modal shows the filename, at least one metadata field (dimensions or size), a download link, and a close affordance; (d) clicking the backdrop closes the modal; (e) pressing Escape closes the modal.

## Assumptions

- Feature 003 inline media is considered successful enough to serve as the attachment foundation for this work.
- This feature focuses on presentation and rendering behavior, not archive import redesign.
- Existing conversation data remains the source content; the system will not require users to re-import archives solely to benefit from formatting improvements.
- Exact visual parity with ChatGPT is not required, but the experience should feel comparably readable and polished.
- Unsupported rich content may use clear fallbacks as long as raw transport payloads are not the primary user-facing output.
- Per-message model badges are out of scope for sprint 004 because `metadata.model_slug` is not persisted in the current DB schema. The conversation-level model label in the header is retained as-is.
