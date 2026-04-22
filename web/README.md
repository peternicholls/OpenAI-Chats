# OpenAI-Chats Frontend

This directory contains the Next.js frontend for the local OpenAI-Chats archive app.

## What It Covers

- Conversation browsing and detail views
- Search UI
- Import flow and progress display
- Favorites, tags, and settings
- Batch export controls
- Embedding management UI

## Local Development

```bash
cd web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

If you are running the full Docker stack instead, the browser entrypoint is `http://localhost` and nginx proxies requests to the backend for you.

## Scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
npm test
npm run test:e2e
```

## Environment

The frontend currently depends on:

- `NEXT_PUBLIC_API_URL`: browser-facing API base URL

Examples:

- Local frontend + local backend: `http://localhost:8000`
- Docker Compose through nginx: `http://localhost`

`NEXT_PUBLIC_API_URL` is baked into the frontend build, so rebuild the frontend if you change it.

## Notes

- The app uses Next.js 16, React 19, TypeScript, and React Query.
- The main project overview lives in [../README.md](../README.md).
- The previous scaffold README has been archived in [../docs/archive/frontend-scaffold-readme.md](../docs/archive/frontend-scaffold-readme.md).
