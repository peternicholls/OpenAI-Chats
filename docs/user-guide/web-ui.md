# ChatGPT Archive Web UI

Run the browser UI locally with Docker, or run the API and frontend separately during development.

## At a Glance

- Docker entrypoint: `docker compose up -d`
- Browser URL: `http://localhost`
- Public routing in Docker:
  - `/` -> Next.js frontend
  - `/api/` -> FastAPI backend
- Persistent host data: `~/.chatgpt-archive/`

## Key Interface Behaviors

- The sidebar keeps search, favorites, tags, and utility actions fixed while the conversation list scrolls independently.
- The conversation list is loaded in pages and automatically fetches more conversations when you reach the bottom of the current list.
- Conversation rows, site-brand links, utility actions, and archive controls use a consistent custom tooltip treatment instead of mixed native hover titles.
- Conversation transcripts render formatted markdown, code blocks, tables, math, inline media, and readable fallback blocks rather than exposing raw export payloads.
- Assistant turns condense reasoning and tool activity into compact disclosure blocks so technical export noise does not dominate the reading experience.

## Docker Quick Start

```bash
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

docker compose up -d
open http://localhost
```

Check service status:

```bash
docker compose ps
docker compose logs nginx
docker compose logs api
docker compose logs web
```

If the frontend container is recreated during a rebuild and `http://localhost` briefly returns `502 Bad Gateway`, restart nginx so it refreshes the web upstream target:

```bash
docker compose restart nginx
```

Stop the stack:

```bash
docker compose down
```

## Serving Model

The Docker stack uses three services:

```text
Browser -> nginx (:80) -> web (:3000)
                    -> api (:8000)
```

Details:

- `nginx` is the only service exposed to the host.
- `web` is the production Next.js standalone server created by `next build`.
- `api` runs `uvicorn api.main:app`.
- SSE buffering is disabled in nginx so import progress streams correctly.
- Uploads are capped at `500M` by nginx.

## Data and Media

The API stores its runtime data in `~/.chatgpt-archive/` on the host:

```text
~/.chatgpt-archive/
├── chats.db
├── settings.json
├── encryption.key
└── media/
```

Media handling:

- `CHATGPT_ARCHIVE_DIR` points at the extracted archive or a persistent media directory.
- Attachment files stay on disk and are served from the filesystem at request time.
- If you already have an extracted OpenAI export, mount it read-only and point `CHATGPT_ARCHIVE_DIR` at it.

Example API service override:

```yaml
services:
  api:
    volumes:
      - ${HOME}/.chatgpt-archive:/data
      - /path/to/chatgpt-export:/archive:ro
    environment:
      - CHATGPT_ARCHIVE_DB=/data/chats.db
      - CHATGPT_ARCHIVE_DIR=/archive
```

## Configuration

### Important Environment Variables

| Variable | Default | Notes |
| --- | --- | --- |
| `CHATGPT_ARCHIVE_DB` | `/data/chats.db` | SQLite database inside the API container |
| `CHATGPT_ARCHIVE_DIR` | `/data/media` | Archive/media source directory |
| `API_HOST` | `0.0.0.0` | Required for container networking |
| `API_PORT` | `8000` | Internal API port |
| `CORS_ORIGINS` | `["http://localhost"]` | JSON array of allowed browser origins |
| `TRUSTED_PROXY_IPS` | `127.0.0.1,::1` | Trusted forwarded-header sources |
| `OPENAI_API_KEY` | unset | Enables semantic search |
| `NEXT_PUBLIC_API_URL` | `http://localhost` | Browser-facing API URL compiled into the frontend build |

`NEXT_PUBLIC_API_URL` is a build-time variable. If you change the browser-visible hostname or port, rebuild the web image:

```bash
docker compose build web
docker compose up -d web
```

## Custom Ports

By default the stack serves on host port `80`. If that conflicts with another service, change the nginx port mapping and keep the browser-facing frontend build arg aligned with the new public origin.

Example using host port `8080`:

```yaml
services:
  nginx:
    ports:
      - "8080:80"

  api:
    environment:
      - CORS_ORIGINS=["http://localhost:8080"]

  web:
    build:
      args:
        - NEXT_PUBLIC_API_URL=http://localhost:8080
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8080
```

Then rebuild the web service:

```bash
docker compose build web
docker compose up -d
```

## Local Development Without Docker

Backend:

```bash
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Useful endpoints during local development:

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## Production Notes

- The API is designed for trusted single-user or self-hosted environments.
- There is no built-in multi-user authentication layer.
- If you expose the stack outside localhost, place it behind an authenticated reverse proxy and review `CORS_ORIGINS`.
- Back up `~/.chatgpt-archive/encryption.key` together with `settings.json`; encrypted settings cannot be recovered without it.

## See Also

- [User Guide Index](README.md)
- [CLI Reference](usage.md)
- [Troubleshooting](troubleshooting.md)
- [REST API Reference](../REST-API.md)
