# ChatGPT Archive

Search, browse, and export ChatGPT conversation archives from the command line or a local web UI.

The repository contains three main surfaces:

- A Python package and CLI for importing OpenAI exports into SQLite and searching or exporting them offline.
- A FastAPI backend that exposes the archive over a local REST API.
- A Next.js + TypeScript frontend that provides a browser UI for search, tagging, favorites, import progress, and inline media rendering.

## Highlights

- Import extracted ChatGPT exports into a local SQLite database with FTS5 search.
- Search conversations by keyword, date range, or optional semantic embeddings.
- View and export conversations as Markdown, JSON, YAML, HTML, XML, CSV, or Excel.
- Serve a browser UI with tagging, favorites, import workflows, and transcript rendering.
- Keep attachment files on disk and stream them directly when needed instead of storing blobs in the database.

## Quick Start

### CLI

```bash
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

python -m venv .venv
source .venv/bin/activate
pip install -e .

chatgpt-archive import /path/to/chatgpt-export
chatgpt-archive search "machine learning"
chatgpt-archive view <conversation-id>
```

Optional semantic search support:

```bash
pip install -e ".[semantic]"
export OPENAI_API_KEY="sk-..."
chatgpt-archive embed
```

### Web UI

```bash
docker compose up -d
open http://localhost
```

The Docker setup serves everything behind nginx on port `80`:

- `/` -> Next.js frontend
- `/api/` -> FastAPI backend

## Documentation

- [User Guide](docs/user-guide/README.md)
- [CLI Reference](docs/user-guide/usage.md)
- [Web UI and Docker Guide](docs/user-guide/web-ui.md)
- [Troubleshooting](docs/user-guide/troubleshooting.md)
- [Python API](docs/API.md)
- [REST API Reference](docs/REST-API.md)
- [Contributing](CONTRIBUTING.md)

## Developer Overview

### Stack

| Area | Technology |
| --- | --- |
| CLI and core library | Python, Click, SQLite |
| Optional semantic search | `sqlite-vec`, OpenAI embeddings |
| Web API | FastAPI, Uvicorn, Pydantic |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Frontend tests | Vitest, Testing Library, Playwright |
| Container serving | Docker Compose, nginx |

### Repository Layout

```text
OpenAI-Chats/
├── chatgpt_archive/        # Core Python package, CLI, DB layer, import/search/export logic
├── api/                    # FastAPI application, routers, middleware, backend tests
├── web/                    # Next.js frontend, TypeScript source, web tests
├── docs/                   # User guide plus Python and REST API docs
│   └── user-guide/         # End-user CLI, web UI, and troubleshooting guides
├── docker/                 # nginx config and Dockerfiles
├── tests/                  # Python tests for the core package and API
├── specs/                  # Feature specs, plans, and contracts
├── docker-compose.yml      # Local Docker stack: nginx + api + web
└── pyproject.toml          # Root Python package metadata
```

### How the Pieces Fit Together

1. `chatgpt_archive.importer` parses `conversations.json` from an extracted OpenAI export and stores normalized data in SQLite.
2. The CLI reads the same database directly for search, listing, viewing, export, and embedding workflows.
3. The API wraps the core package and local services in FastAPI routes under `/api/`.
4. The web app calls those routes through `web/src/services/api.ts`.
5. In Docker, nginx proxies browser traffic to the frontend and API and disables buffering for SSE import progress.

## Local Development

### Prerequisites

- Python `3.11+` for the API stack
- Python `3.10+` for CLI-only usage
- Node.js `20+` and npm for the frontend
- Docker 24+ with Compose v2 for the containerized stack

### Install Everything

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev,semantic]"
pip install -e "./api[dev]"

cd web
npm ci
cd ..
```

### Run the Services Locally

Backend API:

```bash
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Local development URLs:

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Building the TypeScript Frontend

The frontend is a standard Next.js application in `web/` written in TypeScript. For local or CI builds:

```bash
cd web
npm ci
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run build
```

What that build produces:

- `npm run build` runs `next build`
- `web/next.config.ts` sets `output: "standalone"`
- Next.js emits:
  - `.next/standalone/` for the production Node server
  - `.next/static/` for client assets
  - `public/` static files copied alongside the build

This is the production artifact used for web consumption in Docker. `docker/web.Dockerfile` copies the standalone output and serves it with:

```bash
node server.js
```

Important detail: `NEXT_PUBLIC_API_URL` is a build-time variable. If the browser-facing API origin changes, rebuild the frontend.

## How the Project Is Served

### Local Development

- `uvicorn api.main:app` serves the API directly on `:8000`
- `npm run dev` serves the Next.js frontend directly on `:3000`
- The browser talks to the API using `NEXT_PUBLIC_API_URL`

### Docker and Shared Local Use

`docker compose up -d` starts three services:

- `nginx` on host port `80`
- `api` on internal port `8000`
- `web` on internal port `3000`

nginx routes:

- `/` -> `web:3000`
- `/api/` -> `api:8000`

It also:

- disables proxy buffering for SSE progress streams
- sets a `500M` upload limit for archive imports
- keeps the internal web and API services off host-exposed ports by default

Persistent app data lives in `~/.chatgpt-archive/` and is mounted into the API container as `/data`.

## Testing

Backend and core package:

```bash
source .venv/bin/activate
pytest tests -q
```

Frontend:

```bash
cd web
npm run lint
npm test
npm run test:e2e
```

## Key Runtime Configuration

| Variable | Purpose |
| --- | --- |
| `CHATGPT_ARCHIVE_DB` | SQLite database path |
| `CHATGPT_ARCHIVE_DIR` | Extracted archive/media directory |
| `OPENAI_API_KEY` | Enables embedding generation and semantic search |
| `NEXT_PUBLIC_API_URL` | Browser-facing API base URL baked into the frontend build |
| `CORS_ORIGINS` | JSON array of allowed browser origins for the API |
| `TRUSTED_PROXY_IPS` | Proxies allowed to supply forwarded IP headers |

More detail lives in the [web UI guide](docs/user-guide/web-ui.md).

## Notes

- The API is intended for trusted local or self-hosted use. It does not ship with multi-user authentication.
- Attachment media is served from the filesystem at request time; it is not embedded into the SQLite database.
- The checked-in `docker-compose.yml` includes a repo-local archive mount for development. Update that bind mount for your machine before relying on it.

## License

MIT
