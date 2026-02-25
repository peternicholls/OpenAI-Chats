# ChatGPT Archive Search & Export

A CLI tool to import, search, view, and export your ChatGPT conversation archives.

## Features

- **Import** - Load ChatGPT export archives into a fast SQLite database
- **Search** - Full-text search across all conversations with FTS5
- **Semantic Search** (Optional) - AI-powered semantic search using OpenAI embeddings
- **View** - Display conversations in readable format
- **Export** - Export to Markdown, JSON, YAML, HTML, XML, CSV, or Excel
- **List** - Browse all imported conversations with metadata
- **Web UI** - Browser-based interface with tagging, favorites, and import via Docker

## Installation

```bash
# Clone the repository
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

# Install in development mode
pip install -e .

# Optional: Install semantic search support
pip install -e ".[semantic]"
```

## Quick Start

### 1. Import your ChatGPT export

Download your data from ChatGPT (Settings → Data controls → Export), extract the archive, then:

```bash
chatgpt-archive import /path/to/chatgpt-export/
```

**Expected output:**
```
Importing from /path/to/chatgpt-export/...
  Processed 100/1778 conversations...
  Processed 200/1778 conversations...
  ...

✓ Import complete!
  Conversations: 1,778
  Messages: 63,493
  Database: ~/.chatgpt-archive/chats.db (45.2 MB)
```

### 2. Search conversations

```bash
# Simple keyword search
chatgpt-archive search "machine learning"

# Advanced FTS5 syntax
chatgpt-archive search "python AND (tutorial OR guide)"

# Search with date range
chatgpt-archive search "python" --from 2024-01-01 --to 2024-06-30

# Limit results
chatgpt-archive search "error" --limit 5
```

**Expected output:**
```
Found 7 conversations matching "machine learning"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2024-03-15] Introduction to Neural Networks (12 messages)
ID: 6974cc29-45d8-8327-a6dc-ef1ef0a82f46

  ...about machine learning and supervised learning specifically. How do neural 
  networks work, and...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2024-02-28] Understanding Deep Learning (8 messages)
ID: 68e06336-bce4-8330-b350-f7a33ffac85e

  ...concepts in machine learning. I'd like to understand the fundamentals of deep...
```

### 3. View a conversation

```bash
chatgpt-archive view 6974cc29-45d8-8327-a6dc-ef1ef0a82f46
```

**Expected output:**
```
# Introduction to Neural Networks
Created: 2024-03-15 14:23:17 | Model: gpt-4 | 12 messages

---

**User** (14:23:17):
I'm interested in learning about machine learning and supervised learning 
specifically. How do neural networks work?

---

**Assistant** (14:23:22):
Neural networks are a fundamental concept in machine learning, inspired by 
the structure of the human brain...
```

### 4. Export a conversation

```bash
# Export to Markdown
chatgpt-archive export 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 -f md -o ml-tutorial.md

# Export to JSON (stdout)
chatgpt-archive export 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 -f json > conversation.json

# Export to HTML with styling
chatgpt-archive export 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 -f html -o chat.html
```

### 5. List all conversations

```bash
# List recent conversations
chatgpt-archive list --limit 20

# Sort by title alphabetically
chatgpt-archive list --sort title --order asc

# Sort by message count (most active first)
chatgpt-archive list --sort messages --order desc --limit 10
```

**Expected output:**
```
1,778 conversations

[2024-06-15] Python Async Programming Guide (45 messages)
  ID: 68c2f808-cea0-832a-9bbf-07fe292314c4

[2024-06-10] React Component Optimization (23 messages)
  ID: 68cd640c-c7f8-8332-8083-7fadfd34af16

[2024-06-05] Database Schema Design (31 messages)
  ID: 68e06336-bce4-8330-b350-f7a33ffac85e

(showing 1-20 of 1,778)
```

## Optional: Semantic Search

For AI-powered semantic search (finds concepts, not just keywords):

### 1. Install semantic search dependencies

```bash
pip install -e ".[semantic]"
```

### 2. Generate embeddings

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Generate embeddings for all messages (one-time, ~$2-5 for 64K messages)
chatgpt-archive embed

