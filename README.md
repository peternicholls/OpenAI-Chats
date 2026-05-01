# OpenAI-Chats

OpenAI-Chats is a local-first archive browser for ChatGPT exports. It imports your exported archive into SQLite, gives you a browser UI for reading and organizing conversations, exposes a FastAPI backend for automation, and keeps the original CLI and Python library available for scripting and bulk workflows.

The current focus of the project is not just search and export. It is building a dependable personal archive that reflects the structure of real ChatGPT exports closely enough to support accurate transcript rendering, tagging, favorites, batch export, and future archive-analysis features.

## Project Focus

- **Web-first archive workflow**: the main product surface is the local web app, backed by FastAPI and Next.js.
- **Faithful archive handling**: parsing and rendering decisions are grounded in observed ChatGPT export data rather than simplified assumptions.
- **Local ownership**: data stays in SQLite on your machine, with optional OpenAI-powered embeddings when you choose to enable semantic search.
- **Multiple access paths**: use the browser UI for day-to-day browsing, the REST API for integrations, and the CLI/library for batch operations.

## What You Get

- Import ChatGPT export archives into a fast local SQLite database
- Browse conversations in a browser with sorting, pagination, and virtualized large-list views
- Read individual transcripts with a dedicated conversation view
- Search with keyword, semantic, or hybrid search modes
- Organize conversations with tags and favorites
- Export single or multiple conversations in multiple formats
- Track archive import progress in the UI
- Manage settings for the local archive app
- Script against the same archive via CLI commands or the Python API

## Architecture

The repo is now a small local stack built around one archive database:

- **Frontend**: Next.js 16, React 19, TypeScript
- **Backend**: FastAPI
- **Storage**: SQLite in `~/.chatgpt-archive/`
- **CLI / library**: `chatgpt_archive`
- **Container entrypoint**: nginx on `http://localhost`

When you run the Docker setup, nginx fronts both the web app and the API so the browser only needs one origin.

## Current Design Direction

The design is centered on a practical archive-reading experience rather than a generic admin dashboard:

- The default browser experience is a conversation workspace with navigation for conversations, search, import, favorites, and settings.
- Large archives are treated as a first-class case, with pagination and virtualized list rendering for broader browsing.
- Conversation detail pages are designed for reading transcripts, exporting, favoriting, and cleanup actions.
- Import, export, and embedding flows are integrated into the app instead of being treated as separate utilities.
- Frontend formatting work is informed by direct inspection of real ChatGPT export structures, including hidden/internal nodes and branching behavior captured in [Ground-truth-from-ChatGPT-archive.md](/Users/peternicholls/Dev/OpenAI-Chats/Ground-truth-from-ChatGPT-archive.md).

## Quick Start

### Docker

The simplest way to run the project is with Docker Compose.

```bash
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats
docker compose up -d
```

Then open `http://localhost`.

Available endpoints in the default compose setup:

- Web app: `http://localhost`
- API: `http://localhost/api`

Data is persisted on the host in `~/.chatgpt-archive/`.

### Local Development

Backend:

```bash
pip install -e .
pip install -e ./api
uvicorn api.main:app --reload
```

Frontend:

```bash
cd web
npm install
npm run dev
```

The frontend expects `NEXT_PUBLIC_API_URL` to point at the API origin it should call.

## CLI and Library

The original CLI remains useful for import, search, export, and scripting workflows.

Install the main package in editable mode:

```bash
pip install -e .
```

Optional semantic search support:

```bash
pip install -e ".[semantic]"
```

Basic examples:

```bash
chatgpt-archive import /path/to/chatgpt-export/
chatgpt-archive search "machine learning"
chatgpt-archive view <conversation-id>
chatgpt-archive export <conversation-id> -f md -o conversation.md
```

The default database path is `~/.chatgpt-archive/chats.db`. Override it with `CHATGPT_ARCHIVE_DB` or `--db`.

## Search Modes

- **Keyword search**: SQLite FTS-based text search
- **Semantic search**: embedding-backed meaning search with OpenAI
- **Hybrid search**: combines keyword and semantic results

Semantic search is optional and requires an OpenAI API key.

## Export Formats

- Markdown
- JSON
- YAML
- HTML
- XML
- CSV
- Excel

## Repository Layout

- [chatgpt_archive](/Users/peternicholls/Dev/OpenAI-Chats/chatgpt_archive): CLI, database, importer, search, exporters
- [api](/Users/peternicholls/Dev/OpenAI-Chats/api): FastAPI backend for the local web app
- [web](/Users/peternicholls/Dev/OpenAI-Chats/web): Next.js frontend
- [docs](/Users/peternicholls/Dev/OpenAI-Chats/docs): API, deployment, troubleshooting, and usage docs
- [tests](/Users/peternicholls/Dev/OpenAI-Chats/tests): CLI/library/integration tests
- [Ground-truth-from-ChatGPT-archive.md](/Users/peternicholls/Dev/OpenAI-Chats/Ground-truth-from-ChatGPT-archive.md): archive data findings that inform import and rendering decisions

## Testing

Backend and core package tests:

```bash
pytest tests/ api/tests/ -q
```

Frontend checks:

```bash
cd web
npm test -- --run
npx tsc --noEmit
```

End-to-end tests:

```bash
cd web
npm run test:e2e
```

## Notes

- Python 3.10+ is required for the CLI/library.
- Python 3.11+ is required for the API backend.
- The Docker stack currently routes traffic through nginx on port 80.
- Some secondary docs still describe older port layouts; treat `docker-compose.yml` as the source of truth for the shipped runtime.

## License

MIT
