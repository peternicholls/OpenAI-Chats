# Research: Frontend Formatting

**Phase**: 0 — Resolve technical decisions for formatted conversation rendering  
**Date**: 2026-03-25

## R-001: Rendering Boundary

**Decision**: Generate ordered render segments in the backend conversation response and let the frontend render those segments.

**Rationale**:
- The importer stores multimodal message parts as newline-joined Python `repr` strings, so the frontend currently only sees flattened text.
- The backend already owns attachment resolution and safe parsing of stored asset-pointer payloads.
- A backend-produced segment list avoids duplicating parsing rules in the browser and keeps all clients consistent.

**Alternatives considered**:
- Parse everything in the frontend: rejected because it duplicates archive parsing logic and makes browser behavior drift from API behavior.
- Keep attachment tokens only and add more frontend heuristics: rejected because it does not solve raw structured payload leaks cleanly.

## R-002: Markdown Rendering Stack

**Decision**: Use a safe React markdown renderer with support for the agreed markdown scope, specifically `react-markdown` with `remark-breaks`, and do not enable raw HTML rendering.

**Rationale**:
- The agreed MVP scope is headings, emphasis, lists, links, blockquotes, inline code, and fenced code blocks.
- `react-markdown` covers the core markdown rendering path cleanly and safely.
- `remark-breaks` preserves author-intended line breaks more closely to ChatGPT-style message formatting.
- Omitting raw HTML support satisfies the security requirement and keeps rendering deterministic.

**Alternatives considered**:
- Regex-based custom markdown formatting: rejected because it is brittle and hard to extend safely.
- `dangerouslySetInnerHTML` with server-generated HTML: rejected because it expands the XSS surface and complicates sanitization.

## R-003: Segment Model

**Decision**: Add a `segments` array to each message response while retaining existing `content` and `attachments` for compatibility.

**Rationale**:
- `segments` provides an ordered rendering contract without forcing the UI to reinterpret raw strings.
- Keeping `content` avoids breaking existing consumers abruptly and preserves a readable fallback/debug representation.
- Attachment segments can reference existing `attachments` by index, avoiding repeated attachment payloads in the response.

**Alternatives considered**:
- Replace `content` entirely: rejected because it is a larger compatibility break than this feature needs.
- Duplicate full attachment data inside each segment: rejected because it creates redundant payloads and synchronization risk.

## R-004: Structured Payload Fallback Policy

**Decision**: Parse known structured payload lines on the backend, convert recognized asset-related payloads into attachment segments, and preserve unsupported structured payloads as explicit fallback segments.

**Rationale**:
- The spec requires avoiding raw transport blobs when a user-facing rendering is available, not silently dropping unknown content.
- A fallback segment preserves archive fidelity for unsupported cases while preventing broken layout.
- This keeps malformed or unexpected content visible and readable during migration to richer rendering.

**Alternatives considered**:
- Drop unknown structured payloads entirely: rejected because it risks data loss in the UI.
- Always show raw payload text verbatim: rejected because it preserves the current user-facing problem.

## R-005: Scope Boundaries For This Feature

**Decision**: Fully support the clarified markdown scope only; tables, raw HTML, and math-like blocks remain plain readable fallback content in this feature phase.

**Rationale**:
- The feature goal is ChatGPT-like readability for the common cases, not full markdown or HTML parity.
- This keeps the implementation small enough to validate without redesigning the message pipeline again.
- It aligns with the clarified scope recorded in the feature spec.

**Alternatives considered**:
- Add full GFM and math support immediately: rejected because it expands scope without being required for the MVP.
