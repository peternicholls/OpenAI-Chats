# Research: Inline Media in Conversation View

**Phase**: 0 — Resolve all NEEDS CLARIFICATION and design unknowns  
**Date**: 2026-02-25

---

## R-001: Asset Pointer URI Schemes and File Layouts

**Question**: How do `sediment://` and `file-service://` URIs map to actual files on disk?

**Decision**: Two distinct resolution strategies, verified against the real archive.

**Rationale**:

### `sediment://file_{hex_id}`
- Format: `sediment://file_00000000{16_hex_chars}`
- Files stored in: `{archive_root}/{conv_id}/image/` or `{archive_root}/{conv_id}/audio/`
- Filename pattern: `file_{hex_id}-{uuid}.{ext}`  
  e.g. `file_000000004f48620a9bfb06ccaa684b65-c83dff0c-5472-4221-b956-562e790b3bcf.jpg`
- Resolution algorithm: scan `{conv_id}/image/` and `{conv_id}/audio/` for any file whose name starts with `file_{hex_id}`
- The UUID suffix and extension are not derivable from the pointer; directory scan is required.

### `file-service://file-{short_id}`
- Format: `file-service://file-{alphanumeric_id}` (e.g. `file-MxiG6K5nWu8CKMocj8GDbL`)
- Files stored in: `{archive_root}/` (top level)
- Filename pattern: `file-{short_id}-{original_name}.{ext}`  
  e.g. `file-482wvxnQterzEyTpE7tC95-36CD1CB5-F969-4E5E-A9B9-DB34D5F55634.jpeg`
- Resolution algorithm: scan archive root for any file matching `file-{short_id}-*`
- Original filename is human-readable in some cases (e.g. `file-4Vdhhbs7F48DZfbPKwk1PN-Screenshot 2025-05-23 at 22.17.46.png`)

### Content type detection
- Extension in filename generally reliable (`.jpg`, `.jpeg`, `.png`, `.wav`, `.pdf`, `.png`)
- MIME type can be derived from extension using Python's `mimetypes` stdlib module
- No content sniffing required

**Alternatives considered**: Parse MIME from file content — rejected (unnecessary complexity, stdlib is sufficient).

---

## R-002: Archive File Persistence After Import

**Question**: The API import flow extracts ZIP to a temp dir then deletes it. How are media files accessible at request time?

**Decision**: Introduce a **permanent archive media store directory** (`CHATGPT_ARCHIVE_DIR`). During import, instead of using a temp-only dir, copy the extracted archive contents to this permanent location. On subsequent imports of new exports, merge into the same directory (additive, never deletes existing files).

**Rationale**:
- The current import flow (`tempfile.TemporaryDirectory`) deletes all extracted files after import completes — media files are lost.
- The user's existing workflow shows they keep the raw extracted archive directory at a known path (`6a46cf212e33...`). We need to formalise this.
- Simplest fix: after extraction and DB import, `shutil.copytree` the archive into `CHATGPT_ARCHIVE_DIR` (default: `~/.chatgpt-archive/media/`). Only copy if not already present per-file ("merge copy").
- Alternative: accept a directory path as import input instead of ZIP — but this would require UI/API changes and works less well in the Docker deployment.
- Alternative: stream files from the original ZIP on every request — rejected (each request would open the ZIP; original ZIP path is not retained).

**Implementation note**: `CHATGPT_ARCHIVE_DIR` env var defaults to the same parent directory as `CHATGPT_ARCHIVE_DB`. Example: if DB is at `~/.chatgpt-archive/chats.db`, media store defaults to `~/.chatgpt-archive/media/`. This can also be set in `settings.json` for UI users.

---

## R-003: Asset Pointer Extraction from Stored Message Content

**Question**: Message `content` is currently stored as a string — how do we reliably extract asset pointers from it?

**Decision**: At API response time, parse the raw content string using a regex pattern to detect asset pointer blocks, then extract structured attachment metadata alongside the existing text content.

**Rationale**:
- The importer converts content parts to string via `str(p)` for dict parts, so stored content looks like:
  ```
  {'content_type': 'image_asset_pointer', 'asset_pointer': 'file-service://file-ABC', 'size_bytes': 172498, 'width': 1536, 'height': 1228, ...}
  ```
