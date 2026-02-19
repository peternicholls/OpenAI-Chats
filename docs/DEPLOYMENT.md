# ChatGPT Archive - Deployment Guide

Deploy the ChatGPT Archive Web UI using Docker.

## Prerequisites

- Docker 20.10+
- Docker Compose v2+
- 2GB available disk space
- Existing ChatGPT archive data (optional, can import later)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

# Start the services
docker-compose up -d

# Open in browser
open http://localhost:3000
```

That's it! The web UI is now running.

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   Browser   │────▶│  Frontend   │────▶│      Backend API    │
│ :3000       │     │  (Next.js)  │     │     (FastAPI)       │
└─────────────┘     │  :3000      │     │     :8000           │
                    └─────────────┘     └──────────┬──────────┘
                                                   │
                                        ┌──────────▼──────────┐
                                        │   ~/.chatgpt-archive │
                                        │   - archive.db      │
                                        │   - settings.json   │
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
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins (JSON array) |
| `OPENAI_API_KEY` | — | OpenAI API key for semantic search |
| `NEXT_PUBLIC_API_URL` | `http://api:8000` | API URL for frontend |

### Custom Configuration

Create a `.env` file in the project root:

```bash
# .env
CHATGPT_ARCHIVE_DB=/data/chats.db
CORS_ORIGINS=["http://localhost:3000","https://your-domain.com"]
OPENAI_API_KEY=sk-...
```

Or override in docker-compose:

```yaml
services:
  api:
    environment:
      - CHATGPT_ARCHIVE_DB=/data/chats.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

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
docker-compose stop

# Backup data
cp -r ~/.chatgpt-archive ~/.chatgpt-archive.backup

# Restart
docker-compose start
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
docker-compose up -d
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

# Rebuild containers
docker-compose build --no-cache

# Restart with new images
docker-compose up -d
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs api
docker-compose logs web

# Verify containers are running
docker-compose ps
```

### Port Conflicts

If ports 3000 or 8000 are in use:

```yaml
# docker-compose.yml
services:
  web:
    ports:
      - "3001:3000"  # Use 3001 instead
  api:
    ports:
      - "8001:8000"  # Use 8001 instead
```

Update `CORS_ORIGINS` and `NEXT_PUBLIC_API_URL` accordingly.

### Permission Denied on Volume

```bash
# Ensure directory exists
mkdir -p ~/.chatgpt-archive

# Check permissions
ls -la ~/.chatgpt-archive

# Fix permissions if needed
chmod 755 ~/.chatgpt-archive
```

### Database Issues

```bash
# Check database integrity
sqlite3 ~/.chatgpt-archive/chats.db "PRAGMA integrity_check;"

# Reset if corrupted (data loss!)
rm ~/.chatgpt-archive/chats.db
docker-compose restart api
```

### Health Check Failures

```bash
# Test API directly
curl http://localhost:8000/api/health

# Check container health
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
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f web
```

---

## Stopping

```bash
# Stop services (preserves data)
docker-compose down

# Stop and remove volumes (DELETES DATA)
docker-compose down -v
```

---

## See Also

- [README.md](../README.md) - Overview
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting
- [REST-API.md](REST-API.md) - API reference
