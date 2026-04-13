# Sprint 004 Remediation Report

## Review Scope

- Compared the sprint task list in [specs/004-frontend-formatting/tasks.md](specs/004-frontend-formatting/tasks.md) against the implementation on branch `004-frontend-formatting`.
- Verified against the current task-list revision, including the later hardening and validation additions T036, T037, and T039.
- Reviewed the design moodboard in [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html) as the intended visual baseline for transcript typography, `ThinkingBlock`, date separators, fallback styling, and image modal treatment.
- Reviewed and preserved the moodboard snapshot set in [specs/004-frontend-formatting/claude-opus-4.6/snapshots](specs/004-frontend-formatting/claude-opus-4.6/snapshots) so redesign work can be compared against fixed visual references instead of relying only on the source HTML.
- Reviewed the backend and frontend transcript-formatting code path, including the segment contract, fixture builders, renderer safety path, and conversation route layout.
- Re-ran focused validation on the current branch:
  - Backend: `tests/api/test_formatting_service.py` and `tests/api/test_conversations.py` — 29 passed
  - Frontend unit tests: `MarkdownRenderer`, `MessageBubble`, `FallbackBlock`, and `api` client tests — 41 passed
  - Playwright: `web/__tests__/e2e/conversation.spec.ts` — 7 passed, 2 failed
- Distinguished between:
  - task-list-backed implementation or validation gaps
  - broader moodboard-alignment recommendations that go beyond explicit checklist wording

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

## Scope Correction

- The style gap between the moodboard and the localhost transcript view should no longer be treated as a narrow component-polish issue.
- The current mismatch is broader than `ThinkingBlock`, date separators, or markdown styling. It is also shaped by page-level layout, surrounding app chrome, generic prose wrappers, and div-heavy transcript structure.
- Remediation should therefore be allowed to redesign:
  - conversation-route layout and spacing
  - transcript container structure
  - message bubble semantics and hierarchy
  - page-local typography and spacing tokens
  - header and surrounding chrome as it affects reading focus
- In practice, this means sprint follow-up work should not be constrained to tiny className edits in the existing components if those components are the wrong structural starting point.

## Reference Assets

- Source moodboard: [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html)
- Full-page snapshot: [specs/004-frontend-formatting/claude-opus-4.6/snapshots/00-moodboard-full.png](specs/004-frontend-formatting/claude-opus-4.6/snapshots/00-moodboard-full.png)
- Section snapshots:
  - [specs/004-frontend-formatting/claude-opus-4.6/snapshots/01-header.png](specs/004-frontend-formatting/claude-opus-4.6/snapshots/01-header.png)
  - [specs/004-frontend-formatting/claude-opus-4.6/snapshots/02-decision-1-typography.png](specs/004-frontend-formatting/claude-opus-4.6/snapshots/02-decision-1-typography.png)
  - [specs/004-frontend-formatting/claude-opus-4.6/snapshots/03-decision-2-thinking-block.png](specs/004-frontend-formatting/claude-opus-4.6/snapshots/03-decision-2-thinking-block.png)
  - [specs/004-frontend-formatting/claude-opus-4.6/snapshots/04-decision-3-date-separators-header.png](specs/004-frontend-formatting/claude-opus-4.6/snapshots/04-decision-3-date-separators-header.png)
  - [specs/004-frontend-formatting/claude-opus-4.6/snapshots/05-decision-4-attachments-fallbacks.png](specs/004-frontend-formatting/claude-opus-4.6/snapshots/05-decision-4-attachments-fallbacks.png)
  - [specs/004-frontend-formatting/claude-opus-4.6/snapshots/06-decision-matrix.png](specs/004-frontend-formatting/claude-opus-4.6/snapshots/06-decision-matrix.png)
- These should be treated as the visual comparison set for future redesign snapshots and review passes.

## Task Verification Summary

- Verified as implemented on this branch:
  - T001: markdown and math dependencies are present in `web/package.json`
  - T003: `ThinkingSegment` is present in the runtime response models and frontend types
  - T005, T005b, T005c: `MarkdownRenderer`, `FallbackBlock`, `DateSeparator`, `ImageModal`, and thumbnail-based `AttachmentImage` exist
  - T013 and T013a: segment-first message rendering, date separators, and header date updates are present
  - FR-020 implementation appears present in `api/services/archive_service.py`: the conversation detail response computes `message_count` from the number of visible rendered messages rather than raw DB rows
  - T014b: citation-token stripping is implemented in the markdown pre-processing step
  - SC-012a implementation appears present in `AttachmentImage`: the inline thumbnail classes are `h-32 w-48`, which corresponds to 128 × 192 px and satisfies the spec's smaller-than-200 × 150 requirement
  - Part of T036 and T037: raw HTML is currently rendered inertly and the frontend renderer does not use `rehype-raw` or `dangerouslySetInnerHTML`