# Or embed during import (slower but convenient)
chatgpt-archive import /path/to/archive --embed
```

### 3. Search semantically

```bash
# Semantic search (finds related concepts)
chatgpt-archive search "neural networks" --semantic

# Hybrid search (keyword + semantic, best results)
chatgpt-archive search "machine learning" --hybrid
```

**Note**: Semantic search requires an OpenAI API key and costs ~$0.02 per 1M tokens (~$2-5 for 64K messages, one-time).

## Common Use Cases

### Finding Code Examples

```bash
# Find Python tutorials
chatgpt-archive search "python tutorial" --limit 10

# Find debugging discussions
chatgpt-archive search "error OR bug OR debug" --from 2024-01-01

# Export a helpful tutorial
chatgpt-archive export <id> -f md -o python-guide.md
```

### Archiving Important Conversations

```bash
# Find all conversations about a project
chatgpt-archive search "project-name"

# Export multiple conversations by searching and exporting each
chatgpt-archive search "project-name" --json | \
  jq -r '.results[].id' | \
  while read id; do
    chatgpt-archive export "$id" -f md -o "archive/${id}.md"
  done
```

### Data Analysis & Statistics

```bash
# Get conversation statistics in JSON
chatgpt-archive list --json | jq '{
  total: .total,
  avg_messages: ([.conversations[].message_count] | add / length)
}'

# Find longest conversations
chatgpt-archive list --sort messages --order desc --limit 10

# Search by date range to analyze usage patterns
chatgpt-archive search "*" --from 2024-01-01 --to 2024-01-31 --json
```

### Migration & Backup

```bash
# Export entire archive to Markdown
mkdir -p backup/markdown
chatgpt-archive list --json | jq -r '.conversations[].id' | \
  while read id; do
    chatgpt-archive export "$id" -f md -o "backup/markdown/${id}.md"
  done

# Create timestamped database backup
cp ~/.chatgpt-archive/chats.db \
   ~/backups/chats-$(date +%Y%m%d).db
```

### Working with JSON Output

```bash
# Find conversations and process with jq
chatgpt-archive search "API design" --json | \
  jq '.results[] | {title, date: .create_time, id}'

# Get conversation titles programmatically
chatgpt-archive list --limit 1000 --json | \
  jq -r '.conversations[] | "\(.create_time | strftime("%Y-%m-%d")): \(.title)"'

# Export search results to CSV
chatgpt-archive search "python" --json | \
  jq -r '.results[] | [.id, .title, .message_count] | @csv' > results.csv
```

### Using Different Database Locations

```bash
# Import to project-specific database
chatgpt-archive --db ./project-chats.db import ~/Downloads/export/

# Search in specific database
chatgpt-archive --db ./project-chats.db search "implementation"

# Use environment variable for session
export CHATGPT_ARCHIVE_DB=~/work/chats.db
chatgpt-archive import ~/Downloads/work-export/
chatgpt-archive search "meeting notes"
```

### Advanced Search with FTS5 Syntax

```bash
# Boolean operators
chatgpt-archive search "python AND (flask OR django)"
chatgpt-archive search "NOT error"

# Phrase search
chatgpt-archive search '"machine learning"'

# Proximity search (words near each other)
chatgpt-archive search 'NEAR(neural network, 5)'

# Column-specific search (searches in message content)
chatgpt-archive search "content:api"
```

## Commands

| Command | Description |
|---------|-------------|
| `import <dir>` | Import conversations from ChatGPT export directory |
| `search <query>` | Search conversations by keyword or phrase |
| `list` | List all imported conversations |
| `view <id>` | View a specific conversation |
| `export <id>` | Export a conversation to file |
| `embed` | Generate embeddings for semantic search (optional) |

## Options

### Global Options

| Option | Description |
|--------|-------------|
| `--db PATH` | Database file path (default: `~/.chatgpt-archive/chats.db`) |
| `--json` | Output in JSON format for scripting |
| `--help` | Show help message |
| `--version` | Show version |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CHATGPT_ARCHIVE_DB` | Override default database location |
| `OPENAI_API_KEY` | OpenAI API key (required for semantic search) |

