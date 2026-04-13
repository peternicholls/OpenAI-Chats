# Sprint 004 Remediation Report

## Reconciliation Basis

This report reflects the current state of branch `004-frontend-formatting` as reviewed on 13 April 2026 against:

- the current task tracker in `specs/004-frontend-formatting/design-improvement-tasks.md`
- the actual code paths used by the live conversation route
- the localhost browser rendering observed during review

The review was grounded in the current active route implementation, not older report language.

## Evidence Reviewed

### Code paths

- `web/src/app/conversation/[id]/page.tsx`
- `web/src/components/conversations/AssistantTurn.tsx`
- `web/src/components/conversations/MessageBubble.tsx`
- `web/src/components/conversations/MarkdownRenderer.tsx`
- `web/src/components/conversations/ThinkingBlock.tsx`
- `web/src/components/conversations/ToolBlock.tsx`
- `web/src/components/layout/Sidebar.tsx`
- `api/services/archive_service.py`

### Browser evidence

- Home/index view at `http://localhost/`
- Conversation view for `Pub Manager Conflict`
- Conversation view for `Laravel SQL Conversion`

## Current Status Summary

### Confirmed complete

- T001: Fixture and test coverage groundwork exists for markdown-oriented transcript rendering.
- T002: The codebase has now been reviewed against the design notes and the gaps are documented here.

### Confirmed in progress

- T003: Code blocks currently have a copy affordance and a header row, but syntax highlighting is not yet actually implemented in the live renderer.

### Confirmed not yet complete

- T004 to T028 remain incomplete or only partially represented in code or browser behavior.
- Some supporting implementation exists outside the task statuses, but the browser still shows major design-note gaps.

## What Is Actually Shipping

### Transcript and formatting progress that is real

- Segment-based transcript rendering is active in the conversation route.
- Basic markdown rendering is active.
- KaTeX preprocessing for ChatGPT delimiter normalization is present.
- Date-aware conversation headers are present.
- `ThinkingBlock`, `ToolBlock`, `DateSeparator`, `AttachmentImage`, and `ImageModal` components exist.
- Dedicated tests now exist for `ThinkingBlock`, `DateSeparator`, and `ImageModal`.

### Browser-visible evidence of progress

- The `Pub Manager Conflict` conversation renders readable formatted transcript content rather than raw markdown.
- The conversation header shows start date and updated date behavior.
- Assistant content renders headings and lists with clear formatting.

## Current Gaps Against The Design Tasks

### 1. Tool activity is still too noisy in real conversations

The `Laravel SQL Conversion` localhost screenshot shows a long vertical stack of repeated `Tool call` pills.

This matches the current route implementation:

- `AssistantTurn` renders every `tool` role message as a standalone `ToolBlock`.
- The route therefore still exposes internal processing noise in tool-heavy conversations instead of producing a calmer condensed reading flow.

Implication:

- Transcript readability is still materially off in important real-world conversations.
- The current browser behavior does not yet satisfy the design intent for low-noise conversational reading.

### 2. Code block work is only partial

`MarkdownRenderer` currently provides:

- a code-block header
- a language label
- a copy button

But it still renders plain code text and still uses horizontal overflow.

Current code state:

- no actual syntax-highlighting renderer is used in the component
- code blocks still rely on `overflow-x-auto`
- the current block surface remains a hard-coded dark slate treatment rather than the intended lighter, note-driven treatment

Implication:

- T003 is correctly marked in progress, not complete.
- T004, T005, T006, and T007 should remain open.

### 3. Turn-level actions are not live in the active conversation path

Neither active turn-rendering path mounts end-of-turn copy or text-to-speech actions:

- `MessageBubble` renders content only
- `AssistantTurn` renders segment output only

Implication:

- T012 is not started in shipped behavior.
- T013 and T014 also remain open.

### 4. Sidebar and conversation-list redesign is not live

The home screenshot shows:

- the search box remains in the top banner instead of in the sidebar
- the sidebar still includes a static `Search` navigation link
- tags are still rendered in the sidebar footer region
- conversation cards still show metadata by default instead of title-first presentation

Implication:

- T019 through T025 remain open in real browser behavior.
- The current shell still reads like the pre-redesign app structure rather than the design-note direction.

### 5. The previous remediation report was stale

The previous version of this file no longer matched the branch state. It incorrectly claimed some tests were missing even though dedicated tests for `ThinkingBlock`, `DateSeparator`, and `ImageModal` are now present.

Implication:

- This report should now be treated as the source of truth for current remediation status.
- Older findings based on missing component tests should be discarded.

## Reconciled Task Interpretation

### Phase 1

- T001: done
- T002: done

### Phase 2

- T003: partial and still in progress
- T004: not done
- T005: not done
- T006: not done
- T007: not done

### Phase 3

- T008: not done
- T009: not done
- T010: not done
- T011: not done

### Phase 4

- T012: not done
- T013: not done
- T014: not done

### Phase 5

- T015: not done
- T016: not done
- T017: not done
- T018: not done

### Phase 6

- T019: not done
- T020: not done
- T021: not done
- T022: not done
- T023: not done
- T024: not done
- T025: not done

### Phase 7

- T026: not done
- T027: not done
- T028: not done

## Notes On Active Rendering Paths

The branch currently contains more than one transcript rendering path, and that matters for progress tracking.

- `MessageBubble.tsx` contains one segment-aware message renderer.
- The active conversation route also uses `AssistantTurn.tsx` to group assistant and tool messages into turns.

This means status should always be judged against the route-level browser output, not from reading a single component in isolation.

## Recommended Next Work Order

1. Collapse or otherwise reduce repeated tool-role output so the active route no longer renders long stacks of `Tool call` pills.
2. Finish code-block rendering properly: syntax highlighting, lighter surface treatment, wrapping, and line-number behavior.
3. Add turn-level actions and long-user-prompt handling to the active conversation route.
4. Move sidebar search and implement the conversation-list redesign in the live shell.
5. Re-run browser review and then update task statuses only after those behaviors are visible on localhost.

## Progress Tracking Rule Going Forward

Do not mark a task complete based on component existence alone.

A task should only move to complete when:

- the active localhost route shows the behavior
- the relevant tests cover it where appropriate
- the behavior matches the design-note intent closely enough to survive browser review
