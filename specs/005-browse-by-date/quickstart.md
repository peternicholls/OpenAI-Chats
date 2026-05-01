# Quickstart: Browse Chats by Date

## Prerequisites

- Python 3.11+ for the API backend
- Python environment with the root package and API package installed
- Node.js environment for the Next.js frontend
- An imported archive database at the default path or via `CHATGPT_ARCHIVE_DB`

## Setup

### Backend

```bash
pip install -e .
pip install -e ./api
uvicorn api.main:app --reload
```

### Frontend

```bash
cd web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

## Validation Flow

### 1. Verify the separate date-browsing mode

1. Open the main archive UI.
2. Switch from the normal conversation/search experience into the new date-browsing mode.
3. Confirm that the visible calendar period highlights only days with initiated conversations.
4. Confirm that conversations lacking initiated dates do not appear in dated cells and are reachable through the unknown-date group.

### 2. Verify calendar-day detail and adjacent navigation

1. Select a day with known conversations.
2. Confirm that the day-detail list shows conversation summaries and opens the expected conversation.
3. Move to the previous and next calendar period.
4. Confirm that the active range context is preserved while the period updates.

### 3. Verify date-range narrowing

1. Apply a start date and end date in date mode.
2. Confirm that only conversations initiated inside the range remain visible/selectable.
3. Apply a range with no matches and confirm the empty-state behavior.

### 4. Verify cross-mode date ordering

1. Open the normal conversation list and sort by initiated date.
2. Confirm that ordering matches `create_time` semantics.
3. Switch to last updated date ordering and confirm that ordering changes to `update_time` semantics.
4. Repeat the same sort validation in the search results page.

## Suggested Test Commands

### Backend

```bash
pytest api/tests/test_conversations.py api/tests/test_search.py -q
```

### Frontend unit/integration

```bash
cd web
npm test -- --run
```

### End-to-end

```bash
cd web
npm run test:e2e
```

## API Smoke Checks

Example calendar summary request:

```bash
curl "http://localhost:8000/api/conversations/calendar?period_unit=month&period_start=2026-05-01&timezone=Europe/London"
```

Example day-detail request:

```bash
curl "http://localhost:8000/api/conversations/by-date?date=2026-05-01&timezone=Europe/London&limit=20&offset=0"
```

Example unknown-date request:

```bash
curl "http://localhost:8000/api/conversations/by-date/unknown?limit=20&offset=0"
```

Example search sort request:

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"python","sort_by":"updated_date","order":"desc","limit":20,"offset":0}'
```