- These are Python `repr` strings of dicts, not JSON. `ast.literal_eval()` can safely parse them.
- Regex approach: scan for `'content_type': '(image_asset_pointer|multimodal_text)'` blocks; extract the enclosing dict with `ast.literal_eval`.
- For text-only messages, the parse attempt is trivial (no matches) — zero overhead for the common case.
- **Security**: `ast.literal_eval` is safe — it only evaluates literals (strings, numbers, dicts, lists), never arbitrary code. Input is internal DB data, not user-provided.

**Alternatives considered**:
- Modify importer to store structured content in DB — rejected (violates no-DB-change constraint and would require schema migration).
- Store content as JSON from day one — a future improvement for spec 004+, but would require re-import of all conversations.

---

## R-004: API Endpoint Design for Media Serving

**Question**: What URL structure should the media endpoint use, and how does it validate paths securely?

**Decision**: Two endpoint styles unified under `/api/media/`:

```
GET /api/media/{conv_id}/{file_id}    # sediment:// (conv-scoped files: image/audio)
GET /api/media/root/{file_id}         # file-service:// (archive root-level files)
```

**Rationale**:
- Conv-scoped files need the conversation ID to locate the right subdirectory (`{conv_id}/image/` or `{conv_id}/audio/`).
- Root-level files do not need conv ID; `root` prefix avoids UUID collision with conv IDs.
- FastAPI `FileResponse` handles streaming, content-type headers, and ETag/caching automatically.
- **Path traversal prevention**: All paths are constructed from `CHATGPT_ARCHIVE_DIR` as the base; resolved path must be `is_relative_to(archive_dir)` before serving. `conv_id` and `file_id` validated to match safe patterns (alphanumeric, hyphens, underscores only) before any filesystem operation.
- The frontend calls these endpoints by embedding the resolved media URL in the `attachments` array of the Message API response. The web UI renders the URL directly in `<img src>`, `<audio src>`, or as a download link.

---

## R-005: Frontend Rendering Approach

**Question**: How should the web UI distinguish between attachment types and render them without breaking text-only conversations?

**Decision**: Extend the `Message` API response to include an `attachments` array (empty for text-only messages). `MessageBubble` delegates to type-specific sub-components.

**Rationale**:
- The API already handles content parsing at response time (see R-003). The resolved `attachments` array tells the frontend exactly what to render — no client-side URI parsing required.
- Each attachment has a `type` field (`image`, `audio`, `file`), a `url` (the `/api/media/...` URL), and metadata (`filename`, `width`, `height` for images).
- For text-only messages, `attachments` is `[]` — `MessageBubble` renders exactly as today with zero change to existing behaviour.
- Inline image rendering uses Next.js `<img>` (not `next/image`, to avoid static origin restriction on local API URLs). Images are lazy-loaded; clicking opens full size.
- Audio uses HTML5 `<audio controls>` — no extra library needed.
- Files use a download card with icon derived from MIME type.

**Alternatives considered**: Client-side parsing of the raw content string — rejected (duplicates server logic, couples frontend to DB storage format, breaks if storage format ever changes).

---

## R-006: Performance — Multiple Attachments Per Conversation

**Question**: What happens when a conversation has many attachments? Is per-request file lookup expensive?

**Decision**: Per-request directory scan is acceptable for MVP at this scale. No caching or indexing needed.

**Rationale**:
- The real archive has ~150 root-level files and at most a handful of files per conv subdirectory.
- `os.scandir()` on a directory of this size is <1ms on any modern OS.
- Each media request is a single file serve; FastAPI `FileResponse` with `stat_result` avoids double-stat.
- For conversations with 10+ attachments, the browser makes 10+ parallel requests to `/api/media/...`; these are independent, fast file serves.
- If the archive grows to thousands of files per directory (unlikely for OpenAI exports), an in-memory index built once at startup would be the next step — but YAGNI for now.

---

## Summary Table

| Unknown | Decision | Confidence |
|---------|----------|------------|
| URI → file mapping | Two regex + dir scan strategies (verified against real archive) | High |
| Archive persistence | Permanent media store dir, merged during import | High |
| Content parsing | `ast.literal_eval` on stringified dict blocks | High |
| API endpoint design | `/api/media/{conv_id}/{file_id}` + `/api/media/root/{file_id}` | High |
| Frontend rendering | `attachments[]` in API response; type-specific sub-components | High |
| Performance | Per-request scan acceptable at current scale | High |
