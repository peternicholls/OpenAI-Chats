# ChatGPT Archive - Usage Guide

Comprehensive reference for all commands, options, and features.

## Table of Contents

- [Global Options](#global-options)
- [Commands](#commands)
  - [import](#import)
  - [verify-media](#verify-media)
  - [search](#search)
  - [view](#view)
  - [export](#export)
  - [list](#list)
  - [embed](#embed)
- [Exit Codes](#exit-codes)
- [Output Formats](#output-formats)
- [Advanced Usage](#advanced-usage)

## Global Options

These options can be used with any command:

### `--db PATH` / `-d PATH`

Specify a custom database file location.

**Default**: `~/.chatgpt-archive/chats.db`

**Environment Variable**: `CHATGPT_ARCHIVE_DB`

**Examples**:
```bash
# Use custom database
chatgpt-archive --db ~/my-chats.db import ./archive

# Environment variable (affects all commands in session)
export CHATGPT_ARCHIVE_DB=~/work/chats.db
chatgpt-archive import ./work-archive
chatgpt-archive search "project"
```

### `--json` / `-j`

Output results in JSON format instead of human-readable text. Useful for scripting and programmatic access.

**Examples**:
```bash
# Get import results as JSON
chatgpt-archive import ./archive --json

# Process search results with jq
chatgpt-archive search "python" --json | jq '.results[].title'
```

### `--version`

Display the version number and exit.

```bash
chatgpt-archive --version
# Output: chatgpt-archive, version 1.0.0
```

### `--help`

Show help message and available commands.

```bash
chatgpt-archive --help
chatgpt-archive import --help  # Command-specific help
```

---

## Commands

### `import`

Import conversations from a ChatGPT export archive.

**Syntax**:
```bash
chatgpt-archive import ARCHIVE_DIR [OPTIONS]
```

**Arguments**:
- `ARCHIVE_DIR` (required): Path to the extracted ChatGPT export directory containing `conversations.json`

**Options**:
- `--json`: Output results in JSON format

**Exit Codes**:
- `0`: Success
- `1`: Invalid archive (missing conversations.json or wrong format)
- `2`: Invalid JSON (malformed conversations.json)
- `3`: Import failed (database error or other failure)

**Examples**:
```bash
# Basic import
chatgpt-archive import ~/Downloads/chatgpt-export

# Import to custom database
chatgpt-archive --db ./project.db import ~/Downloads/export

# Get JSON output
chatgpt-archive import ./archive --json
```

**Output (Human)**:
```
Importing from ~/Downloads/chatgpt-export...
  Processed 100/1778 conversations...
  Processed 500/1778 conversations...
  Processed 1000/1778 conversations...
  Processed 1500/1778 conversations...

✓ Import complete!
  Conversations: 1,778
  Messages: 63,493
  Database: ~/.chatgpt-archive/chats.db (45.2 MB)
```

**Output (JSON)**:
```json
{
  "status": "success",
  "conversations_imported": 1778,
  "messages_imported": 63493,
  "database_path": "~/.chatgpt-archive/chats.db",
  "database_size_bytes": 47397632,
  "archive_media_dir": "~/.chatgpt-archive/media"
}
```

**Behavior**:
- Idempotent: Re-importing the same archive updates existing conversations
- Title fallback: Uses first user message if title is missing, or "[Untitled]"
- Attachment detection: Extracts file references from message content
- Progress updates: Shows progress every 100 conversations (stderr)

### `verify-media`

Verify the archive media directory used for inline images, audio, and file attachments.

**Syntax**:
```bash
chatgpt-archive verify-media [ARCHIVE_DIR] [OPTIONS]
```

**Arguments**:
- `ARCHIVE_DIR` (optional): Override the configured media directory for this check

**Environment Variables**:
- `CHATGPT_ARCHIVE_DIR`: Preferred archive media directory
- `CHATGPT_ARCHIVE_DB`: Used to derive the default fallback media directory (`<db parent>/media`)

**Examples**:
```bash
chatgpt-archive verify-media
chatgpt-archive verify-media ~/Downloads/chatgpt-export --json
```

**Output (JSON)**:
```json
{
  "archive_media_dir": "/Users/example/Downloads/chatgpt-export",
  "exists": true,
  "has_conversations_json": true,
  "root_file_count": 12,
  "conversation_dir_count": 45
}
```

---

### `search`

Search conversations using full-text search (FTS5) or semantic search.

**Syntax**:
```bash
chatgpt-archive search QUERY [OPTIONS]
```

**Arguments**:
- `QUERY` (required): Search term or FTS5 expression

**Options**:
- `--from DATE`: Filter conversations created after DATE (YYYY-MM-DD format)
- `--to DATE`: Filter conversations created before DATE (YYYY-MM-DD format)
- `--limit N` / `-l N`: Maximum results to return (default: 20)
- `--semantic`: Use semantic/vector search instead of keyword search
- `--hybrid`: Combine keyword and semantic search for best results
- `--json`: Output in JSON format

**Exit Codes**:
- `0`: Success (even if 0 results found)
- `1`: Database not found
- `2`: Invalid query syntax

**FTS5 Query Syntax**:
- `word1 word2`: Search for both words (implicit AND)
- `word1 OR word2`: Either word
- `word1 AND word2`: Both words (explicit)
- `NOT word`: Exclude word
- `"exact phrase"`: Phrase search
- `word*`: Prefix search
- `NEAR(word1 word2, 5)`: Words within 5 tokens of each other

**Examples**:
```bash
# Simple keyword search
chatgpt-archive search "machine learning"

# Boolean operators
chatgpt-archive search "python AND (flask OR django)"
chatgpt-archive search "NOT error"

# Phrase search
chatgpt-archive search '"neural network"'

# Date filtering
chatgpt-archive search "api" --from 2024-01-01 --to 2024-06-30

# Limit results
chatgpt-archive search "error" --limit 5

# Semantic search (requires embeddings)
chatgpt-archive search "deep learning concepts" --semantic

# Hybrid search (best results)
chatgpt-archive search "machine learning" --hybrid

# JSON output for scripting
chatgpt-archive search "python" --json | jq '.results[].title'
```

**Output (Human)**:
```
Found 7 conversations matching "machine learning"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2024-03-15] Introduction to Neural Networks (12 messages)
ID: 6974cc29-45d8-8327-a6dc-ef1ef0a82f46

  ...about machine learning and supervised learning specifically. How do neural 
  networks work, and...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Output (JSON)**:
```json
{
  "query": "machine learning",
  "total": 7,
  "results": [
    {
      "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
      "title": "Introduction to Neural Networks",
      "create_time": 1710513797.123,
      "message_count": 12,
      "match_count": 3,
      "snippet": "...about machine learning and supervised learning..."
    }
  ]
}
```

**Notes**:
- Searches message content only (not titles)
- Case-insensitive
- Results ranked by relevance (BM25 for keyword, cosine similarity for semantic)
- Snippet shows context around matches (configured in search.py)
- Semantic search requires running `embed` command first

---

### `view`

Display the full content of a specific conversation.

**Syntax**:
```bash
chatgpt-archive view CONVERSATION_ID [OPTIONS]
```

**Arguments**:
- `CONVERSATION_ID` (required): The OpenAI conversation ID (UUID format, shown in search/list output)

**Options**:
- `--json`: Output in JSON format

**Exit Codes**:
- `0`: Success
- `1`: Database not found
- `2`: Conversation not found
- `3`: View failed (database error)

**Examples**:
```bash
# View conversation
chatgpt-archive view 6974cc29-45d8-8327-a6dc-ef1ef0a82f46

# JSON output
chatgpt-archive view 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 --json

# Pipe to file
chatgpt-archive view 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 > conversation.txt

# Search and view first result
ID=$(chatgpt-archive search "python tutorial" --limit 1 --json | jq -r '.results[0].id')
chatgpt-archive view "$ID"
```

**Output (Human)**:
```
# Introduction to Neural Networks
Created: 2024-03-15 14:23:17 | Model: gpt-4 | 12 messages

---

**User** (14:23:17):
I'm interested in learning about machine learning and supervised learning 
specifically. How do neural networks work?

---

**Assistant** (14:23:22):
Neural networks are a fundamental concept in machine learning...
```

**Output (JSON)**:
```json
{
  "id": "6974cc29-45d8-8327-a6dc-ef1ef0a82f46",
  "title": "Introduction to Neural Networks",
  "create_time": 1710513797.123,
  "update_time": 1710514892.456,
  "model": "gpt-4",
  "message_count": 12,
  "messages": [
    {
      "id": "msg_abc123",
      "role": "user",
      "content": "I'm interested in learning about...",
      "create_time": 1710513797.123
    }
  ]
}
```

**Behavior**:
- Messages displayed in chronological order
- Long conversations (1000+ messages) use pager automatically
- System messages with no content are hidden
- Timestamps shown in UTC

---

### `export`

Export a conversation to a file in various formats.

**Syntax**:
```bash
chatgpt-archive export CONVERSATION_ID --format FORMAT [OPTIONS]
```

**Arguments**:
- `CONVERSATION_ID` (required): The OpenAI conversation ID

**Options**:
- `--format FORMAT` / `-f FORMAT` (required): Output format (`md`, `json`, `yaml`, `html`, `xml`)
- `--output PATH` / `-o PATH`: Output file path (stdout if not specified)

**Exit Codes**:
- `0`: Success
- `1`: Database not found
- `2`: Conversation not found
- `3`: Export failed (invalid format or other error)
- `4`: File write error

**Examples**:
```bash
# Export to Markdown
chatgpt-archive export 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 -f md -o tutorial.md

# Export to JSON (stdout)
chatgpt-archive export 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 -f json > conv.json

# Export to HTML with styling
chatgpt-archive export 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 -f html -o chat.html

# Batch export multiple conversations
for id in $(chatgpt-archive search "python" --json | jq -r '.results[].id'); do
  chatgpt-archive export "$id" -f md -o "exports/${id}.md"
done
```

**Export Formats**:

| Format | Extension | Description | Use Case |
|--------|-----------|-------------|----------|
| `md` | `.md` | Markdown with headers | Human-readable docs, note-taking |
| `json` | `.json` | Structured JSON | Programmatic access, re-import |
| `yaml` | `.yaml` | Human-editable YAML | Configuration, editing |
| `html` | `.html` | Styled HTML page | Browser viewing, sharing |
| `xml` | `.xml` | XML structure | Legacy systems, formal schemas |

**Markdown Example Output**:
```markdown
# Introduction to Neural Networks

**Created**: 2024-03-15 14:23:17  
**Model**: gpt-4  
**Messages**: 12

---

## User (14:23:17)

I'm interested in learning about machine learning...

## Assistant (14:23:22)

Neural networks are a fundamental concept...
```

---

### `list`

List all imported conversations with metadata and pagination.

**Syntax**:
```bash
chatgpt-archive list [OPTIONS]
```

**Options**:
- `--sort FIELD` / `-s FIELD`: Sort by field (`date`, `title`, `messages`) (default: `date`)
- `--order ORDER` / `-o ORDER`: Sort order (`asc`, `desc`) (default: `desc`)
- `--limit N` / `-l N`: Maximum results to return (default: 50)
- `--offset N`: Skip first N results for pagination (default: 0)
- `--json`: Output in JSON format

**Exit Codes**:
- `0`: Success
- `1`: Database not found

**Examples**:
```bash
# List recent conversations
chatgpt-archive list

# List with custom limit
chatgpt-archive list --limit 20

# Sort by title alphabetically
chatgpt-archive list --sort title --order asc

# Sort by message count (most active first)
chatgpt-archive list --sort messages --order desc

# Pagination
chatgpt-archive list --limit 50 --offset 0   # Page 1
chatgpt-archive list --limit 50 --offset 50  # Page 2
chatgpt-archive list --limit 50 --offset 100 # Page 3

# Get all conversation IDs as JSON
chatgpt-archive list --limit 10000 --json | jq -r '.conversations[].id'
```

**Output (Human)**:
```
1,778 conversations

[2024-06-15] Python Async Programming Guide (45 messages)
  ID: 68c2f808-cea0-832a-9bbf-07fe292314c4

[2024-06-10] React Component Optimization (23 messages)
  ID: 68cd640c-c7f8-8332-8083-7fadfd34af16

[2024-06-05] Database Schema Design (31 messages)
  ID: 68e06336-bce4-8330-b350-f7a33ffac85e

(showing 1-50 of 1,778)
```

**Output (JSON)**:
```json
{
  "total": 1778,
  "offset": 0,
  "limit": 50,
  "conversations": [
    {
      "id": "68c2f808-cea0-832a-9bbf-07fe292314c4",
      "title": "Python Async Programming Guide",
      "create_time": 1718462400.0,
      "update_time": 1718465200.0,
      "message_count": 45,
      "model": "gpt-4"
    }
  ]
}
```

**Command Aliases**:
- `ls` → `list`
- `find` → `search`
- `show` → `view`

---

### `embed`

Generate vector embeddings for semantic search (optional feature).

**Syntax**:
```bash
chatgpt-archive embed [OPTIONS]
```

**Prerequisites**:
- Install semantic dependencies: `pip install 'chatgpt-archive[semantic]'`
- Set `OPENAI_API_KEY` environment variable

**Options**:
- `--model MODEL` / `-m MODEL`: Embedding model to use (default: `text-embedding-3-small`)
- `--batch-size N` / `-b N`: Messages per API batch (default: 100)
- `--estimate`: Show cost estimate without generating embeddings
- `--yes` / `-y`: Skip confirmation prompt

**Exit Codes**:
- `0`: Success
- `1`: Database not found or API key missing

**Supported Models**:
- `text-embedding-3-small` (1536 dimensions, $0.02/1M tokens)
- `text-embedding-3-large` (3072 dimensions, $0.13/1M tokens)
- `text-embedding-ada-002` (1536 dimensions, legacy)

**Examples**:
```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Show cost estimate without creating embeddings
chatgpt-archive embed --estimate

# Generate embeddings with confirmation prompt
chatgpt-archive embed

# Skip confirmation
chatgpt-archive embed --yes

# Use larger model for better quality
chatgpt-archive embed --model text-embedding-3-large

# Smaller batch size for rate limit compliance
chatgpt-archive embed --batch-size 50
```

**Output (Estimate)**:
```
Embedding cost estimate:
  Messages to embed: 63,493
  Estimated tokens:  15,873,250
  Model:             text-embedding-3-small
  Estimated cost:    $0.32 - $3.17

Proceed with embedding generation? [y/N]: 
```

**Output (Generation)**:
```
Generating embeddings...
  Embedding: 10,000/63,493 (15.7%) - est. cost: $0.50
  Embedding: 20,000/63,493 (31.5%) - est. cost: $1.00
  ...
  Embedding: 63,493/63,493 (100.0%) - est. cost: $3.17

✓ Embedding complete!
  Embedded:  63,493/63,493 messages
  Remaining: 0
  Tokens:    ~15,873,250
  Cost:      ~$3.17
```

**Behavior**:
- Resumes automatically: Only embeds messages without existing embeddings
- Progress saved: Can interrupt and resume later
- Rate limiting: Respects OpenAI API rate limits
- Enables semantic and hybrid search after completion

---

## Exit Codes

All commands use consistent exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Database not found, invalid archive, or API key missing |
| `2` | Invalid query, malformed JSON, or conversation not found |
| `3` | Operation failed (import, view, export, embed) |
| `4` | File write error (export only) |

**Usage in Scripts**:
```bash
if chatgpt-archive search "python" > results.txt; then
  echo "Search successful"
else
  echo "Search failed with exit code $?"
fi
```

---

## Output Formats

### Human-Readable Output
- Default for terminal usage
- Formatted with visual separators, colors (if terminal supports)
- Progress messages to stderr
- Data to stdout

### JSON Output (`--json`)
- Machine-readable structured data
- All fields have consistent types
- Errors include `status: "error"` and `error` field
- Suitable for scripting with `jq`, Python, etc.

**Example JSON Error**:
```json
{
  "status": "error",
  "error": "database_not_found",
  "message": "Database not found. Run 'chatgpt-archive import' first."
}
```

---

## Advanced Usage

### Working with Multiple Databases

```bash
# Create separate databases for different purposes
chatgpt-archive --db ~/work-chats.db import ~/Downloads/work-export
chatgpt-archive --db ~/personal-chats.db import ~/Downloads/personal-export

# Search specific database
chatgpt-archive --db ~/work-chats.db search "meeting"
```

### Automation & Scripting

```bash
# Export all conversations containing "python"
mkdir -p exports
chatgpt-archive search "python" --json | \
  jq -r '.results[].id' | \
  while read id; do
    chatgpt-archive export "$id" -f md -o "exports/${id}.md"
  done

# Get statistics
echo "Total conversations: $(chatgpt-archive list --json | jq '.total')"
echo "Total with 'error': $(chatgpt-archive search 'error' --json | jq '.total')"
```

### Database Direct Access

The database is standard SQLite and can be queried directly:

```bash
# Open database
sqlite3 ~/.chatgpt-archive/chats.db

# Example queries
SELECT COUNT(*) FROM conversations;
SELECT title, create_time FROM conversations ORDER BY create_time DESC LIMIT 10;
SELECT COUNT(*) FROM messages;
```

**Schema**: See [data-model.md](../specs/001-archive-search-export/data-model.md) for full schema reference.

### Performance Tips

1. **Import**: Import is I/O bound. Use SSD for best performance.
2. **Search**: FTS5 is very fast. Keyword search typically <500ms even for 64K+ messages.
3. **Semantic Search**: Vector search is slower (~2-5s) but finds conceptually related content.
4. **Hybrid Search**: Combines both - use when you want comprehensive results.
5. **Database Size**: Typically 1.5-2x the original JSON size. Uses WAL mode for better concurrent reads.

### Environment Variables Reference

| Variable | Purpose | Default |
|----------|---------|---------|
| `CHATGPT_ARCHIVE_DB` | Override database location | `~/.chatgpt-archive/chats.db` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | (none) |

---

## Command Aliases

The following command aliases are supported for convenience:

| Alias | Command | Example |
|-------|---------|----------|
| `ls` | `list` | `chatgpt-archive ls` |
| `find` | `search` | `chatgpt-archive find "python"` |
| `show` | `view` | `chatgpt-archive show <id>` |

---

## See Also

- [User Guide Index](README.md) - User documentation home
- [Root README](../../README.md) - Quick start and developer overview
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Python API](../API.md) - Programmatic usage via Python API
- [Contributing](../../CONTRIBUTING.md) - Development guide
