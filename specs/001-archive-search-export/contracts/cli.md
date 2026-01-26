# CLI Contract: ChatGPT Archive Search & Export

**Feature**: 001-archive-search-export | **Date**: 2026-01-26

## Command Overview

```
chatgpt-archive <command> [options] [arguments]

Commands:
  import   Import conversations from ChatGPT export archive
  search   Search conversations by keyword or phrase
  list     List all imported conversations
  view     View a specific conversation
  export   Export a conversation to file
```

## Global Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--db` | `-d` | PATH | `~/.chatgpt-archive/chats.db` | Database file path |
| `--json` | `-j` | FLAG | false | Output in JSON format (machine-readable) |
| `--help` | `-h` | FLAG | - | Show help and exit |
| `--version` | `-v` | FLAG | - | Show version and exit |

---

## Commands

### import

Import conversations from a ChatGPT export directory.

```
chatgpt-archive import <archive-dir> [options]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `archive-dir` | Yes | Path to extracted ChatGPT export directory |

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--db` | PATH | default | Database file location |

**Exit Codes:**
- `0`: Success
- `1`: Archive directory not found
- `2`: Invalid JSON structure
- `3`: Database error

**Output (human):**
```
Importing from /path/to/archive...
Found 1,778 conversations
Imported: 1,778 conversations, 45,231 messages
Database: ~/.chatgpt-archive/chats.db (156 MB)
```

**Output (--json):**
```json
{
  "status": "success",
  "conversations_imported": 1778,
  "messages_imported": 45231,
  "database_path": "/Users/user/.chatgpt-archive/chats.db",
  "database_size_bytes": 163577856
}
```

---

### search

Search conversations by keyword, phrase, or date range.

```
chatgpt-archive search <query> [options]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `query` | Yes | Search term or phrase (FTS5 syntax supported) |

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--from` | DATE | - | Filter: conversations created after this date (YYYY-MM-DD) |
| `--to` | DATE | - | Filter: conversations created before this date (YYYY-MM-DD) |
| `--limit` | INT | 20 | Maximum results to return |
| `--db` | PATH | default | Database file location |
| `--json` | FLAG | false | JSON output |

**Exit Codes:**
- `0`: Success (including no results)
- `1`: Database not found
- `2`: Invalid query syntax

**Output (human):**
```
Found 12 conversations matching "machine learning"

1. [2024-03-15] Neural Network Architecture
   "...discussing machine learning models for image classification..."
   ID: 6974cc29-45d8-8327-a6dc-ef1ef0a82f46

2. [2024-02-28] Python ML Tutorial
   "...best practices for machine learning in Python..."
   ID: abc123...

(showing 2 of 12 results)
```

**Output (--json):**
```json
{
  "query": "machine learning",
  "total_results": 12,
  "results": [
    {
      "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
      "title": "Neural Network Architecture",
      "create_time": 1710518400,
      "preview": "...discussing machine learning models for image classification...",
      "relevance_score": 0.85
    }
  ]
}
```

---

### list

List all imported conversations with metadata.

```
chatgpt-archive list [options]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--sort` | CHOICE | `date` | Sort by: `date`, `title`, `messages` |
| `--order` | CHOICE | `desc` | Order: `asc`, `desc` |
| `--limit` | INT | 50 | Maximum results |
| `--offset` | INT | 0 | Skip first N results (pagination) |
| `--db` | PATH | default | Database file location |
| `--json` | FLAG | false | JSON output |

**Exit Codes:**
- `0`: Success
- `1`: Database not found

**Output (human):**
```
1,778 conversations

[2024-03-20] Pub Manager Conflict (8 messages)
  ID: 6974cc29-45d8-8327-a6dc-ef1ef0a82f46

[2024-03-19] Code Review Best Practices (23 messages)
  ID: abc123...

(showing 50 of 1,778)
```

**Output (--json):**
```json
{
  "total": 1778,
  "offset": 0,
  "limit": 50,
  "conversations": [
    {
      "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
      "title": "Pub Manager Conflict",
      "create_time": 1710892800,
      "update_time": 1710893200,
      "message_count": 8,
      "model": "gpt-5-2-thinking"
    }
  ]
}
```

---

### view

View a specific conversation.

```
chatgpt-archive view <conversation-id> [options]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `conversation-id` | Yes | OpenAI conversation ID |

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--db` | PATH | default | Database file location |
| `--json` | FLAG | false | JSON output |

**Exit Codes:**
- `0`: Success
- `1`: Database not found
- `2`: Conversation not found

**Output (human):**
```
# Pub Manager Conflict
Created: 2024-03-20 14:15:30 | Model: gpt-5-2-thinking | 8 messages

---

**User** (14:15:30):
Script time again! This weeks: J manager of a pub...

---

**Assistant** (14:15:45):
Here's a dramatic script based on your scenario...
```

**Output (--json):**
```json
{
  "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
  "title": "Pub Manager Conflict",
  "create_time": 1710892530,
  "model": "gpt-5-2-thinking",
  "messages": [
    {
      "id": "f792fe2b-a623-49e2-8a04-c03050380076",
      "role": "user",
      "content": "Script time again! This weeks...",
      "create_time": 1710892530
    }
  ]
}
```

---

### export

Export a conversation to a file in the specified format.

```
chatgpt-archive export <conversation-id> --format <format> [options]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `conversation-id` | Yes | OpenAI conversation ID |

**Options:**
| Option | Short | Type | Required | Default | Description |
|--------|-------|------|----------|---------|-------------|
| `--format` | `-f` | CHOICE | Yes | - | Output format: `md`, `json`, `yaml`, `html`, `xml` |
| `--output` | `-o` | PATH | No | stdout | Output file path |
| `--db` | `-d` | PATH | No | default | Database file location |

**Exit Codes:**
- `0`: Success
- `1`: Database not found
- `2`: Conversation not found
- `3`: Invalid format
- `4`: File write error

**Output:**
- If `--output` specified: writes to file, prints confirmation
- If no `--output`: writes formatted content to stdout

**Example:**
```bash
# Export to markdown file
chatgpt-archive export abc123 -f md -o conversation.md

# Export to stdout as YAML
chatgpt-archive export abc123 -f yaml

# Export to HTML
chatgpt-archive export abc123 -f html -o chat.html
```

---

## Error Output

All errors are written to stderr with descriptive messages:

```
Error: Archive directory not found: /path/to/archive
Error: Database not found. Run 'chatgpt-archive import' first.
Error: Conversation not found: invalid-id-123
Error: Invalid date format. Use YYYY-MM-DD.
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHATGPT_ARCHIVE_DB` | Database file path | `~/.chatgpt-archive/chats.db` |

---

## Exit Code Summary

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Resource not found (directory, database, conversation) |
| 2 | Invalid input (JSON, query, format) |
| 3 | Database/storage error |
| 4 | File I/O error |
