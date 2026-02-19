# ChatGPT Archive - Deployment Guide

Deploy the ChatGPT Archive Web UI using Docker.

## Prerequisites

- Docker 24+ with Compose v2 (`docker compose` — note: no hyphen)
- 2GB available disk space
- Existing ChatGPT archive data (optional, can import via the UI)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

# Build images and start services (first run takes a few minutes)
docker compose up -d

# Open in browser
open http://localhost:3001
```

That's it! The web UI is now running.

| Service | URL |
|---------|-----|
| Web UI | http://localhost:3001 |
| API | http://localhost:8000 |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   Browser   │────▶│  Frontend   │────▶│      Backend API    │
│ :3001       │     │  (Next.js)  │     │     (FastAPI)       │
└─────────────┘     │  :3001      │     │     :8000           │
                    └─────────────┘     └──────────┬──────────┘
                                                   │
                                        ┌──────────▼──────────┐
                                        │   ~/.chatgpt-archive │
                                        │   - chats.db        │
                                        │   - settings.json   │
                                        │   - encryption.key  │
                                        └─────────────────────┘
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHATGPT_ARCHIVE_DB` | `/data/chats.db` | Database file path inside container |
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `8000` | API port |
| `CORS_ORIGINS` | `["http://localhost:3001"]` | Allowed CORS origins (JSON array) |
| `OPENAI_API_KEY` | — | OpenAI API key for semantic search (optional — can also be set via Settings UI) |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | API URL baked into the frontend at build time |

> **`NEXT_PUBLIC_API_URL` is a build-time variable** — it is compiled into the frontend bundle.
> If you change the API port or hostname, update the `args` section in `docker-compose.yml`
> and rebuild the web image (`docker compose build web`).

### Custom Port Configuration

If ports `3001` or `8000` conflict with other services, change the host-side port in `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "3002:3000"   # host:container — change left side only
    build:
      args:
        - NEXT_PUBLIC_API_URL=http://localhost:8000   # always the API host port
  api:
    ports:
      - "8001:8000"   # change host port to 8001
    environment:
      - CORS_ORIGINS=["http://localhost:3002"]
```

Then rebuild: `docker compose build && docker compose up -d`

---

## Data Persistence

Your data is stored in `~/.chatgpt-archive/` on the host machine:

```
~/.chatgpt-archive/
├── chats.db          # SQLite database
├── settings.json     # User settings
└── attachments/      # Imported file attachments
```

This directory is mounted into the container at `/data/`. Data persists across:
- Container restarts
- Image updates
- docker-compose down/up cycles

### Backup

```bash
# Stop services (optional but recommended)
docker compose stop

# Backup data
cp -r ~/.chatgpt-archive ~/.chatgpt-archive.backup

# Restart
docker compose start
```

### Migration

To move data to another machine:

```bash
# On source machine
tar -czvf chatgpt-archive-backup.tar.gz ~/.chatgpt-archive

# Transfer to destination
scp chatgpt-archive-backup.tar.gz user@new-host:~

# On destination
tar -xzvf chatgpt-archive-backup.tar.gz -C ~
docker compose up -d
```

---

## Production Deployment

### Security Considerations

⚠️ **Important Security Notices:**

1. **Network Exposure**: By default, the API binds to `0.0.0.0`, making it accessible on all network interfaces. For local-only access:
   ```yaml
   services:
     api:
       ports:
         - "127.0.0.1:8000:8000"
     web:
       ports:
         - "127.0.0.1:3000:3000"
   ```

2. **No Authentication**: The API has no built-in authentication. For shared deployments, add a reverse proxy with authentication.

3. **API Key Storage**: OpenAI API keys are encrypted at rest but consider using environment variables instead of storing in settings.

### Reverse Proxy (nginx)

For production, use nginx as a reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name archive.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }
}
```

### Resource Limits

For constrained environments:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

---

## Updating

```bash
# Pull latest changes
git pull

# Rebuild and restart (use --no-cache to force a full rebuild)
docker compose build
docker compose up -d

# Force full rebuild (clears Docker layer cache)
docker compose build --no-cache
docker compose up -d
```

---

## Developer Workflow

When iterating on the code locally, rebuild only the image you changed to save time:

```bash
# Changed anything in api/ or chatgpt_archive/
docker compose build api && docker compose up -d api

# Changed anything in web/src/ or web/public/
docker compose build web && docker compose up -d web

# Changed both
docker compose build && docker compose up -d
```

### Running Services Without Docker

For faster iteration without rebuilding images:

```bash
# Backend API (auto-reloads on file changes)
source .venv/bin/activate
uvicorn api.main:app --reload --port 8000

# Frontend (in a separate terminal)
cd web && npm run dev   # served at http://localhost:3000
```

### Running Tests

```bash
# All Python tests (225)
source .venv/bin/activate
pytest tests/ api/tests/ -q

# Frontend unit tests (81)
cd web && npm test -- --run

# Frontend E2E tests (Playwright)
cd web && npm run test:e2e
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs api
docker compose logs web

# Verify containers are running
docker compose ps
```

### Port Conflicts

If ports `3001` or `8000` are already in use, check what's using them:

```bash
lsof -iTCP -sTCP:LISTEN -P | grep -E "3001|8000"
```

Then change the host-side port in `docker-compose.yml` as described in [Custom Port Configuration](#custom-port-configuration) above.

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
