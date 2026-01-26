# Quickstart: ChatGPT Archive Search & Export

Get up and running in 5 minutes.

## Prerequisites

- Python 3.8 or later
- A ChatGPT data export (download from [chat.openai.com/settings](https://chat.openai.com/settings) → Data Controls → Export)

## Installation

```bash
# Clone and install
git clone <repository-url>
cd OpenAI-Chats
pip install -e .

# Or install from PyPI (when published)
pip install chatgpt-archive
```

## Quick Start

### 1. Import Your Archive

Extract your ChatGPT export ZIP file, then import:

```bash
chatgpt-archive import ./path/to/extracted/export/
```

Output:
```
Importing from ./path/to/extracted/export/...
Found 1,778 conversations
Imported: 1,778 conversations, 45,231 messages
Database: ~/.chatgpt-archive/chats.db (156 MB)
```

### 2. Search Your Conversations

```bash
# Simple keyword search
chatgpt-archive search "machine learning"

# Search with date filter
chatgpt-archive search "python" --from 2024-01-01 --to 2024-06-30

# Get JSON output for scripting
chatgpt-archive search "API design" --json
```

### 3. List All Conversations

```bash
# List recent conversations
chatgpt-archive list

# Sort by title
chatgpt-archive list --sort title

# Get more results
chatgpt-archive list --limit 100
```

### 4. View a Conversation

```bash
# Use the conversation ID from search or list
chatgpt-archive view 6974cc29-45d8-8327-a6dc-ef1ef0a82f46
```

### 5. Export a Conversation

```bash
# Export to Markdown
chatgpt-archive export abc123 -f md -o conversation.md

# Export to HTML (viewable in browser)
chatgpt-archive export abc123 -f html -o conversation.html

# Export to JSON (for processing)
chatgpt-archive export abc123 -f json -o conversation.json

# Export to YAML
chatgpt-archive export abc123 -f yaml -o conversation.yaml

# Export to XML
chatgpt-archive export abc123 -f xml -o conversation.xml
```

## Common Workflows

### Find and Export a Specific Chat

```bash
# 1. Search for the conversation
chatgpt-archive search "project proposal"

# 2. Copy the ID from the results
# 3. Export it
chatgpt-archive export 6974cc29-45d8-8327-a6dc-ef1ef0a82f46 -f md -o proposal-chat.md
```

### Batch Export All Conversations (Advanced)

```bash
# Export all conversation IDs
chatgpt-archive list --json | jq -r '.conversations[].id' > ids.txt

# Export each as markdown
while read id; do
  chatgpt-archive export "$id" -f md -o "exports/${id}.md"
done < ids.txt
```

### Re-import After New Export

The import is idempotent—just run it again:

```bash
chatgpt-archive import ./new-export-2024-03/
```

Existing conversations are updated; new ones are added; nothing is duplicated.

## Configuration

### Custom Database Location

```bash
# Use environment variable
export CHATGPT_ARCHIVE_DB=/path/to/my/chats.db
chatgpt-archive search "hello"

# Or use --db flag
chatgpt-archive search "hello" --db /path/to/my/chats.db
```

## Troubleshooting

### "Database not found"

Run `chatgpt-archive import` first to create the database.

### "No conversations found"

Check that your archive directory contains `conversations.json`.

### Search is slow

This shouldn't happen with FTS5. If it does, try re-importing:
```bash
rm ~/.chatgpt-archive/chats.db
chatgpt-archive import ./export/
```

## Getting Help

```bash
# General help
chatgpt-archive --help

# Command-specific help
chatgpt-archive search --help
chatgpt-archive export --help
```
