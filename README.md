# ChatGPT Archive Search & Export

A CLI tool to import, search, view, and export your ChatGPT conversation archives.

## Features

- **Import** - Load ChatGPT export archives into a fast SQLite database
- **Search** - Full-text search across all conversations with FTS5
- **View** - Display conversations in readable format
- **Export** - Export to Markdown, JSON, YAML, HTML, or XML
- **List** - Browse all imported conversations with metadata

## Installation

```bash
# Clone the repository
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

# Install in development mode
pip install -e .
```

## Quick Start

### 1. Import your ChatGPT export

Download your data from ChatGPT (Settings → Data controls → Export), extract the archive, then:

```bash
chatgpt-archive import /path/to/chatgpt-export/
```

### 2. Search conversations

```bash
# Simple keyword search
chatgpt-archive search "machine learning"

# Search with date range
chatgpt-archive search "python" --from 2024-01-01 --to 2024-06-30
```

### 3. View a conversation

```bash
chatgpt-archive view <conversation-id>
```

### 4. Export a conversation

```bash
# Export to Markdown
chatgpt-archive export <conversation-id> -f md -o conversation.md

# Export to JSON (stdout)
chatgpt-archive export <conversation-id> -f json
```

### 5. List all conversations

```bash
# List recent conversations
chatgpt-archive list --limit 20

# Sort by title
chatgpt-archive list --sort title --order asc
```

## Commands

| Command | Description |
|---------|-------------|
| `import <dir>` | Import conversations from ChatGPT export directory |
| `search <query>` | Search conversations by keyword or phrase |
| `list` | List all imported conversations |
| `view <id>` | View a specific conversation |
| `export <id>` | Export a conversation to file |

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

- Python 3.8+
- No external services required (fully offline)

## License

MIT
