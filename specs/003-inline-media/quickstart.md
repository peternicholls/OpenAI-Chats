# Quick Start: Inline Media in Conversation View

Developer guide for getting the feature running end-to-end.

---

## Prerequisites

- Existing `chatgpt-archive` dev environment (Python venv activated, API running)
- An extracted OpenAI archive directory on disk (the `6a46cf212e33...` folder)
- Node.js / pnpm installed (for web changes)

---

## Step 1: Configure the Archive Media Directory

Set the `CHATGPT_ARCHIVE_DIR` environment variable to point to your extracted archive:

```bash
# In api/.env (or export in your shell)
CHATGPT_ARCHIVE_DIR=/Users/peternicholls/Dev/OpenAI-Chats/6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875
```

For Docker (`docker-compose.yml`), add:
```yaml
environment:
  - CHATGPT_ARCHIVE_DIR=/data/archive
volumes:
  - /path/to/your/archive:/data/archive:ro
```

The default (if unset) is `{DB_PARENT_DIR}/media/`, populated automatically on next ZIP import.

---

## Step 2: Verify Media Endpoint

Restart the API, then test with a known file from your archive:

```bash
# Find a conv ID that has an image subdir
ls 6a46cf212e33.../68e06336-bce4-8330-b350-f7a33ffac85e/image/

# Test the endpoint
curl -I "http://localhost:8000/api/media/68e06336-bce4-8330-b350-f7a33ffac85e/file_000000004f48620a9bfb06ccaa684b65"
# → HTTP/1.1 200 OK, Content-Type: image/jpeg

# Test root-level file
curl -I "http://localhost:8000/api/media/root/file-482wvxnQterzEyTpE7tC95"
# → HTTP/1.1 200 OK, Content-Type: image/jpeg
```

---

## Step 3: Verify Attachment Resolution in API Response

Open a conversation known to have images (e.g. "AI image check" — `68e06336-bce4-8330-b350-f7a33ffac85e`):

```bash
curl -s "http://localhost:8000/api/conversations/68e06336-bce4-8330-b350-f7a33ffac85e" \
  | python3 -c "import json,sys; msgs=json.load(sys.stdin)['messages']; [print(m['attachments']) for m in msgs if m.get('attachments')]"
```

Expected output: JSON array of attachment objects with `type`, `url`, `filename`, `found: true`.

---

## Step 4: Verify UI Rendering

Start the web dev server:

```bash
cd web && pnpm dev
```

Navigate to the conversation containing images. Images should render inline in the message bubbles. Broken/missing files show a labelled placeholder.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `404` on `/api/media/...` | `CHATGPT_ARCHIVE_DIR` not set or wrong path | Check env var; verify files exist at that path |
| Attachments array empty | Content parsing failed | Check API logs for `ast.literal_eval` errors; verify `content` column has asset pointer strings |
| `400` on media endpoint | Invalid `conv_id` or `file_id` format | Ensure IDs match expected regex patterns |
| Images show placeholder | File exists in DB but not in media dir | Copy the specific conv subdirectory into `CHATGPT_ARCHIVE_DIR` |
| Import doesn't copy media | Feature not deployed yet | Ensure new import flow is installed and `CHATGPT_ARCHIVE_DIR` is writable |

---

## Running Tests

```bash
# API tests
cd api && python -m pytest tests/test_media.py -v

# Frontend tests
cd web && pnpm test --run AttachmentImage AttachmentFile AttachmentAudio
```
