# Feature Specification: Web UI for ChatGPT Archive

**Feature Branch**: `002-web-ui`  
**Created**: 2026-02-12  
**Status**: Draft  
**Input**: User description: "Build a web UI for the ChatGPT Archive with Docker deployment"

## Clarifications

### Session 2026-02-12

- Q: Authentication & Access Control - How should the web UI handle user access? → A: Single user, personal deployment (no authentication, assumes trusted environment like localhost or private server)
- Q: Web Framework Architecture - Should frontend and backend be separate, and which frameworks? → A: Separate backend (FastAPI) and frontend (Next.js) communicating via REST API
- Q: Database Persistence in Docker - How should the SQLite database be persisted across container restarts? → A: Mount host directory in user's home area (e.g., ~/.chatgpt-archive/) for data persistence and easy backup access
- Q: UI Component Library - Which component library should be used for consistent, accessible UI? → A: shadcn/ui + Tailwind CSS (copy-paste components, no heavy dependencies, built-in accessibility)
- Q: Progress Updates for Long-Running Operations - How should the system communicate import/embedding progress to the client? → A: Server-Sent Events (SSE) for real-time server-to-client progress updates

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import and View Conversations (Priority: P1)

A user wants to import their ChatGPT data export archive and browse their conversation history through a web interface.

**Why this priority**: This is the core value proposition - users need to get their data into the system and view it. Without this, no other features matter.

**Independent Test**: Can be fully tested by uploading a ChatGPT export ZIP file, verifying the import completes successfully, and browsing the conversation list to view individual conversations. Delivers immediate value by making archived conversations accessible.

**Acceptance Scenarios**:

1. **Given** a user has a ChatGPT export ZIP file, **When** they upload it through the web interface, **Then** the system imports all conversations and displays a success message with the count of imported conversations
2. **Given** conversations are imported, **When** the user views the conversation list, **Then** they see all conversations with titles, dates, and message counts
3. **Given** a conversation list is displayed, **When** the user clicks on a conversation, **Then** they see the full conversation with all messages formatted properly
4. **Given** an import is in progress, **When** the user checks the import status, **Then** they see a progress indicator showing current status

---

### User Story 2 - Search Conversations (Priority: P2)

A user wants to quickly find specific conversations or messages by searching through their archive.

**Why this priority**: Search is essential for working with large archives (hundreds or thousands of conversations). It's the primary way users will navigate beyond browsing.

**Independent Test**: Can be fully tested by entering search queries and verifying results match expectations. Works independently if conversations are already imported (P1).

**Acceptance Scenarios**:

1. **Given** conversations are imported, **When** the user enters a search query, **Then** results appear within 500ms of query submission showing matching conversations
2. **Given** search results are displayed, **When** the user refines their query, **Then** results update dynamically after a 500ms input debounce delay (query is sent 500ms after user stops typing)
3. **Given** a user searches with no matches, **When** the search completes, **Then** they see a helpful "no results" message
4. **Given** search results exist, **When** the user clicks a result, **Then** they navigate to that conversation with the search term highlighted

---

### User Story 3 - Export Conversations (Priority: P3)

A user wants to export one or more conversations in various formats for backup, sharing, or analysis.

**Why this priority**: Export enables data portability and integration with other tools. Important but not required for basic viewing.

**Independent Test**: Can be fully tested by selecting conversations and downloading them in different formats. Works independently if conversations are imported (P1).

**Acceptance Scenarios**:

1. **Given** a user is viewing a conversation, **When** they click export and select a format (Markdown, JSON, YAML, HTML, XML, CSV, or Excel), **Then** the conversation downloads in that format
2. **Given** a user has selected multiple conversations, **When** they export them, **Then** all selected conversations are included in a single export file
3. **Given** a user initiates an export, **When** the export completes, **Then** the file downloads automatically with a descriptive filename

---

### User Story 4 - Manage Tags and Favorites (Priority: P3)

A user wants to organize their conversations by adding tags and marking important conversations as favorites for quick access.

