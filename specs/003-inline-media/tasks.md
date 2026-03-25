# Tasks: Inline Media in Conversation View

**Input**: Design documents from `/specs/003-inline-media/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/media-api.yaml, quickstart.md

**Tests**: Tests are included. Backend coverage extends the existing API test suite in `api/tests/`; frontend coverage extends Vitest component tests in `web/__tests__/components/` and Playwright conversation coverage in `web/__tests__/e2e/`.

**Organization**: Tasks are grouped by shared infrastructure and user story so each story can be implemented and verified independently once foundational work is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: Which user story the task belongs to (`US1`, `US2`, `US3`)
- Include exact file paths in each description

---

## Phase 1: Setup

**Purpose**: Align configuration, settings, routing, and fixtures with the approved design before feature work starts.

- [ ] T001 Add `archive_media_dir` support to persisted settings in `api/services/settings_service.py` and `api/routers/settings.py`
- [ ] T002 [P] Extend settings types and settings UI for archive media directory configuration in `web/src/types/index.ts`, `web/src/services/api.ts`, and `web/src/components/settings/SettingsForm.tsx`
- [ ] T003 [P] Create media router scaffold in `api/routers/media.py` and register it in `api/main.py`
- [ ] T004 [P] Add media-capable sample archive fixtures, ZIP fixtures, and helper builders in `api/tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared runtime parsing, media resolution, persistence, CLI coverage, and response contracts used by every story.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [ ] T005 Add runtime `Attachment` response models and extend `Message.attachments` in `api/models/responses.py`
- [ ] T006 [P] Create asset-pointer parsing, archive directory resolution, and media lookup service in `api/services/media_service.py`
- [ ] T007 [P] Add secure `conv_id` and `file_id` validation plus path traversal protection in `api/middleware/validation.py` and `api/routers/media.py`
- [ ] T008 Move archive media persistence into shared infrastructure by updating ZIP import flow in `api/services/archive_service.py` and import regression coverage in `api/tests/test_import.py`
- [ ] T009 Update conversation assembly in `api/services/archive_service.py` to resolve attachments at response time while preserving the text-only fast path
- [ ] T010 [P] Add CLI support for archive media verification and `CHATGPT_ARCHIVE_DIR` configuration in `chatgpt_archive/cli.py`
- [ ] T011 [P] Extend frontend attachment contracts and media helpers in `web/src/types/index.ts` and `web/src/services/api.ts`
- [ ] T012 [P] Add foundational backend coverage for attachment parsing, text stripping, and no-attachment behavior in `api/tests/test_conversations.py` and `api/tests/test_media.py`

**Checkpoint**: Shared media infrastructure is ready; image, file, and audio stories can proceed independently.

---

## Phase 3: User Story 1 - View Inline Images in Conversations (Priority: P1) 🎯 MVP

**Goal**: Images referenced by archive messages render inline in the conversation view instead of raw asset-pointer text.

**Independent Test**: Open a conversation containing uploaded or generated images and verify the images appear inline in the correct message position, with a placeholder when the file is missing.

### Implementation for User Story 1

- [ ] T013 [US1] Implement `GET /api/media/{conv_id}/{file_id}` for conversation-scoped media files in `api/routers/media.py`
- [ ] T014 [US1] Implement `sediment://` image resolution, MIME detection, dimensions mapping, and missing-file handling in `api/services/media_service.py`
- [ ] T015 [US1] Attach resolved image metadata to conversation responses in `api/services/archive_service.py` and `api/routers/conversations.py`
- [ ] T016 [P] [US1] Create inline image rendering with graceful fallback in `web/src/components/conversations/AttachmentImage.tsx`
- [ ] T017 [US1] Update `web/src/components/conversations/MessageBubble.tsx` to render ordered text-plus-image content without regressing text-only messages
- [ ] T018 [P] [US1] Add backend tests for conversation-scoped image serving, invalid IDs, and missing images in `api/tests/test_media.py`
- [ ] T019 [P] [US1] Add frontend component coverage for inline image rendering and image placeholders in `web/__tests__/components/MessageBubble.test.tsx`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Download or Preview Uploaded Files (Priority: P2)

**Goal**: Non-image attachments render as usable file cards with filename and open/download access.

**Independent Test**: Open a conversation with a PDF or document attachment and verify a named attachment card appears, opens or downloads correctly, and degrades gracefully when the file is absent.

### Implementation for User Story 2

