# Feature Specification: ChatGPT Archive Search & Export

**Feature Branch**: `001-archive-search-export`  
**Created**: 2026-01-26  
**Status**: Draft  
**Input**: User description: "Archive and search ChatGPT conversations with multi-format export - store in fast accessible database, search via CLI or interface, view chats, export to MD/XML/HTML/JSON/YAML"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import Archive into Database (Priority: P1)

As a user with a ChatGPT export archive, I want to import all my conversations into a searchable database so that I can quickly access my conversation history without parsing large JSON files each time.

**Why this priority**: Without import, no other functionality is possible. This is the foundation that enables all search and export capabilities.

**Independent Test**: Can be fully tested by running the import command on the archive directory and verifying conversations are accessible in the database. Delivers immediate value by making 1,778 conversations queryable.

**Acceptance Scenarios**:

1. **Given** a valid ChatGPT export directory, **When** user runs the import command, **Then** all conversations are stored in the database with their metadata (title, dates, message count)
2. **Given** an already-imported archive, **When** user runs import again, **Then** the operation is idempotent (no duplicates, updated conversations are refreshed)
3. **Given** import completes successfully, **When** user queries conversation count, **Then** the count matches the source archive
4. **Given** a corrupted or invalid JSON file, **When** user runs import, **Then** clear error message is displayed and partial imports are handled gracefully

---

### User Story 2 - Search Conversations (Priority: P2)

As a user with imported conversations, I want to search across all my chats by keyword, phrase, or date range so that I can quickly find specific discussions without manually browsing.

**Why this priority**: Search is the primary value proposition—finding information in a large archive. Without search, users must still browse manually.

**Independent Test**: Can be fully tested by searching for a known term and verifying matching conversations are returned with context previews.

**Acceptance Scenarios**:

1. **Given** an imported database, **When** user searches for a keyword, **Then** matching conversations are listed with title, date, and relevant message preview
2. **Given** multiple matches exist, **When** user searches, **Then** results are returned within 500ms for typical queries
3. **Given** a date range filter, **When** user searches with date constraints, **Then** only conversations within that range are returned
4. **Given** no matches found, **When** user searches, **Then** a clear "no results" message is displayed
5. **Given** search terms appear in multiple messages of one conversation, **When** user searches, **Then** the conversation appears once with the most relevant preview

---

### User Story 3 - View Conversation (Priority: P3)

As a user who found a conversation via search, I want to view the full conversation in a readable format so that I can review the complete discussion.

**Why this priority**: Viewing is essential to derive value from search results. Users need to read conversations, not just find them.

**Independent Test**: Can be fully tested by requesting a specific conversation by ID/title and verifying all messages are displayed in chronological order.

**Acceptance Scenarios**:

1. **Given** a valid conversation ID, **When** user requests to view it, **Then** all messages are displayed in chronological order with role labels (user/assistant)
2. **Given** a conversation with images or attachments, **When** user views it, **Then** attachment references are clearly indicated with file paths
3. **Given** a conversation with branching (edited messages), **When** user views it, **Then** the main conversation thread is shown by default

---

### User Story 4 - Export Conversation (Priority: P4)

As a user viewing a conversation, I want to export it to my preferred format (Markdown, JSON, HTML, YAML, or XML) so that I can share, archive, or process it externally.

**Why this priority**: Export enables external use of conversations—sharing with others, backup, or integration with other tools.

**Independent Test**: Can be fully tested by exporting a conversation to each format and verifying the output is valid and contains all conversation data.

**Acceptance Scenarios**:

1. **Given** a conversation, **When** user exports to Markdown, **Then** output is human-readable with clear message formatting and metadata header
2. **Given** a conversation, **When** user exports to JSON, **Then** output preserves full structure and can be re-imported
3. **Given** a conversation, **When** user exports to HTML, **Then** output renders correctly in a browser with basic styling
4. **Given** a conversation, **When** user exports to YAML, **Then** output is valid YAML with proper escaping
5. **Given** a conversation, **When** user exports to XML, **Then** output is valid XML with appropriate element structure
6. **Given** export request, **When** user specifies output path, **Then** file is written to that location; otherwise output goes to stdout

---

### User Story 5 - List Conversations (Priority: P5)

