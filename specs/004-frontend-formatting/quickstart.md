# Quickstart: Frontend Formatting

Developer guide for validating the formatted conversation rendering flow.

## Prerequisites

- Existing backend and web dependencies installed
- Inline media feature from 003 available in the working tree
- A conversation fixture or real archive conversation containing:
  - markdown headings, lists, links, quotes, inline code, and fenced code blocks
  - at least one raw structured asset payload currently leaking into the UI

## Step 1: Run unit and API validation

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats
source .venv/bin/activate
pytest api/tests/test_conversations.py api/tests/test_media.py

cd web
npm test -- --run __tests__/components/MessageBubble.test.tsx __tests__/services/api.test.ts
```

## Step 2: Run browser validation

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats/web
npx playwright test __tests__/e2e/conversation.spec.ts --project=chromium
```

## Step 3: Manual conversation check

1. Start the API and web app.
2. Open a conversation known to contain markdown-rich assistant output.
3. Verify headings, lists, links, blockquotes, inline code, and fenced code blocks render as formatted content.
4. Open a conversation that previously displayed raw asset-pointer dictionaries.
5. Verify raw payload blobs are replaced by readable attachment or fallback blocks.

## Expected Outcomes

- Common markdown no longer appears as literal source syntax.
- Structured attachment-related payloads are not shown as raw Python-style dicts.
- Text-only messages remain readable and ordered correctly.
- Unsupported rich content stays readable through fallback rendering instead of breaking layout.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Raw markdown still visible | Message renderer still uses plain text path | Verify frontend uses `segments` before raw `content` |
| Raw dict payload still visible | Backend segment parsing missed the payload shape | Expand structured payload parsing and add a fallback segment |
| Code blocks collapse line breaks | Markdown renderer missing break/code configuration | Verify markdown renderer plugin setup and code block styling |
| Attachment order is wrong | Segment ordering drifted from parsed content order | Re-check segment builder tests for mixed-content messages |
