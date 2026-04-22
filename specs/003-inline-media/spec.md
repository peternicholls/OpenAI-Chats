# Feature Specification: Inline Media in Conversation View

**Feature Branch**: `003-inline-media`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "the data downloaded from openai includes files, images, and other resources, that should be linked with each chat and show inline within conversations. Currently the webui just shows file names etc. we need to handle this efficiently. it would be ideal not to change the database, otherwise when we append new data it could get out of sync — but we also don't want unnecessary complexity."

## Context

The OpenAI export archive (`conversations.json`) contains message content parts that reference media assets via two URI schemes:

- **`sediment://file_{hex_id}`** — user-uploaded images and audio files, stored on disk at `{conv_id}/image/file_{hex_id}-{uuid}.{ext}` or `{conv_id}/audio/file_{hex_id}-{uuid}.{ext}` relative to the archive directory.
- **`file-service://file-{short_id}`** — files (images, PDFs, documents) uploaded to a conversation, stored at the root of the archive directory as `file-{short_id}-{original_name}.{ext}`.

The importer currently stores message content as plain text, converting all content parts (including structured attachment objects) to their string representation. The web UI renders this string as-is, so users see raw text like `{'content_type': 'image_asset_pointer', 'asset_pointer': 'file-service://file-ABC', ...}` instead of the actual image or a usable file link.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
-->

### User Story 1 - View Inline Images in Conversations (Priority: P1)

A user opens a conversation in which they or the assistant shared images. Instead of seeing raw file references or placeholder text, they see the actual images rendered inline within the conversation flow — exactly where they appeared in the original chat.

**Why this priority**: Images are the most common type of media attachment and the most jarring failure in the current UI. Resolving them gives immediate, high-visibility value for the majority of affected conversations.

**Independent Test**: Can be fully tested by opening any conversation that contains an uploaded or DALL-E generated image and verifying the image renders inline in the correct message position.

**Acceptance Scenarios**:

1. **Given** a conversation containing a user-uploaded image, **When** a user opens that conversation, **Then** the image is displayed inline within the user's message bubble at the correct position.
2. **Given** a conversation containing an AI-generated (DALL-E) image, **When** a user opens that conversation, **Then** the generated image is displayed inline within the assistant's message bubble.
3. **Given** a message containing both text and an image, **When** the conversation is viewed, **Then** the text and image are both visible in the correct order, neither overriding the other.
4. **Given** a conversation where the source image file is missing from the archive, **When** the user opens the conversation, **Then** a clear placeholder with the original filename is shown instead of the image, and the rest of the conversation renders normally.

---

### User Story 2 - Download or Preview Uploaded Files (Priority: P2)

A user opens a conversation where they uploaded a non-image file (PDF, spreadsheet, code file, etc.). Instead of seeing garbled text representing the file reference, they see a clearly labelled file attachment card with the original filename and a way to open or download the file.

**Why this priority**: Documents, PDFs and code files are common in research and analysis conversations. While images are higher priority, file attachments represent a distinct and important class of media that many users rely on for context.

**Independent Test**: Can be fully tested by opening a conversation with an uploaded PDF or document and verifying a named, downloadable attachment card appears in place of the raw file reference.

**Acceptance Scenarios**:

1. **Given** a conversation where the user uploaded a PDF document, **When** the conversation is viewed, **Then** a file attachment card shows the original filename, file type indicator, and a way to access the file.
2. **Given** a file attachment in a message, **When** the user interacts with the attachment card, **Then** the file opens or downloads without leaving the conversation view.
3. **Given** a file whose source is missing from the archive, **When** the conversation is viewed, **Then** the attachment card shows the filename with a "file not found" indicator rather than crashing or hiding the card entirely.

---

### User Story 3 - Play Inline Audio (Priority: P3)

A user opens a conversation that included voice input or audio output. The audio clip appears as a playable audio widget inline in the conversation, rather than as unreadable text.

**Why this priority**: Audio attachments are less common than images or documents, but archive exports do include voice recordings. This rounds out full media support and is a low-scope addition once the core media-serving infrastructure is in place.

**Independent Test**: Can be fully tested by opening a "Fair rent" or "Time machine preservation plan" conversation (both contain audio attachments) and verifying an audio player renders in place of the raw reference.

**Acceptance Scenarios**:

1. **Given** a conversation containing a voice recording, **When** the conversation is viewed, **Then** an inline audio player is shown at the correct position in the message.
2. **Given** the user presses play on the audio widget, **When** the audio plays, **Then** it streams or loads without navigating away from the conversation.
3. **Given** an audio file missing from the archive, **When** the conversation is viewed, **Then** a placeholder indicating the missing audio clip is shown instead of the player.

---

### Edge Cases