- Implemented but incomplete against the original task wording:
  - T005a: `ThinkingBlock` exists, but the collapsed labels do not match the approved wording and the required dedicated tests are missing
  - T005b and T005c: the components exist, but their required dedicated test files are missing
  - FR-015, FR-016, FR-020, and SC-010: backend suppression/grouping/message-count logic appears to exist, but the remediation report did not previously call out that dedicated acceptance-style coverage for hidden nodes, bootstrap suppression, thinking grouping, and zero `[No content]` regressions is still not evident from the current focused test set
  - T014a: KaTeX is wired in, but the required parse-error fallback for unsupported `\begin{...}` environments is not evident and the required math tests are missing
  - T015, T017, T028, and T033: browser validation is still red because Playwright targets a stale image selector contract
  - T029: docs are not fully aligned with the shipped `thinking` segment contract
  - FR-011 and SC-006: some source-parity checks exist, but the report did not previously carry source-parity forward as an explicit remediation and closure item
  - FR-008: plain-text readability has unit-level coverage, but the report did not previously track plain-text regression prevention as an explicit remediation concern
  - FR-010 and SC-007: the report noted inert raw HTML handling, but it did not previously make clear that broader unsafe-content acceptance-fixture coverage remains incomplete
  - T039: the quickstart and validation surface have not been updated to explicitly cover the hardening scenarios added late in the sprint
- Not directly required by a single checklist line, but still material to closing the visual gap:
  - route-level shell pressure, transcript semantics, and typography ownership remain the largest reasons the localhost view does not yet read like the moodboard

## Verified Findings

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

### 7. The localhost conversation view is still dominated by application chrome rather than the moodboard's reading-first transcript surface

Severity: Medium

Evidence:

