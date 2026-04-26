# Export Formatting Rectification Plan

## Current state (research summary)

### Frontend export flow
- Export actions in both single-conversation and batch flows download the API blob directly without any client-side transformation.
- The selected UI format labels (`markdown`, `json`, `html`, `csv`, `yaml`, `xml`, `excel`) are mapped to API format codes and then downloaded as-is.

### Backend export behavior
- Export endpoints support the full matrix of formats and route to format-specific exporters.
- The HTML exporter currently escapes message content directly (`escape(content)`) and places it in `.message-content`, so markdown links/code/lists are shown as markdown source instead of rendered HTML.
- JSON/YAML/XML/CSV exporters output structured data correctly for their file types, but `content` is the raw message text from the archive (typically markdown for assistant replies).

## Problem framing

What users perceive as "non-markdown exports exposing markdown" is primarily a content rendering issue:
- **Expected**: format-specific files should be idiomatic and human-usable.
- **Actual**: message bodies are mostly copied verbatim from source markdown into each format.

This is acceptable for machine-readable formats in some workflows (JSON/YAML/XML/CSV), but not ideal for human-readable outputs (especially HTML) where links and formatting should be rendered.

## Rectification goals

1. Keep current raw content fidelity available for programmatic use.
2. Produce user-friendly exports where markup is rendered when the target format supports it.
3. Ensure links are clickable in rendered targets.
4. Preserve security guarantees (escaping/sanitization).

## Proposed implementation plan

### Phase 1 (high impact, low risk): Fix HTML exporter rendering
1. Add a markdown-to-HTML rendering step for message content in `chatgpt_archive/exporters/html.py`.
2. Sanitize rendered HTML output using a strict allowlist (tags/attributes/protocols).
3. Replace the current `escape(content)` insertion with sanitized rendered HTML.
4. Add link styling (`a` selector) and safe defaults (`target="_blank"` with `rel="noopener noreferrer"` when appropriate).
5. Add tests for:
   - markdown link rendering to `<a href="...">`
   - code fences and inline code rendering
   - list/heading rendering
   - XSS blocking remains intact

### Phase 2 (optional compatibility extension): Dual-content fields for structured formats
For JSON/YAML/XML exports, include both:
- `content_raw` (existing canonical text)
- `content_rendered_html` (sanitized html fragment)

This avoids breaking consumers expecting raw content while enabling richer downstream rendering.

### Phase 3 (tabular formats): explicit strategy
For CSV/XLSX, choose one explicit model:
- **Option A (recommended default):** keep raw content column only for interoperability.
- **Option B:** add an additional `content_rendered_text` column with markdown stripped to readable plain text.

Do not embed raw HTML in CSV/XLSX by default.

## API and UI alignment updates

- Keep current format code mapping in `web/src/services/api.ts` (already correct).
- Update export UX copy in dialog/help text to clarify:
  - Markdown = source-native transcript
  - HTML = rendered transcript
  - JSON/YAML/XML = structured data (raw + optional rendered field once Phase 2 lands)

## Testing matrix

1. Unit tests for HTML exporter rendering + sanitization.
2. API tests asserting HTML export contains rendered anchors instead of markdown link syntax for representative messages.
3. Regression tests ensuring existing JSON/YAML/XML/CSV contracts remain stable unless Phase 2 is enabled.
4. E2E export smoke test can remain unchanged but should include one assertion around HTML content quality if fixtures permit.

## Rollout and compatibility notes

- Deliver Phase 1 first as a non-breaking quality fix.
- Gate Phase 2 behind a feature flag (or API query param) if strict backward compatibility is required.
- Document the semantic difference between `raw` and `rendered` message content in API docs/changelog.