- [ ] T020 [US2] Implement `GET /api/media/root/{file_id}` for root-level archive files in `api/routers/media.py`
- [ ] T021 [US2] Implement `file-service://` resolution, filename extraction, MIME detection, shared-root lookup, and content-disposition behavior in `api/services/media_service.py`
- [ ] T022 [US2] Extend runtime attachment assembly in `api/services/archive_service.py` to classify non-image assets as file attachments
- [ ] T023 [P] [US2] Create file attachment card UI with found and missing states in `web/src/components/conversations/AttachmentFile.tsx`
- [ ] T024 [US2] Update `web/src/components/conversations/MessageBubble.tsx` to render file cards inline with surrounding message content
- [ ] T025 [P] [US2] Add backend tests for root-level file serving, content-disposition headers, and missing files in `api/tests/test_media.py`
- [ ] T026 [P] [US2] Add frontend component coverage for file cards, download links, and missing-file indicators in `web/__tests__/components/MessageBubble.test.tsx`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Play Inline Audio (Priority: P3)

**Goal**: Audio attachments render as inline players inside the conversation flow.

**Independent Test**: Open a conversation with a voice recording attachment and verify an audio player appears inline, plays in place, and shows a fallback when the source file is missing.

### Implementation for User Story 3

- [ ] T027 [US3] Extend `sediment://` resolution in `api/services/media_service.py` to detect and classify audio files
- [ ] T028 [US3] Extend runtime attachment assembly in `api/services/archive_service.py` to return audio metadata alongside text and other attachments
- [ ] T029 [P] [US3] Create inline audio player with missing-file fallback in `web/src/components/conversations/AttachmentAudio.tsx`
- [ ] T030 [US3] Update `web/src/components/conversations/MessageBubble.tsx` to render audio attachments inline without breaking image and file layouts
- [ ] T031 [P] [US3] Add backend tests for audio attachment resolution and conversation-scoped audio serving in `api/tests/test_media.py`
- [ ] T032 [P] [US3] Add frontend component coverage for inline audio rendering and fallback states in `web/__tests__/components/MessageBubble.test.tsx`

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Validation

**Purpose**: Close the remaining documentation, mixed-content, settings, and performance gaps before implementation sign-off.

- [ ] T033 [P] Document the media endpoints and `Message.attachments` response contract in `docs/REST-API.md` and `docs/API.md`
- [ ] T034 [P] Document CLI media verification and archive media directory configuration in `docs/USAGE.md` and `README.md`
- [ ] T035 [P] Document local and Docker archive media directory setup in `docs/DEPLOYMENT.md` and `docker-compose.yml`
- [ ] T036 Add regression coverage for mixed text-plus-multiple-attachment ordering in `web/__tests__/components/MessageBubble.test.tsx` and `web/__tests__/e2e/conversation.spec.ts`
- [ ] T037 Add archive media directory settings and import-persistence regression coverage in `api/tests/test_settings.py`, `api/tests/test_import.py`, and `web/__tests__/services/api.test.ts`
- [ ] T038 Add performance-oriented validation for text-only conversations and conversations with 10+ attachments in `api/tests/test_conversations.py` and `api/tests/test_media.py`
- [ ] T039 Run backend validation for `api/tests/test_media.py`, `api/tests/test_conversations.py`, `api/tests/test_import.py`, and `api/tests/test_settings.py`
- [ ] T040 Run frontend validation for `web/__tests__/components/MessageBubble.test.tsx`, `web/__tests__/services/api.test.ts`, and `web/__tests__/e2e/conversation.spec.ts`
- [ ] T041 Run the end-to-end quickstart validation from `specs/003-inline-media/quickstart.md` against a real extracted archive

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKING
    ↓
┌───────────────┬───────────────┬───────────────┐
↓               ↓               ↓
US1             US2             US3
(P1)            (P2)            (P3)
↓               ↓               ↓
Phase 6 (Polish & Validation)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Inline Images) | Foundational | Phase 2 complete |
| US2 (File Cards) | Foundational | Phase 2 complete |
| US3 (Inline Audio) | Foundational | Phase 2 complete |

### Parallel Opportunities

- T002, T003, and T004 can run in parallel during Setup.
- T006, T007, T010, T011, and T012 can run in parallel once Phase 1 is in place.
- T016 and T018 can run in parallel after the image attachment contract is defined.
- T023 and T025 can run in parallel after root-level file resolution is implemented.
- T029 and T031 can run in parallel after audio classification is implemented.
- T033, T034, and T035 can run in parallel during Polish.

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Deliver User Story 1 as the MVP.
3. Validate image rendering, attachment stripping, and text-only fast path before expanding attachment types.

### Incremental Delivery

1. Add file attachment cards after conversation-scoped media serving is stable.
2. Add audio rendering once the shared `sediment://` resolver is proven.
3. Finish with settings coverage, CLI coverage, mixed-content regressions, and performance validation.

### Task Count Summary

- Total tasks: 41
- Setup: 4
- Foundational: 8
- US1: 7
- US2: 7
- US3: 6
- Polish & Validation: 9