- The route is still rendered inside the generic app shell with sticky top header and sidebar in [web/src/app/layout.tsx](web/src/app/layout.tsx) and uses the global header in [web/src/components/layout/Header.tsx](web/src/components/layout/Header.tsx) plus the sidebar in [web/src/components/layout/Sidebar.tsx](web/src/components/layout/Sidebar.tsx)
- The conversation page itself is a simple `max-w-4xl mx-auto` container in [web/src/app/conversation/[id]/page.tsx](web/src/app/conversation/[id]/page.tsx#L89)
- The moodboard is composed around a calmer, transcript-first reading surface with lighter framing and clearer sectional hierarchy, not an admin-dashboard shell pressing in on the content: [specs/004-frontend-formatting/claude-opus-4.6/index.html](specs/004-frontend-formatting/claude-opus-4.6/index.html)

Impact:

- Even when individual conversation components improve, the overall page still feels visually different from the moodboard because the shell and spacing system communicate a different product posture.
- This is likely the main reason the localhost view still reads as mismatched from a user perspective.

Remediation:

- Allow a broader redesign of the conversation route presentation instead of limiting changes to transcript internals.
- Consider a conversation-specific layout treatment that reduces shell competition and gives the transcript more visual priority.
- Re-evaluate spacing, width, background treatment, and sticky header behavior at the route level, not only inside bubbles.

### 8. The transcript markup is too generic to support the moodboard's more intentional reading experience cleanly

Severity: Medium

Evidence:

- The conversation page is assembled mostly from generic `div` containers in [web/src/app/conversation/[id]/page.tsx](web/src/app/conversation/[id]/page.tsx) and [web/src/components/conversations/MessageBubble.tsx](web/src/components/conversations/MessageBubble.tsx)
- The current structure does not use richer transcript semantics such as `article`, `header`, `section`, `ol`, `li`, or `time` for message chronology and transcript grouping.
- The user explicitly called out that the mismatch may come from the original scope being too tight to redesign wider CSS and semantic HTML, which matches what the current structure suggests.

Impact:

- Styling has to fight generic wrappers instead of working with meaningful structure.
- It is harder to build a transcript that feels like a designed reading surface when the DOM hierarchy does not express transcript semantics.
- Accessibility and future design iteration both suffer when chronology and message structure are represented only as nested `div`s.

Remediation:

- Loosen implementation bounds to allow semantic restructuring of the conversation page and message list.
- Use semantic containers where they improve transcript readability and styling control, especially around conversation metadata, date groupings, and message chronology.
- Treat transcript semantics as part of the design fix, not as optional cleanup.

## Additional Verification Notes

- T036 and T037 are only partially represented in the current report if treated as explicit sprint obligations:
  - Frontend safety posture is materially better than the original report made explicit. `MarkdownRenderer` does not enable raw HTML execution paths, and `FallbackBlock` renders label and body text as plain React text.
  - However, the task-list expectation is broader than current evidence. The frontend has a raw-HTML unit test, but the late-sprint unsafe-content coverage and quickstart updates are not clearly represented as completed deliverables across backend, frontend, and documentation.
- Findings 6 through 8 should be read as design-remediation scope guidance, not as literal assertions that a specific checkbox task failed. They explain why the current implementation can satisfy many component-level tasks while still feeling visually off against the moodboard.

## Spec Cross-check Additions

- The spec adds a few closure expectations that should remain explicit in remediation even where implementation appears present:
  - FR-020: visible-message counting must be treated as a verified acceptance item, not only an implementation detail
  - SC-010: the report should continue to track zero `[No content]` regressions for thinking/search conversations and explicit suppression of hidden system-style turns
  - FR-011 and SC-006: source parity between generated assistant content and imported historical content should remain in the remediation closure set
  - FR-008: plain-text conversations should remain an explicit non-regression concern during redesign work
  - SC-012: thumbnail size is implemented, but modal interactions and size behavior still need dedicated validation coverage
  - SC-007: unsafe-content handling needs broader acceptance-fixture proof than the current raw-HTML spot check alone

## What Looks Complete

- Segment contracts were added in the backend and frontend types.
- Backend message assembly suppresses empty bootstrap assistant nodes, folds processing turns into `thinking` segments, and returns a user-visible `message_count` for conversation detail.
- Frontend segment-first rendering is in place in `MessageBubble`.
- Citation stripping, markdown formatting, image thumbnail + modal UI, date separators, and updated header date display are present.
- Focused backend and frontend unit tests currently pass.
- Frontend renderer hardening is partly in place: raw HTML currently renders as inert text and no unsafe markdown plugin is enabled.

## Missing Or Incomplete Against The Task List

- Missing dedicated tests for `ThinkingBlock`, `DateSeparator`, and `ImageModal`.
- Missing math-specific frontend tests required by T010 and T014a.
- Missing the task-required `ThinkingBlock` copy alignment: the implemented labels differ from the approved wording in T005a.
- Missing explicit frontend coverage for `ThinkingBlock` variants in mocks/helpers.
- Missing explicit acceptance-style coverage for visible-message counting, hidden-node suppression, thinking-turn grouping, and zero `[No content]` regressions in thinking/search conversations.
- Missing fully passing E2E validation for `web/__tests__/e2e/conversation.spec.ts`.
- Missing complete docs alignment for the expanded segment contract.
- Missing explicit remediation tracking for source-parity validation between generated and imported content.
- Missing broader unsafe-content acceptance coverage beyond the current inert raw-HTML spot check.
- Missing explicit non-regression coverage language for plain-text conversations during redesign follow-up.
- Missing explicit quickstart and validation updates for the late hardening tasks T036, T037, and T039.
- Moodboard-driven design intent is still only partially encoded in tests and component structure.
- The current scope is too narrow to fully close the observed localhost-versus-moodboard visual gap.

## Recommended Remediation Order

1. Fix the Playwright selector mismatch so the current E2E suite is green again.
2. Add the three missing component test files and wire them into the frontend validation task.
3. Correct `ThinkingBlock` labels to the approved wording.
4. Simplify the collapsed `ThinkingBlock` styling to the chosen minimal moodboard direction.
5. Implement and test KaTeX parse-error fallback handling.
6. Expand MSW fixtures, docs, and quickstart coverage to include `thinking` segments and the late unsafe-content validation scenarios.
7. Record the current frontend safety posture explicitly as part of T037, then add any missing backend/frontend hardening coverage required by T036 and T039.
8. Consolidate transcript typography ownership so moodboard-driven tuning can happen in one place.
9. Widen the allowed redesign scope from component-local styling to conversation-route layout, shell interaction, and semantic transcript markup.

## Concrete Remediation Checklist

### Immediate unblockers

- [ ] Fix the stale image selector contract in `web/__tests__/e2e/conversation.spec.ts` so Playwright targets the current thumbnail/button test IDs, or restore a stable wrapper test ID in `web/src/components/conversations/AttachmentImage.tsx`.
- [ ] Re-run `web/__tests__/e2e/conversation.spec.ts` and confirm the suite is green again. This closes the current T015/T017/T028/T033 blocker.

### Missing sprint deliverables

- [ ] Add `web/__tests__/components/ThinkingBlock.test.tsx` covering all three `activityType` labels plus expand/collapse behavior required by T005a and T010.
- [ ] Add `web/__tests__/components/DateSeparator.test.tsx` covering formatted date rendering plus the no-separator-before-first-message boundary required by T005b and T013a.
- [ ] Add `web/__tests__/components/ImageModal.test.tsx` covering open, close button, backdrop click, Escape dismissal, download link, and metadata presence/absence required by T005c.
- [ ] Update `web/src/components/conversations/ThinkingBlock.tsx` to match the approved labels: `Reasoning`, `Searched the web`, and `Reasoning and web search`.
- [ ] Simplify the collapsed `ThinkingBlock` visual treatment to match the moodboard’s lighter pill direction.
- [ ] Add math fixtures to `web/__tests__/components/MarkdownRenderer.test.tsx` for display math, inline math, mixed prose + math, and a failing `\begin{...}` case.
- [ ] Implement the missing KaTeX parse-error fallback behavior in `web/src/components/conversations/MarkdownRenderer.tsx` so unsupported environments degrade to labeled text instead of blank output or runtime failure.
- [ ] Add or expand backend/frontend acceptance coverage for FR-015, FR-016, FR-020, and SC-010 so hidden nodes, bootstrap suppression, thinking grouping, visible-message counting, and zero `[No content]` regressions are explicitly verified.
- [ ] Preserve explicit plain-text non-regression coverage during remediation so FR-008 remains demonstrably satisfied.

### Contract, docs, and hardening follow-up

- [ ] Extend `web/__tests__/mocks/handlers.ts` so mock render segments support `thinking` and related coverage paths.
- [ ] Update `docs/REST-API.md` and any related API docs to describe all segment kinds, including `thinking`, plus the message-count/date-separator behavior shipped in this sprint.
- [ ] Keep source-parity validation explicit in the remediation closure set so FR-011 and SC-006 are not lost during follow-up work.
- [ ] Audit T036/T037 coverage explicitly: keep the raw-HTML safety assertions, verify no unsafe markdown plugins have been introduced, and document the current renderer safety posture in the report or completion notes.
- [ ] Broaden unsafe-content acceptance coverage so SC-007 is evidenced by more than a single inert raw-HTML case.
- [ ] Update `specs/004-frontend-formatting/quickstart.md` and validation references so T039’s unsafe-content and source-parity checks are represented in the closure criteria.

### Design-remediation scope

- [ ] Consolidate transcript typography ownership so density and spacing tuning happen in one place instead of both `MessageBubble` and `MarkdownRenderer`.
- [ ] Decide whether the conversation route should get a conversation-specific layout treatment that reduces header/sidebar competition with the transcript.
- [ ] Restructure the transcript markup toward semantic containers where they improve chronology, readability, and styling control.

## Exit Criteria For Closing Sprint 004

- `web/__tests__/e2e/conversation.spec.ts` passes cleanly.
- `ThinkingBlock.test.tsx`, `DateSeparator.test.tsx`, and `ImageModal.test.tsx` exist and cover the behavior named in the task list.
- `ThinkingBlock` copy and collapsed-state styling match the approved spec and moodboard direction.
- Math rendering is covered by unit tests, including an unsupported-environment fallback case.
- Documentation matches the shipped segment contract, including `thinking` segments.
- Visible-message counting, hidden-node suppression, thinking grouping, and zero `[No content]` regressions are explicitly covered in acceptance-style validation.
- Source-parity and plain-text non-regression checks remain green after remediation work.
- Validation and quickstart coverage explicitly include the unsafe-content and source-parity checks added late in the sprint.
- The conversation route as rendered on localhost presents a transcript-first reading experience that is recognizably aligned with the moodboard at the page level, not just at the component level.