# ChatGPT Archive Web Frontend

Next.js 16 + React 19 + TypeScript frontend for the ChatGPT Archive web UI.

## Current UI Scope

- Segment-aware conversation rendering for markdown, attachments, fallback blocks, reasoning disclosures, and grouped tool activity.
- Markdown rendering with syntax-highlighted code blocks, tables, and KaTeX math support.
- Sidebar-based conversation browsing with sorting, favorites, tag sections, and automatic loading of more conversations at the end of the list.
- Shared tooltip-driven interaction hints for shell navigation, conversation metadata, media actions, and archive management controls.

## Development

```bash
cd web
npm ci
npm run dev
```

Set `NEXT_PUBLIC_API_URL` if the API is not running on `http://localhost:8000`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Build

```bash
npm run build
npm start
```

The production build uses Next.js standalone output and is what the Docker image serves.

## Scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
npm test
npm run test:coverage
npm run test:e2e
```

## Related Docs

- [Root README](../README.md)
- [Web UI guide](../docs/user-guide/web-ui.md)
- [Contributing](../CONTRIBUTING.md)
