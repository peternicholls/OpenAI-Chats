# OpenAI-Chats Deployment Guide

This guide covers the current runtime shipped by this repository. The default Docker setup exposes a single browser entrypoint through nginx at `http://localhost` and proxies `/api` traffic to the FastAPI backend.

## Quick Start

### Docker Compose

```bash
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats
docker compose up -d
```

Open `http://localhost` in your browser.

Default compose URLs:

| Surface | URL |
|---------|-----|
| App | `http://localhost` |
| API via nginx | `http://localhost/api` |

The `web` and `api` containers are not exposed directly to the host in the default compose file.

## Runtime Layout

```text
Browser
  -> nginx (:80 on host)
    -> Next.js web container
    -> FastAPI api container
      -> ~/.chatgpt-archive on the host
```

The host data directory is mounted into the API container at `/data`.

## Data Storage

Application data is stored in `~/.chatgpt-archive/` on the host:

```text
~/.chatgpt-archive/
├── chats.db
├── settings.json
├── encryption.key
└── attachments/
```

Back up the whole directory, not just the database, so encrypted settings remain readable.

### Backup

```bash
docker compose stop
cp -r ~/.chatgpt-archive ~/.chatgpt-archive.backup
docker compose start
```

### Migration

```bash
tar -czvf chatgpt-archive-backup.tar.gz ~/.chatgpt-archive
scp chatgpt-archive-backup.tar.gz user@new-host:~
ssh user@new-host 'tar -xzvf ~/chatgpt-archive-backup.tar.gz -C ~'
```

## Compose Configuration

The current `docker-compose.yml` uses these key settings:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CHATGPT_ARCHIVE_DB` | `/data/chats.db` | Database path inside the API container |
| `API_HOST` | `0.0.0.0` | API bind address inside Docker |
| `API_PORT` | `8000` | Internal API port |
| `CORS_ORIGINS` | `["http://localhost"]` | Browser origins allowed to call the API |
| `TRUSTED_PROXY_IPS` | `127.0.0.1,::1` | Proxy IPs trusted for forwarded headers |
| `NEXT_PUBLIC_API_URL` | `http://localhost` | Browser-facing base URL baked into the web build |

`NEXT_PUBLIC_API_URL` is a build-time variable for the frontend. If you change it, rebuild the `web` image.

## Changing the Exposed Port

If host port `80` is already in use, change the nginx port mapping, then keep the browser-facing API URL aligned with the new host origin.

Example: expose the stack on `http://localhost:8080`

```yaml
services:
  nginx:
    ports:
      - "8080:80"

  web:
    build:
      args:
        - NEXT_PUBLIC_API_URL=http://localhost:8080
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8080

  api:
    environment:
      - CORS_ORIGINS=["http://localhost:8080"]
```

Then rebuild:

```bash
docker compose build web api nginx
docker compose up -d
```

## Local Development Without Docker

For faster iteration, run the backend and frontend separately:

Backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e ./api
uvicorn api.main:app --reload --port 8000
```

Frontend:

```bash
cd web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

In local development, the browser typically uses:

| Surface | URL |
|---------|-----|
| Frontend dev server | `http://localhost:3000` |
| FastAPI dev server | `http://localhost:8000` |
| OpenAPI docs | `http://localhost:8000/docs` |

## Updating the Stack

```bash
git pull
docker compose build
docker compose up -d
```

Rebuild one service when only one side changed:

```bash
docker compose build api && docker compose up -d api
docker compose build web && docker compose up -d web
```

## Security Notes

- The project is designed for single-user local deployment by default.
- The API has no built-in authentication.
- `API_HOST=0.0.0.0` is expected inside Docker, but do not expose the stack to an untrusted network without adding auth and a hardened reverse proxy.
- The OpenAI API key is stored encrypted in `settings.json` using `encryption.key`.

## Troubleshooting Quick Checks

```bash
docker compose ps
docker compose logs api
docker compose logs web
curl http://localhost/api/health
```

If you are running the backend directly instead of through nginx, use `curl http://localhost:8000/api/health`.

### Permission Denied on Volume

```bash
# Ensure directory exists with correct permissions
mkdir -p ~/.chatgpt-archive
chmod 755 ~/.chatgpt-archive
```

### Database Issues

```bash
# Check database integrity
sqlite3 ~/.chatgpt-archive/chats.db "PRAGMA integrity_check;"

# Reset if corrupted (data loss!)
rm ~/.chatgpt-archive/chats.db
docker compose restart api
```

### Health Check Failures

```bash
# Test API directly
curl http://localhost:8000/api/health

# Check container health status
docker inspect --format='{{.State.Health.Status}}' openai-chats-api-1
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 1GB | 2GB+ |
| Disk | 1GB + data | 5GB + data |
| Docker | 20.10 | Latest |

---

## Logs

View logs in real-time:

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f web
```

---

## Stopping

```bash
# Stop services (data is preserved)
docker compose down

# Stop and remove all data volumes (DELETES DATA)
docker compose down -v
```

---

## See Also

- [README.md](../README.md) - Overview
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting
- [REST-API.md](REST-API.md) - API reference