**Why this priority**: Tags and favorites improve organization for power users, enabling quick re-access to important conversations without repeated searching. Not essential for basic archive access.

**Independent Test**: Can be fully tested by creating tags, applying them to conversations, marking favorites, and filtering by tags or favorites. Works independently if conversations are imported (P1).

**Acceptance Scenarios**:

1. **Given** a user is viewing a conversation, **When** they add a tag, **Then** the tag appears on that conversation and in the tag list
2. **Given** tags exist, **When** the user filters by a tag, **Then** only conversations with that tag are displayed
3. **Given** a user has created tags, **When** they rename or delete a tag, **Then** the changes apply to all conversations with that tag
4. **Given** a user has found an important conversation, **When** they mark it as a favorite, **Then** it appears in their favorites list for quick access
5. **Given** a user has favorites, **When** they view the favorites list, **Then** they see all favorited conversations without needing to search again

---

### User Story 5 - Generate Semantic Search Embeddings (Priority: P4)

A user wants to enable semantic search capabilities by generating embeddings for their conversations.

**Why this priority**: Advanced feature that enhances search quality but requires external API setup and isn't needed for basic functionality.

**Independent Test**: Can be fully tested by providing OpenAI API credentials, initiating embedding generation, and verifying semantic search works. Works independently if conversations are imported (P1).

**Acceptance Scenarios**:

1. **Given** a user has provided OpenAI API credentials, **When** they initiate embedding generation, **Then** embeddings are generated for all conversations with a progress indicator
2. **Given** embeddings exist, **When** the user performs a search, **Then** results include semantically similar conversations even without exact keyword matches
3. **Given** embedding generation is in progress, **When** the user navigates to another page within the app, **Then** the server-side process continues in the background (closing the browser does NOT cancel the server-side operation)

---

### Edge Cases

