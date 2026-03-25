# Feature Specification: Frontend Formatting

**Feature Branch**: `004-frontend-formatting`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Render conversation content like ChatGPT so markdown and structured asset parts display as formatted UI instead of raw markdown or raw JSON/dict payloads"

## Clarifications

### Session 2026-03-25

- Q: Which markdown scope should the initial implementation support? → A: Common ChatGPT markdown: headings, emphasis, lists, links, blockquotes, inline code, fenced code blocks.

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
- **FR-007**: The system MUST render formatted content consistently across desktop and mobile conversation views, including preserved content order, readable code overflow handling, and readable attachment and fallback presentation.
- **FR-008**: The system MUST keep text-only and plain-message conversations readable without introducing visual regressions.
- **FR-009**: The system MUST treat already-resolved media attachments from feature 003 as input content to be presented cleanly, not redefined as a new attachment system.
- **FR-010**: The system MUST avoid executing unsafe embedded content while rendering message formatting.
- **FR-011**: The system MUST support generated assistant content and imported historical content with the same formatting behavior when they use the same message structures.
- **FR-012**: Tables, raw HTML, and math-like blocks MAY fall back to plain readable output in this feature phase and are not required to receive full rich rendering.

### Key Entities *(include if feature involves data)*

- **Formatted Message**: A conversation message after presentation rules have been applied, including readable prose, formatted markdown, attachment blocks, and fallbacks.
- **Renderable Segment**: A user-visible segment inside a message, such as prose, code, quote, list, attachment block, or fallback block, kept in original message order.
- **Structured Content Payload**: Non-prose message content imported from the archive, such as asset metadata or multimodal content parts, which may need transformation before display.

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
- **SC-005**: In desktop and mobile acceptance viewports, formatted messages, attachment blocks, and fallback blocks remain readable without overlap, clipping, or order changes.
- **SC-006**: In acceptance fixtures containing generated assistant content and imported historical content with equivalent message structures, 100% of cases produce the same segment types in the same order.
- **SC-007**: In malicious-content acceptance fixtures containing raw HTML or script-like payloads, 100% of cases render inert readable output or fallback UI without executing embedded content.

## Assumptions

- Feature 003 inline media is considered successful enough to serve as the attachment foundation for this work.
- This feature focuses on presentation and rendering behavior, not archive import redesign.
- Existing conversation data remains the source content; the system will not require users to re-import archives solely to benefit from formatting improvements.
- Exact visual parity with ChatGPT is not required, but the experience should feel comparably readable and polished.
- Unsupported rich content may use clear fallbacks as long as raw transport payloads are not the primary user-facing output.
