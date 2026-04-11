# ChatGPT Archive Web Frontend

Next.js 16 + React 19 + TypeScript frontend for the ChatGPT Archive web UI.

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
