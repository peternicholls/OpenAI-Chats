# Research: Frontend Formatting

**Phase**: 0 — Resolve implementation choices and unknowns  
**Date**: 2026-03-25

---

## R-001: Where Should Formatting Be Derived?

**Decision**: Derive ordered render segments on the backend and expose them in the conversation-detail API response.

**Rationale**:
- Current message rendering in `web/src/components/conversations/MessageBubble.tsx` only splits on `[[ATTACHMENT:n]]` tokens and otherwise treats all remaining content as plain text.
- The importer flattens structured `content.parts[]` values into strings, which means raw payload dictionaries already exist in stored message content.
- `api/services/media_service.py` only strips recognized `asset_pointer` dictionaries; unrecognized structured payloads pass through unchanged.
- A backend segment builder centralizes the archive-specific parsing rules and gives the frontend a stable ordered structure to render.
- The API already serves as the integration boundary between archive data and the web UI, so extending the response contract is the least surprising place for this logic.

**Alternatives considered**:
- Parse everything in the browser from raw `content`: rejected because it duplicates archive parsing rules and pushes transport-format knowledge into the UI.
- Normalize content during import into new DB fields: rejected because the feature does not require a schema change and archive data must remain the source of truth.

---

## R-002: How Should Markdown Be Rendered Safely?

**Decision**: Use `react-markdown` with `remark-breaks` and explicit component overrides for the supported markdown subset.

**Rationale**:
- The supported scope in the spec is limited to headings, emphasis, lists, links, blockquotes, inline code, and fenced code blocks.
- `react-markdown` is mature, safe by default, and avoids `dangerouslySetInnerHTML`.
- `remark-breaks` better matches ChatGPT-style line-break behavior for message prose.
- The frontend already uses React components and Tailwind prose styling, so component overrides can align rendered blocks with the existing message bubble presentation.
- Unsupported constructs such as tables, raw HTML, and math can intentionally fall back to readable output without trying to fully emulate GitHub Flavored Markdown.

**Alternatives considered**:
- Build an in-house regex formatter: rejected because it is brittle for nested or mixed markdown.
- Render server-produced HTML: rejected because it expands the sanitization surface and couples API output to exact presentation markup.

---

## R-003: How Should Structured Payloads That Are Not Attachments Be Shown?

**Decision**: Convert non-user-facing structured payloads into explicit `fallback` segments with a label and readable text body.

**Rationale**:
- The spec requires graceful degradation for unsupported or malformed content rather than blank output or crashes.
- Some dict-like payloads are transport metadata, tool output wrappers, or malformed asset blocks that should not be rendered as prose.
- A labeled fallback block gives the user context without leaking a raw transport blob inline with prose.
- This approach preserves content order and makes future structured segment types additive rather than breaking.

**Alternatives considered**:
- Drop unknown payloads silently: rejected because it risks hiding information from archived conversations.
- Leave unknown payloads inline as raw text: rejected because it fails the primary user experience goal of the feature.

---

## R-004: What Segment Model Preserves Ordering Without Duplicating Data?

**Decision**: Add `segments[]` to each message, with segment kinds `markdown`, `attachment`, and `fallback`, while continuing to return `attachments[]` separately.

**Rationale**:
- The existing attachment system already resolves media metadata and URLs cleanly; it should be reused rather than replaced.
- An attachment segment can reference `attachments[]` by index, which preserves order without duplicating attachment payloads inside every segment.
- Markdown and fallback segments can carry text directly, allowing the frontend to render each block with an appropriate component.
- The message can retain `content` for compatibility and debugging during rollout.

**Alternatives considered**:
- Put full attachment objects inside segments: rejected because it duplicates response data and creates consistency risks.
- Continue tokenizing attachment positions inside `content`: rejected because it still leaves markdown and fallback parsing coupled to a raw string.

---

## R-005: What Is the Concrete Test Strategy?

**Decision**: Cover the feature at three levels: backend segment-builder unit tests, frontend renderer unit tests, and Playwright mixed-content conversation tests.

**Rationale**:
- Backend tests validate that segment derivation preserves order and classifies structured payloads correctly.
- Frontend tests validate markdown rendering, attachment insertion, and fallback block appearance independent of API wiring.
- End-to-end tests ensure the conversation view no longer shows raw markdown or raw dict blobs for representative mixed-content messages.
- The repo already has message bubble unit tests and conversation Playwright coverage, so the new tests can extend existing patterns.

**Alternatives considered**:
- Rely only on UI tests: rejected because backend parsing behavior is the core risk area.
- Rely only on backend tests: rejected because markdown presentation and mobile-friendly rendering are frontend concerns.

---

## Summary Table

| Topic | Decision |
|-------|----------|
| Formatting boundary | Backend derives ordered render segments |
| Markdown renderer | `react-markdown` + `remark-breaks` |
| Unsupported structured payloads | Render labeled fallback blocks |
| Ordering model | `segments[]` referencing `attachments[]` by index |
| Verification | pytest + Vitest + Playwright |