As a user, I want to list all imported conversations with basic metadata so that I can browse my archive and understand what's available.

**Why this priority**: Browsing complements search—users may want to explore without a specific query in mind.

**Independent Test**: Can be fully tested by running list command and verifying all conversations appear with correct metadata.

**Acceptance Scenarios**:

1. **Given** imported conversations, **When** user requests list, **Then** conversations are displayed with title, date, and message count
2. **Given** many conversations, **When** user lists, **Then** pagination or scrolling is supported
3. **Given** list request with sort option, **When** user specifies sort by date or title, **Then** results are ordered accordingly

---

### Edge Cases

- What happens when the archive contains conversations with no title? → Use first user message as fallback title, or "[Untitled]"
- What happens when message content is empty or null? → Display as "[empty message]" placeholder
- How does system handle very long conversations (1000+ messages)? → Pagination for view, full export still works
- What happens when export target file already exists? → Prompt for overwrite or fail with clear message
- How does system handle conversations in non-English languages? → Full UTF-8 support, no language assumptions
- What happens when database file is locked or inaccessible? → Clear error message with troubleshooting hints

## Requirements *(mandatory)*

### Functional Requirements

**Import**
- **FR-001**: System MUST import all conversations from a ChatGPT export directory's `conversations.json` file
- **FR-002**: System MUST preserve original OpenAI conversation IDs as primary identifiers
- **FR-003**: System MUST extract and store: conversation title, create_time, update_time, and all messages
- **FR-004**: System MUST support idempotent imports (re-running import updates existing, doesn't duplicate)
- **FR-005**: System MUST validate JSON structure before import and report clear errors for invalid data

**Search**
- **FR-006**: System MUST support full-text search across all message content
- **FR-007**: System MUST support filtering by date range (from/to dates)
- **FR-008**: System MUST return search results with: conversation title, date, match count, and preview snippet
- **FR-009**: System MUST index content at import time for fast queries

**View**
- **FR-010**: System MUST display conversations in chronological message order
- **FR-011**: System MUST clearly label message authors (user, assistant, system)
- **FR-012**: System MUST handle and display message metadata (timestamps, model info when available)

**Export**
- **FR-013**: System MUST export to Markdown format with readable conversation structure
- **FR-014**: System MUST export to JSON format preserving full data structure
- **FR-015**: System MUST export to HTML format viewable in standard browsers
- **FR-016**: System MUST export to YAML format with valid syntax
- **FR-017**: System MUST export to XML format with valid structure
- **FR-018**: System MUST support export to file path or stdout

**CLI Interface**
- **FR-019**: System MUST provide CLI commands for: import, search, list, view, export
- **FR-020**: System MUST support `--json` flag for machine-readable output on all commands
- **FR-021**: System MUST use exit code 0 for success, non-zero for errors
- **FR-022**: System MUST output errors to stderr, results to stdout

**Storage**
- **FR-023**: System MUST use SQLite as the default database (portable, no server)
- **FR-024**: System MUST store database as a single file in a configurable location
- **FR-025**: System MUST NOT modify the original archive files

### Key Entities

- **Conversation**: A complete chat session; has title, create_time, update_time, original OpenAI ID; contains many Messages
- **Message**: A single turn in a conversation; has author role (user/assistant/system), content (text), timestamp, parent reference for tree structure
- **Attachment**: Reference to media files (images, audio) associated with messages; has file path, type, original filename

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can import a 250MB archive (1,700+ conversations) in under 60 seconds
- **SC-002**: Users can search and receive results in under 500ms for typical keyword queries
- **SC-003**: Users can find a specific conversation within 3 commands (search → view or list → view)
- **SC-004**: Users can export any conversation to any of the 5 formats in under 2 seconds
- **SC-005**: All exported formats contain complete conversation data without loss
- **SC-006**: CLI operates without internet connection (fully offline capable)
- **SC-007**: Database file size is less than 2x the original JSON size (reasonable overhead)
- **SC-008**: 100% of original conversations are recoverable after import (no data loss)

## Assumptions

- Archive structure follows OpenAI's standard export format (`conversations.json` with documented schema)
- Users have Python 3.8+ available (common runtime, avoids compilation)
- Single-user access to database (no concurrent write requirements)
- Conversations are primarily text-based; image/audio references are preserved but content not indexed
