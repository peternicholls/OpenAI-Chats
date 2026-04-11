# Sprint 004 Remediation Report

## Review Scope

- Compared the sprint task list in [specs/004-frontend-formatting/tasks.md](specs/004-frontend-formatting/tasks.md) against the implementation on branch `004-frontend-formatting`.
- Reviewed the design moodboard in [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html) as the intended visual baseline for transcript typography, `ThinkingBlock`, date separators, fallback styling, and image modal treatment.
- Reviewed the backend and frontend transcript-formatting code path.
- Ran focused validation:
  - Backend: `api/tests/test_formatting_service.py` and `api/tests/test_conversations.py` — 29 passed
  - Frontend unit tests: `MarkdownRenderer`, `MessageBubble`, `FallbackBlock`, and `api` client tests — 41 passed
  - Playwright: `web/__tests__/e2e/conversation.spec.ts` — 7 passed, 2 failed

## Moodboard Alignment

- Clearly aligned:
  - Code blocks include a header treatment with language label and copy affordance in [web/src/components/conversations/MarkdownRenderer.tsx](web/src/components/conversations/MarkdownRenderer.tsx), which matches the moodboard recommendation to keep the tighter transcript density but add the higher-value code-block polish in [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html#L924).
  - The date separator implementation in [web/src/components/conversations/DateSeparator.tsx](web/src/components/conversations/DateSeparator.tsx) follows the moodboard's recommended whisper-line direction described in [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html#L1297).
  - Fallback styling in [web/src/components/conversations/FallbackBlock.tsx](web/src/components/conversations/FallbackBlock.tsx) already distinguishes broken/malformed content from neutral unsupported content, which matches the moodboard's recommended two-severity approach in [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html#L1456).
- Partially aligned:
  - The image thumbnail and modal implementation broadly match the moodboard direction, but the test-selector contract around the thumbnail changed and was not propagated into Playwright.
  - `ThinkingBlock` is visually in the right family, but its wording diverges from the approved copy in the spec and moodboard context, and the collapsed state is more bordered than the moodboard's recommended minimal muted-background pill.
  - Transcript typography lands near the moodboard's preferred tight density, but the actual styling is split between the outer prose wrapper in [web/src/components/conversations/MessageBubble.tsx](web/src/components/conversations/MessageBubble.tsx#L177) and the inner renderer styles in [web/src/components/conversations/MarkdownRenderer.tsx](web/src/components/conversations/MarkdownRenderer.tsx#L67), which makes future tuning less controlled than the moodboard intended.
- Not yet embedded strongly enough in validation:
  - The report, tests, and acceptance checks were not previously explicit about using the moodboard as a baseline, so design intent was easy to lose once implementation started.

## Findings

### 1. Playwright acceptance coverage is currently red because the image test selectors no longer match the component

Severity: High

Evidence:

- The image component exposes `attachment-image-thumbnail-button` and `attachment-image-thumbnail`, not `attachment-image`: [web/src/components/conversations/AttachmentImage.tsx#L30](web/src/components/conversations/AttachmentImage.tsx#L30), [web/src/components/conversations/AttachmentImage.tsx#L37](web/src/components/conversations/AttachmentImage.tsx#L37)
- The Playwright suite still asserts `getByTestId('attachment-image')`: [web/__tests__/e2e/conversation.spec.ts#L119](web/__tests__/e2e/conversation.spec.ts#L119), [web/__tests__/e2e/conversation.spec.ts#L236](web/__tests__/e2e/conversation.spec.ts#L236)
- This directly breaks the sprint validation task: [specs/004-frontend-formatting/tasks.md#L128](specs/004-frontend-formatting/tasks.md#L128)

Impact:

- Sprint-level frontend validation is not complete.
- Two acceptance tests fail even though the underlying UI mostly works.
- This can hide real regressions because the E2E suite is already noisy/red.

Remediation:

- Update Playwright to target the thumbnail/button test IDs actually rendered, or restore a stable `attachment-image` test ID on the image wrapper and standardize around that.
- Re-run the full conversation E2E spec after the selector contract is corrected.

### 2. Required component test files for the new sprint primitives were not created

Severity: High

Evidence:

- The task list explicitly requires dedicated tests for `ThinkingBlock`, `DateSeparator`, and `ImageModal`: [specs/004-frontend-formatting/tasks.md#L36](specs/004-frontend-formatting/tasks.md#L36), [specs/004-frontend-formatting/tasks.md#L37](specs/004-frontend-formatting/tasks.md#L37), [specs/004-frontend-formatting/tasks.md#L38](specs/004-frontend-formatting/tasks.md#L38)
- The same files are named again in the frontend validation task: [specs/004-frontend-formatting/tasks.md#L128](specs/004-frontend-formatting/tasks.md#L128)
- There are currently no matching test files under [web/__tests__/components](web/__tests__/components)

Impact:

- Key sprint behavior is unvalidated:
  - Thinking block labels and expand/collapse behavior
  - Date separator rendering and boundary logic
  - Image modal open/close/backdrop/Escape/download behavior
- The task list shows these as required deliverables, so the implementation is incomplete even if the components exist.

Remediation:

- Add the three missing component test files.
- Extend them to cover the exact acceptance points named in the task list, especially the date-boundary rule and modal dismissal interactions.

### 3. `ThinkingBlock` does not fully match the approved spec and moodboard behavior

Severity: Medium

Evidence:

- Implemented labels are `Reasoned about this`, `Searched the web`, and `Reasoned and searched the web`: [web/src/components/conversations/ThinkingBlock.tsx#L7](web/src/components/conversations/ThinkingBlock.tsx#L7), [web/src/components/conversations/ThinkingBlock.tsx#L8](web/src/components/conversations/ThinkingBlock.tsx#L8), [web/src/components/conversations/ThinkingBlock.tsx#L9](web/src/components/conversations/ThinkingBlock.tsx#L9)
- The task/spec require `Reasoning`, `Searched the web`, and `Reasoning and web search`: [specs/004-frontend-formatting/tasks.md#L36](specs/004-frontend-formatting/tasks.md#L36)
- The collapsed pill currently uses both a border and a muted fill in [web/src/components/conversations/ThinkingBlock.tsx](web/src/components/conversations/ThinkingBlock.tsx#L23), while the moodboard recommendation was a minimal muted-background pill for the collapsed state, with the more structured border treatment reserved for the expanded state in [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html#L1115)

Impact:

- The UI does not match the approved product wording.
- The visual weight is slightly heavier than the chosen moodboard direction for a component that is supposed to preserve context without drawing attention.
- Any tests written later from the task/spec language will fail.
- This creates avoidable inconsistency in user-facing transcript UI.

Remediation:

- Change the collapsed pill labels to match the task/spec exactly.
- Simplify the collapsed pill toward the moodboard's minimal muted-background treatment and keep the more structured border emphasis for the expanded body only.
- Add the missing `ThinkingBlock` unit tests so this does not regress.

### 4. KaTeX preprocessing was implemented, but the required parse-error fallback path is still missing and untested

Severity: Medium

Evidence:

- Citation stripping and delimiter normalization exist: [web/src/components/conversations/MarkdownRenderer.tsx#L13](web/src/components/conversations/MarkdownRenderer.tsx#L13), [web/src/components/conversations/MarkdownRenderer.tsx#L20](web/src/components/conversations/MarkdownRenderer.tsx#L20)
- KaTeX is wired directly into the markdown pipeline: [web/src/components/conversations/MarkdownRenderer.tsx#L70](web/src/components/conversations/MarkdownRenderer.tsx#L70)
- The sprint task explicitly requires catching `\begin{...}...\end{...}` parse failures and falling back to labeled text instead of crashing or going blank: [specs/004-frontend-formatting/tasks.md#L67](specs/004-frontend-formatting/tasks.md#L67)

Impact:

- Unsupported LaTeX environments remain a likely runtime edge case.
- The current test suite does not cover math rendering at all, despite math being explicitly in scope.

Remediation:

- Add a guarded math-rendering fallback path for KaTeX parse errors.
- Add unit coverage for display math, inline math, mixed prose + math, and a failing `\begin{...}` fixture.

### 5. Frontend test fixtures and API docs were only partially updated for the new segment contract

Severity: Medium

Evidence:

- The MSW render-segment builder still excludes `thinking` from its allowed kinds: [web/__tests__/mocks/handlers.ts#L19](web/__tests__/mocks/handlers.ts#L19)
- The REST docs describe segment rules but do not document `thinking` segments alongside the other kinds: [docs/REST-API.md#L143](docs/REST-API.md#L143)
- The OpenAPI contract does include `ThinkingSegment`, so the repo docs are now out of sync with the actual contract: [specs/004-frontend-formatting/contracts/message-rendering-api.yaml](specs/004-frontend-formatting/contracts/message-rendering-api.yaml)

Impact:

- The test fixture layer makes it harder to add the required `ThinkingBlock` coverage.
- Documentation consumers can implement against an incomplete segment contract.

Remediation:

- Extend the MSW helpers to support `thinking` segments.
- Update REST/API docs to describe all segment kinds, including `thinking`, and the message-count/date-separator behavior introduced in this sprint.

### 6. Transcript typography is controlled in two layers, which makes the moodboard's reading-density guidance brittle to tune

Severity: Low

Evidence:

- The message container still applies a global prose wrapper in [web/src/components/conversations/MessageBubble.tsx](web/src/components/conversations/MessageBubble.tsx#L177)
- The markdown renderer also applies its own transcript typography in [web/src/components/conversations/MarkdownRenderer.tsx](web/src/components/conversations/MarkdownRenderer.tsx#L67)
- The moodboard recommendation was to start from the tighter transcript density and then tune spacing after seeing real content in-browser, which assumes there is a clearer single place to tune that density: [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html#L924)

Impact:

- Future density adjustments are more likely to become trial-and-error because prose spacing, heading scale, and margins are being influenced by both wrapper-level and renderer-level styles.
- This increases the chance of subtle regressions between markdown blocks, fallbacks, and attachments as the UI is polished.

Remediation:

- Consolidate transcript typography ownership in one layer, preferably the dedicated renderer and conversation primitives rather than a generic outer prose wrapper.
- Keep the wrapper responsible for layout spacing only, not markdown semantics.

## What Looks Complete

- Segment contracts were added in the backend and frontend types.
- Backend message assembly suppresses empty bootstrap assistant nodes, folds processing turns into `thinking` segments, and returns a user-visible `message_count` for conversation detail.
- Frontend segment-first rendering is in place in `MessageBubble`.
- Citation stripping, markdown formatting, image thumbnail + modal UI, date separators, and updated header date display are present.
- Focused backend and frontend unit tests currently pass.

## Missing Or Incomplete Against The Task List

- Missing dedicated tests for `ThinkingBlock`, `DateSeparator`, and `ImageModal`.
- Missing math-specific frontend tests required by T010 and T014a.
- Missing explicit frontend coverage for `ThinkingBlock` variants in mocks/helpers.
- Missing fully passing E2E validation for `web/__tests__/e2e/conversation.spec.ts`.
- Missing complete docs alignment for the expanded segment contract.
- Moodboard-driven design intent is still only partially encoded in tests and component structure.

## Recommended Remediation Order

1. Fix the Playwright selector mismatch so the current E2E suite is green again.
2. Add the three missing component test files and wire them into the frontend validation task.
3. Correct `ThinkingBlock` labels to the approved wording.
4. Simplify the collapsed `ThinkingBlock` styling to the chosen minimal moodboard direction.
5. Implement and test KaTeX parse-error fallback handling.
6. Expand MSW fixtures and docs to include `thinking` segments and the remaining sprint behaviors.
7. Consolidate transcript typography ownership so moodboard-driven tuning can happen in one place.

## Exit Criteria For Closing Sprint 004

- `web/__tests__/e2e/conversation.spec.ts` passes cleanly.
- `ThinkingBlock.test.tsx`, `DateSeparator.test.tsx`, and `ImageModal.test.tsx` exist and cover the behavior named in the task list.
- `ThinkingBlock` copy and collapsed-state styling match the approved spec and moodboard direction.
- Math rendering is covered by unit tests, including an unsupported-environment fallback case.
- Documentation matches the shipped segment contract, including `thinking` segments.