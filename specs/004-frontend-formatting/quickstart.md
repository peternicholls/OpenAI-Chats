# Quickstart: Frontend Formatting

Developer guide for validating the formatted conversation rendering flow end to end.

---

## Prerequisites

- Python environment for the API is available.
- Node.js is installed for the Next.js app.
- The archive media directory from feature 003 is still configured when attachment scenarios are being tested.

---

## Step 1: Install Frontend Dependencies

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats/web
npm install
```

Expected result: the web app includes the markdown rendering dependencies declared by this feature plan.

---

## Step 2: Start the API and Web App

In one terminal:

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats/api
python -m uvicorn main:app --reload
```

In another terminal:

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats/web
npm run dev
```

---

## Step 3: Verify the Conversation API Contract

Request a conversation that contains markdown and attachments:

```bash
curl -s http://localhost:8000/api/conversations/<conversation-id>
```

Expected result:
- Each message still includes `content` and `attachments`.
- Messages eligible for formatted rendering also include ordered `segments`.
- Mixed messages show `markdown`, `attachment`, and `fallback` segments in the same order as the original content.

---

## Step 4: Verify UI Rendering

Open a conversation in the browser that contains:
- headings or lists
- inline and fenced code
- one or more attachment payloads
- at least one malformed or unsupported structured payload fixture

Expected result:
- prose is formatted like a chat transcript instead of showing raw markdown markers
- attachments render inline at the correct positions
- unsupported structured payloads render as labeled fallback blocks instead of raw dict blobs
- plain-text messages still read normally

---

## Step 5: Run Focused Tests

Backend:

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats/api
pytest tests/test_conversations.py tests/test_formatting_service.py
```

Frontend unit tests:

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats/web
npm run test -- MessageBubble MarkdownRenderer
```

End-to-end:

```bash
cd /Users/peternicholls/Dev/OpenAI-Chats/web
npm run test:e2e -- conversation.spec.ts
```

---

## Troubleshooting

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| Raw markdown still appears | `segments` not present or not used by the UI | Inspect the conversation API response and confirm `MessageBubble` prefers `segments` |
| Raw dict payload still appears inline | Parser classified it as markdown/plain text instead of fallback | Add or adjust backend segment-builder tests for that payload shape |
| Attachments appear out of order | Segment `attachment_index` values do not match the `attachments[]` array | Verify backend ordering tests and mixed-content fixture expectations |
| Code blocks render as plain paragraphs | Markdown renderer dependency or component mapping is missing | Confirm `react-markdown` wiring and unit test coverage |