## Export Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Markdown | `-f md` | Human-readable documentation |
| JSON | `-f json` | Programmatic access, re-import |
| YAML | `-f yaml` | Configuration, human-editable structured |
| HTML | `-f html` | Browser viewing, sharing |
| XML | `-f xml` | Legacy system integration |

## Database Location

By default, the database is stored at `~/.chatgpt-archive/chats.db`. You can override this with:

```bash
# Per-command
chatgpt-archive --db /custom/path/chats.db import ./archive

# Environment variable
export CHATGPT_ARCHIVE_DB=/custom/path/chats.db
chatgpt-archive import ./archive
```

## Requirements

- Python 3.10+ for CLI and library usage
- Python 3.11+ for running the API backend locally
- No external services required (fully offline)

## Web UI (Docker)

A browser-based interface is available via Docker.

### Running with Docker

```bash
# Build and start all services
docker compose up -d

# Web UI:  http://localhost
# API:     http://localhost/api
```

> **First run**: the build step takes a few minutes. Subsequent starts are instant.
>
> All traffic is routed through an nginx reverse proxy on port 80. The `web` and `api`
> services are not exposed directly to the host.

### Stopping

```bash
docker compose down        # stop (data is preserved)
docker compose down -v     # stop AND delete all data
```

### Features

- Browse and search conversations
- Tag and favorite conversations for organization
- Import archives via drag-and-drop (maximum 500MB per file)
- Export to multiple formats
- Real-time import progress tracking

### Development & Testing

```bash
# Run all backend tests (225 tests)
source .venv/bin/activate
pytest tests/ api/tests/ -q

# Run frontend unit tests with Vitest
cd web && npm test -- --run

# Run E2E tests with Playwright
cd web && npm run test:e2e
```

### Rebuilding After Code Changes

When you modify Python or frontend source files, rebuild the relevant image:

```bash
# Rebuild and restart everything
docker compose build && docker compose up -d

# Rebuild only the API (Python changes)
docker compose build api && docker compose up -d api

# Rebuild only the web (frontend changes)
docker compose build web && docker compose up -d web
```

> **Tip**: The web image bakes `NEXT_PUBLIC_API_URL` at build time. If you change
> the API port, update the `args` section in `docker-compose.yml` and rebuild the web image.

### Running Services Locally (without Docker)

```bash
# Backend API
source .venv/bin/activate
uvicorn api.main:app --reload

# Frontend
cd web && npm run dev
```

### Web UI Features

The web interface includes:

- **Conversation Browser** - List, sort, and paginate through conversations
- **Full-Text Search** - Real-time search with result highlighting
- **Semantic Search** - AI-powered search (requires OpenAI API key)
- **Tags & Favorites** - Organize conversations with tags and favorites
- **Batch Export** - Export multiple conversations at once
- **Import Progress** - Real-time SSE progress during archive import  
- **Dark Mode** - System-aware theme switching
- **Embedding Management** - Generate and manage semantic search embeddings with cost controls

### Configuration

Environment variables (set in `.env` or `docker-compose.yml`):

| Variable | Description | Default |
|----------|-------------|---------|
| `CHATGPT_ARCHIVE_DB` | Database file path (inside container) | `/data/chats.db` |
| `CORS_ORIGINS` | Allowed origins (JSON array) | `["http://localhost"]` |
| `API_HOST` | API bind address | `0.0.0.0` |
| `TRUSTED_PROXY_IPS` | Proxy IPs whose `X-Forwarded-For` headers are trusted | `127.0.0.1,::1` |

### Security

The API includes comprehensive security:
- **Content Security Policy** (CSP) to prevent XSS
- **X-Frame-Options** to prevent clickjacking
- **Input validation** and sanitization on all endpoints
- **Rate limiting** – enabled by default; set `DISABLE_RATE_LIMIT=1` only in non-production environments (e.g., automated tests)
- **Upload size limit** – archive imports are capped at **500 MB** per file; the API returns HTTP 413 with a clear message if the limit is exceeded
- **Environment variable validation** on startup
- **API key encryption** at rest using Fernet
- **0.0.0.0 binding warning** logged when exposed to network

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#web-ui-issues) for common issues.

## License

MIT