- What happens when a user uploads an invalid or corrupted ZIP file? The system should validate the ZIP structure, show a clear error message, and allow retry without data loss.
- How does the system handle very large archives (1000+ conversations)? Import should process in batches with SSE progress updates; UI should implement virtualization for conversation lists.
- What happens if the database file is locked or inaccessible? Show clear error message indicating file lock issue, suggest closing other instances or checking permissions.
- How does the system handle network errors during import or export operations? Provide clear error messages with retry options. Import operations are atomic per-archive (restart from beginning on failure); export operations generate files server-side before download (retry re-downloads the same generated file).
- What happens when OpenAI API credentials are invalid or quota is exceeded during embedding generation? Validate credentials before starting; show specific error (auth vs quota) and allow credential update.
- How does the system handle concurrent access if multiple browser tabs are open? SQLite write serialization is acceptable; UI should refresh data when changes detected from other tabs.
- What happens if SSE connection drops during a long-running operation? Backend operation continues; client should auto-reconnect and resume progress display.
- What happens if the application is accidentally exposed to a public network? The system displays a startup warning if binding to 0.0.0.0 or non-localhost addresses. Documentation includes a prominent security notice recommending localhost-only or VPN/firewall-protected deployments.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a web interface for uploading ChatGPT export ZIP files
- **FR-002**: System MUST import conversations from uploaded archives and store them in the existing SQLite database (via existing chatgpt_archive library per FR-012)
- **FR-003**: System MUST display a list of all imported conversations with title, date, and message count
- **FR-004**: System MUST render full conversation details including all messages with proper formatting
- **FR-005**: System MUST provide a search interface that returns results within 500ms
- **FR-006**: System MUST support full-text search across conversation titles and message content
- **FR-007**: System MUST allow users to export conversations in all formats supported by the CLI: Markdown, JSON, YAML, HTML, XML (constitution minimum) plus CSV and Excel (feature 001 extensions)
- **FR-008**: System MUST allow users to create, rename, and delete tags
- **FR-009**: System MUST allow users to apply tags to conversations and filter conversations by tags
- **FR-010**: System MUST allow users to generate semantic search embeddings using OpenAI API credentials
- **FR-011**: System MUST display progress indicators for long-running operations (import, embedding generation) using Server-Sent Events (SSE) for real-time updates. Progress events MUST include: percentage complete, current item count, total items, current operation description, and elapsed time. Updates MUST be sent at least every 5 seconds during active processing
- **FR-012**: System MUST use the existing chatgpt_archive Python library for all data operations (no logic duplication)
- **FR-013**: System MUST maintain compatibility with the SQLite database format from feature 001
- **FR-014**: System MUST be deployable via Docker containers
- **FR-015**: System MUST work offline except for optional embedding generation
- **FR-016**: System MUST provide a consistent user interface following shadcn/ui design patterns (consistent spacing, typography, color palette, and component behavior) with reusable components
- **FR-017**: System MUST support modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- **FR-018**: System MUST handle errors gracefully with structured error messages following the pattern: "[What went wrong]. [What to do next]." (e.g., "Upload failed: file is not a valid ZIP archive. Please select a valid ChatGPT export ZIP file and try again.")
- **FR-019**: System is designed for single-user personal deployment without authentication (assumes trusted network environment such as localhost or private network). ⚠️ If exposed to public networks, users MUST configure firewall rules or reverse proxy authentication; the system provides a startup warning when binding to 0.0.0.0
- **FR-020**: System architecture MUST consist of separate FastAPI backend and Next.js (React) frontend communicating via REST API
- **FR-021**: System MUST persist database and data files to a host directory: ~/.chatgpt-archive/ on Unix/macOS, %USERPROFILE%\.chatgpt-archive\ on Windows. Docker deployments MUST use explicit volume mount (e.g., ${HOME}/.chatgpt-archive:/data) for host data persistence and portability
- **FR-022**: System MUST store user settings and preferences persistently in ~/.chatgpt-archive/settings.json. Settings include: UI theme (light/dark), default export format, OpenAI API key (plaintext — single-user trusted environment per FR-019), sidebar state, and items-per-page preference
- **FR-023**: System MUST allow users to mark conversations as favorites for quick re-access without repeated searching
- **FR-024**: System MUST provide a favorites view showing all favorited conversations
- **FR-025**: Frontend MUST use shadcn/ui components with Tailwind CSS for consistent, accessible UI design

### Key Entities

- **Conversation**: Represents a ChatGPT conversation with title, creation date, update date, messages, optional tags, and favorite status
- **Message**: Individual messages within a conversation with content, author (user/assistant), timestamp, and metadata
- **Tag**: User-defined labels for organizing conversations with name and color
- **Favorite**: Boolean column (is_favorite INTEGER 0/1) on the conversations table indicating user has starred/pinned them for quick access
- **User Settings**: Persistent preferences including UI theme, default export format, OpenAI API credentials, and other configuration
- **Export**: Generated file containing one or more conversations in a specified format
- **Import Job**: Represents an import operation with status, progress, and completion metadata
- **Embedding**: Vector representation of conversation content for semantic search

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a ChatGPT export archive (up to 100 conversations / 50MB ZIP) and view their conversations within 2 minutes
- **SC-002**: Search queries return results in under 500ms for archives with up to 1000 conversations
- **SC-003**: Page navigation (between conversation list and detail views) completes in under 500ms
- **SC-004**: Users can successfully export conversations in all 7 formats (Markdown, JSON, YAML, HTML, XML, CSV, Excel)
- **SC-005**: The web UI provides access to 100% of CLI functionality without requiring terminal access
- **SC-006**: Import operations display progress updates at least every 5 seconds
- **SC-007**: The application can be deployed using a single Docker Compose command
- **SC-008**: UI interactions (clicks, form inputs) respond within 100ms
- **SC-009**: The system supports archives with up to 5000 conversations without performance degradation (list loads <1s, search <500ms, detail view <500ms)
- **SC-010**: 95% of users can successfully complete their first import without documentation or support