- What happens when a message contains multiple attachments (e.g., several images and a PDF)?
- How does the system handle archive directories that have not yet been imported or whose path has changed?
- What if the same `file-service` ID appears in multiple conversations — is the root-level file shared, and is that handled consistently?
- What happens with very large images or audio files — is there a performance concern when loading many at once in a long conversation?
- How are DALL-E generated images (which may have both an image asset pointer and metadata) distinguished from user-uploaded images in display?
- What happens for conversations where the archive subdirectory exists but the specific file within it does not (partial export)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST serve archive media files (images, audio, documents) via a dedicated API endpoint, resolving `sediment://` and `file-service://` URI schemes to actual files on disk without modifying the database.
- **FR-002**: The API endpoint MUST validate all requested file paths to ensure they resolve strictly within the archive directory, preventing path traversal or access to unrelated system files.
- **FR-003**: The API MUST parse message content at response time, identifying and resolving asset pointer references into structured attachment metadata (resolved URL, filename, media type, dimensions where available), returning this alongside the existing plain-text content field.
- **FR-004**: For `sediment://file_{hex_id}` pointers, the system MUST locate the corresponding file by matching the hex ID against files in the conversation's `image/` or `audio/` subdirectory within the archive.
- **FR-005**: For `file-service://file-{id}` pointers, the system MUST locate the corresponding file by matching the short ID against root-level files in the archive directory.
- **FR-006**: The web UI MUST render resolved image attachments inline within the message bubble, at the correct position relative to any accompanying text.
- **FR-007**: The web UI MUST render non-image file attachments as named download/preview cards within the message bubble.
- **FR-008**: The web UI MUST render audio attachments as inline playable audio widgets.
- **FR-009**: When an archive file cannot be found, the system MUST display a graceful placeholder (showing the original filename or pointer ID) rather than hiding the attachment or breaking the message display.
- **FR-010**: The database schema MUST NOT be modified. All attachment resolution MUST happen at runtime from the archive directory and the existing message content stored in the database.
- **FR-011**: The system MUST NOT require a full re-scan or re-index of the archive directory on startup; individual file lookups MUST be performed on demand per request.
- **FR-012**: The system MUST handle conversations where no media attachments exist without any performance overhead or UI change.

### Key Entities

- **Asset Pointer**: A URI embedded in message content parts referencing a media file. Two schemes: `sediment://file_{hex_id}` (conv-scoped) and `file-service://file-{short_id}` (archive root-scoped).
- **Archive Directory**: The on-disk folder produced by an OpenAI data export. Contains `conversations.json`, root-level uploaded files (`file-{id}-{name}.{ext}`), and per-conversation subdirectories (`{conv_id}/image/`, `{conv_id}/audio/`).
- **Resolved Attachment**: Runtime-derived metadata containing a servable URL, original filename, MIME type, and optional dimensions — derived from an asset pointer without touching the database.
- **Media Endpoint**: A new API route that accepts a file identity (conv ID + file ID or root-level file ID) and returns the binary file content with appropriate headers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every image present in the archive and referenced by a conversation message renders as an actual image in the web UI — zero conversations display raw asset pointer text for image attachments.
- **SC-002**: Every file attachment referenced in a conversation message displays as a named, accessible file card — users can retrieve the original file without leaving the conversation view.
- **SC-003**: Every audio attachment referenced in a conversation message renders as a playable audio widget.
- **SC-004**: Opening a conversation with 10 or more media attachments adds no perceptible delay compared to opening a text-only conversation of equivalent message count.
- **SC-005**: A missing or inaccessible archive file never causes a conversation to fail to load or render incorrectly — a placeholder is shown without affecting surrounding messages.
- **SC-006**: Importing a new export archive and viewing its conversations shows media inline with no additional configuration steps required from the user.
- **SC-007**: The feature works correctly across all archive formats currently produced by OpenAI export (images in conv subdirectories, files at archive root, audio in conv subdirectories).

## Assumptions

- The archive directory path is already configured and accessible to the API at runtime (consistent with how the importer currently accesses it).
- File naming conventions in the OpenAI export are stable: `sediment://file_{hex_id}` URIs map to files whose names begin with `file_{hex_id}`, and `file-service://file-{id}` URIs map to root-level files beginning with `file-{id}-`.
- The database `content` column stores message parts as Python string representations of the original JSON objects (e.g. `"{'content_type': 'image_asset_pointer', ...}"`) due to current importer behaviour — parsing of these strings at response time is acceptable.
- No CDN or external image proxy is required; serving files directly from the local archive directory over the existing API is sufficient for local/self-hosted deployment.
- Maximum individual file size in the archive is manageable for direct streaming; no chunked upload or range-request handling is required for MVP.
- The feature is scoped to the archive data already on disk; it does not re-fetch or re-download files from OpenAI's servers.

