# ChatGPT Archive - API Documentation

Documentation for using ChatGPT Archive as a Python library.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Database Module](#database-module)
- [Importer Module](#importer-module)
- [Media Helpers](#media-helpers)
- [Search Module](#search-module)
- [Embeddings Module](#embeddings-module)
- [Exporters Module](#exporters-module)
- [Models](#models)
- [Examples](#examples)

---

## Overview

While ChatGPT Archive is primarily a CLI tool, all functionality is available as a Python API for programmatic access.

**Use cases**:
- Build custom applications on top of your ChatGPT archive
- Integrate with existing Python projects
- Create automated workflows
- Build web interfaces or APIs
- Custom analysis and reporting

---

## Installation

```bash
# Install from source
pip install -e .

# Or with semantic search support
pip install -e ".[semantic]"
```

---

## Database Module

`chatgpt_archive.db` - Database connection and schema management.

### Functions

#### `get_db_path() -> Path`

Get the database path from environment or use default.

**Returns**: Path to the database file

**Example**:
```python
from chatgpt_archive.db import get_db_path

db_path = get_db_path()
print(f"Database: {db_path}")
# Output: Database: ~/.chatgpt-archive/chats.db
```

#### `get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection`

Get a database connection with proper settings (foreign keys enabled, WAL mode).

**Args**:
- `db_path`: Optional path to database file. If None, uses default.

**Returns**: SQLite connection with Row factory

**Example**:
```python
from chatgpt_archive.db import get_connection

conn = get_connection()
try:
    # Use connection...
    cursor = conn.execute("SELECT COUNT(*) FROM conversations")
    count = cursor.fetchone()[0]
    print(f"Conversations: {count}")
finally:
    conn.close()
```

#### `init_db(db_path: Optional[Path] = None) -> sqlite3.Connection`

Initialize database with schema (creates tables, indexes, FTS5).

**Args**:
- `db_path`: Optional path to database file

**Returns**: Initialized database connection

**Example**:
```python
from pathlib import Path
from chatgpt_archive.db import init_db

# Create new database
db_path = Path("./my-archive.db")
conn = init_db(db_path)
conn.close()
```

#### `get_conversation_by_id(conn: sqlite3.Connection, openai_id: str) -> Optional[sqlite3.Row]`

Retrieve a conversation by its OpenAI ID.

**Args**:
- `conn`: Database connection
- `openai_id`: The OpenAI conversation ID (UUID)

**Returns**: Row with conversation data, or None if not found

**Example**:
```python
from chatgpt_archive.db import get_connection, get_conversation_by_id

conn = get_connection()
conv = get_conversation_by_id(conn, "6974cc29-45d8-8327-a6dc-ef1ef0a82f46")

if conv:
    print(f"Title: {conv['title']}")
    print(f"Messages: {conv['message_count']}")
    print(f"Model: {conv['model_slug']}")

conn.close()
```

#### `get_conversation_messages(conn: sqlite3.Connection, conversation_db_id: int, include_hidden: bool = False) -> list`

Retrieve all messages for a conversation in chronological order.

**Args**:
- `conn`: Database connection
- `conversation_db_id`: Internal database ID of the conversation
- `include_hidden`: Whether to include hidden system messages

**Returns**: List of Row objects with message data

**Example**:
```python
from chatgpt_archive.db import get_connection, get_conversation_by_id, get_conversation_messages

conn = get_connection()
conv = get_conversation_by_id(conn, "6974cc29-45d8-8327-a6dc-ef1ef0a82f46")

if conv:
    messages = get_conversation_messages(conn, conv['id'])
    
    for msg in messages:
        print(f"{msg['author_role']}: {msg['content'][:50]}...")

conn.close()
```

#### `list_conversations(conn: sqlite3.Connection, sort_by: str = "date", order: str = "desc", limit: int = 50, offset: int = 0) -> tuple`

List conversations with message counts and pagination.

**Args**:
- `conn`: Database connection
- `sort_by`: Field to sort by: 'date', 'title', 'messages'
- `order`: Sort order: 'asc' or 'desc'
- `limit`: Maximum number of results
- `offset`: Number of results to skip (pagination)

**Returns**: Tuple of (conversations list, total count)

**Example**:
```python
from chatgpt_archive.db import get_connection, list_conversations

conn = get_connection()
conversations, total = list_conversations(conn, sort_by="messages", order="desc", limit=10)

print(f"Top 10 conversations (out of {total}):")
for conv in conversations:
    print(f"  {conv['title']} - {conv['message_count']} messages")

conn.close()
```

---

## Importer Module

`chatgpt_archive.importer` - Import ChatGPT export archives.

### Functions

#### `import_archive(archive_path: Path, db_path: Path, progress_callback: Optional[Callable] = None) -> tuple`

Import a ChatGPT export archive into the database.

**Args**:
- `archive_path`: Path to extracted ChatGPT export directory
- `db_path`: Path to database file (created if doesn't exist)
- `progress_callback`: Optional callback function called with (current, total) on progress

**Returns**: Tuple of (conversations_imported, messages_imported)

**Raises**:
- `InvalidArchiveError`: Archive directory missing or invalid
- `InvalidJSONError`: conversations.json is malformed
- `Exception`: Other import errors

**Example**:
```python
from pathlib import Path
from chatgpt_archive.importer import import_archive

archive_path = Path("~/Downloads/chatgpt-export").expanduser()
db_path = Path("~/.chatgpt-archive/chats.db").expanduser()

def progress(current, total):
    print(f"Progress: {current}/{total}")

try:
    convs, msgs = import_archive(archive_path, db_path, progress)
    print(f"Imported {convs} conversations, {msgs} messages")
except Exception as e:
    print(f"Import failed: {e}")
```

### Exceptions

- `InvalidArchiveError`: Raised when archive directory is invalid
- `InvalidJSONError`: Raised when conversations.json is malformed

---

## Media Helpers

`api.services.media_service` provides the runtime helpers used by the API to resolve inline archive attachments.

### `get_archive_media_dir(settings: dict[str, Any] | None = None) -> Path`

Returns the directory used to resolve inline media files. Resolution order is:

1. `CHATGPT_ARCHIVE_DIR`
2. persisted `archive_media_dir` setting
3. `<db parent>/media`

### `persist_archive_media(source_dir: Path, destination_dir: Path | None = None) -> Path`

Copies extracted archive files into the permanent media directory used by the API and web UI.

### `resolve_message_content(content: str | None, conversation_id: str) -> tuple[str | None, list[Attachment]]`

Strips asset pointer dicts from stored message content, replaces them with ordering tokens, and returns resolved runtime `Attachment` objects for the API response.

### `api.services.formatting_service.build_render_segments(content: str | None, attachments: list[Attachment]) -> list[RenderSegment]`

Builds the ordered render contract consumed by the web transcript UI. The function emits:

- `markdown` segments for prose and markdown blocks
- `attachment` segments referencing `attachments[]` by index
- `fallback` segments for unsupported or malformed structured payloads

The segment list preserves reading order and treats raw HTML as inert text.

---

## Search Module

`chatgpt_archive.search` - Full-text and semantic search.

### Functions

#### `execute_search(conn: sqlite3.Connection, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None, limit: int = 20) -> list`

Execute a full-text search query using FTS5.

**Args**:
- `conn`: Database connection
- `query`: Search query (supports FTS5 syntax)
- `from_date`: Filter conversations after this date (YYYY-MM-DD)
- `to_date`: Filter conversations before this date (YYYY-MM-DD)
- `limit`: Maximum results to return

**Returns**: List of search result dictionaries

**Raises**:
- `InvalidQueryError`: Query syntax is invalid

**Example**:
```python
from chatgpt_archive.db import get_connection
from chatgpt_archive.search import execute_search

conn = get_connection()

try:
    results = execute_search(
        conn, 
        "python AND flask",
        from_date="2024-01-01",
        limit=10
    )
    
    for result in results:
        print(f"{result['title']} - {result['match_count']} matches")
        print(f"  {result['snippet']}")
        
except InvalidQueryError as e:
    print(f"Invalid query: {e}")
finally:
    conn.close()
```

#### `execute_semantic_search(conn: sqlite3.Connection, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None, limit: int = 20) -> list`

Execute a semantic search using vector embeddings.

**Requires**: Embeddings must be generated first (see Embeddings Module)

**Args**: Same as `execute_search`

**Returns**: List of search result dictionaries with similarity scores

**Example**:
```python
from chatgpt_archive.db import get_connection
from chatgpt_archive.search import execute_semantic_search

conn = get_connection()

results = execute_semantic_search(conn, "machine learning concepts", limit=5)

for result in results:
    print(f"{result['title']} - similarity: {result.get('score', 0):.3f}")

conn.close()
```

#### `execute_hybrid_search(conn: sqlite3.Connection, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None, limit: int = 20) -> list`

Execute hybrid search combining keyword (FTS5) and semantic (vector) search.

**Args**: Same as `execute_search`

**Returns**: Combined and ranked results from both search methods

#### `format_results_human(results: list) -> str`

Format search results as human-readable text.

#### `format_results_json(results: list) -> dict`

Format search results as JSON structure.

---

## Embeddings Module

`chatgpt_archive.embeddings` - Vector embeddings for semantic search (optional).

### Functions

#### `embed_messages(conn: sqlite3.Connection, model: str = "text-embedding-3-small", batch_size: int = 100, progress_callback: Optional[Callable] = None) -> EmbeddingProgress`

Generate embeddings for all messages without existing embeddings.

**Requires**: 
- `pip install 'chatgpt-archive[semantic]'`
- `OPENAI_API_KEY` environment variable

**Args**:
- `conn`: Database connection
- `model`: OpenAI embedding model to use
- `batch_size`: Messages per API batch
- `progress_callback`: Optional callback with EmbeddingProgress object

**Returns**: EmbeddingProgress object with statistics

**Example**:
```python
import os
from chatgpt_archive.db import get_connection
from chatgpt_archive.embeddings import embed_messages

os.environ["OPENAI_API_KEY"] = "sk-..."

conn = get_connection()

def progress(p):
    print(f"Progress: {p.percent_complete}% - ${p.estimated_cost:.4f}")

result = embed_messages(conn, progress_callback=progress)

print(f"Embedded {result.completed} messages")
print(f"Cost: ${result.estimated_cost:.2f}")

conn.close()
```

#### `estimate_cost(conn: sqlite3.Connection, model: str = "text-embedding-3-small") -> dict`

Estimate the cost of generating embeddings for all unembed messages.

**Returns**: Dictionary with cost estimation details

**Example**:
```python
from chatgpt_archive.db import get_connection
from chatgpt_archive.embeddings import estimate_cost

conn = get_connection()
estimate = estimate_cost(conn)

print(f"Messages to embed: {estimate['messages_to_embed']}")
print(f"Estimated cost: {estimate['estimated_cost_display']}")

conn.close()
```

### Classes

#### `EmbeddingProgress`

Dataclass containing embedding progress statistics.

**Attributes**:
- `total`: Total messages to embed
- `completed`: Messages embedded so far
- `remaining`: Messages left to embed
- `percent_complete`: Percentage complete
- `tokens_used`: Estimated tokens used
- `estimated_cost`: Estimated cost in USD
- `model`: Embedding model name

---

## Exporters Module

`chatgpt_archive.exporters` - Export conversations to various formats.

### Functions

#### `get_exporter(format: str) -> Optional[BaseExporter]`

Get exporter instance for the specified format.

**Args**:
- `format`: Export format ('md', 'json', 'yaml', 'html', 'xml')

**Returns**: Exporter instance, or None if format invalid

**Example**:
```python
from chatgpt_archive.exporters import get_exporter
from chatgpt_archive.db import get_connection, get_conversation_by_id, get_conversation_messages

conn = get_connection()

# Get conversation
conv = get_conversation_by_id(conn, "6974cc29-45d8-8327-a6dc-ef1ef0a82f46")
messages = get_conversation_messages(conn, conv['id'])

# Prepare data
conv_dict = {
    "id": conv["openai_id"],
    "title": conv["title"],
    "create_time": conv["create_time"],
    "update_time": conv["update_time"],
    "model": conv["model_slug"],
    "message_count": conv["message_count"],
}

messages_list = [
    {
        "id": msg["openai_id"],
        "role": msg["author_role"],
        "content": msg["content"],
        "create_time": msg["create_time"],
    }
    for msg in messages
]

# Export to Markdown
exporter = get_exporter("md")
markdown = exporter.export(conv_dict, messages_list)

with open("conversation.md", "w") as f:
    f.write(markdown)

conn.close()
```

### Base Class

#### `BaseExporter`

Abstract base class for all exporters.

**Methods**:
- `export(conversation: dict, messages: list) -> str`: Export conversation to string

**Subclasses**:
- `MarkdownExporter`: Export to Markdown
- `JSONExporter`: Export to JSON
- `YAMLExporter`: Export to YAML
- `HTMLExporter`: Export to HTML with styling
- `XMLExporter`: Export to XML

---

## Models

`chatgpt_archive.models` - Data models (dataclasses).

### Classes

#### `Conversation`

Dataclass representing a conversation.

**Attributes**:
- `openai_id`: str - OpenAI conversation ID
- `title`: Optional[str] - Conversation title
- `create_time`: Optional[float] - Creation timestamp
- `update_time`: Optional[float] - Last update timestamp
- `model_slug`: Optional[str] - Model used (e.g., "gpt-4")
- `is_archived`: bool - Whether conversation is archived

#### `Message`

Dataclass representing a message.

**Attributes**:
- `openai_id`: str - OpenAI message ID
- `conversation_id`: int - Foreign key to conversation
- `parent_id`: Optional[str] - Parent message ID (tree structure)
- `author_role`: str - Role: 'user', 'assistant', 'system', 'tool'
- `content`: Optional[str] - Message content
- `content_type`: str - Content type (default: 'text')
- `create_time`: Optional[float] - Creation timestamp
- `weight`: float - Message weight (default: 1.0)
- `is_hidden`: bool - Whether message is hidden

#### `Attachment`

Dataclass representing a file attachment.

**Attributes**:
- `message_id`: int - Foreign key to message
- `file_path`: str - Path to attachment file
- `file_type`: Optional[str] - MIME type
- `original_name`: Optional[str] - Original filename

---

## Examples

### Complete Import and Search Workflow

```python
from pathlib import Path
from chatgpt_archive.db import get_connection, init_db
from chatgpt_archive.importer import import_archive
from chatgpt_archive.search import execute_search

# 1. Initialize database
db_path = Path("./my-chats.db")
conn = init_db(db_path)
conn.close()

# 2. Import archive
archive_path = Path("~/Downloads/chatgpt-export").expanduser()

def progress(current, total):
    if current % 100 == 0:
        print(f"Importing: {current}/{total}")

convs, msgs = import_archive(archive_path, db_path, progress)
print(f"\nImported {convs} conversations, {msgs} messages")

# 3. Search
conn = get_connection(db_path)
results = execute_search(conn, "python tutorial", limit=5)

for result in results:
    print(f"\n{result['title']}")
    print(f"  ID: {result['id']}")
    print(f"  Matches: {result['match_count']}")
    print(f"  {result['snippet']}")

conn.close()
```

### Custom Analysis

```python
from chatgpt_archive.db import get_connection
import sqlite3

conn = get_connection()

# Get conversation statistics
stats = conn.execute("""
    SELECT 
        COUNT(DISTINCT c.id) as total_conversations,
        COUNT(m.id) as total_messages,
        AVG(msg_count) as avg_messages_per_conversation,
        MAX(msg_count) as max_messages
    FROM conversations c
    LEFT JOIN (
        SELECT conversation_id, COUNT(*) as msg_count
        FROM messages
        GROUP BY conversation_id
    ) msg_counts ON c.id = msg_counts.conversation_id
    LEFT JOIN messages m ON c.id = m.conversation_id
""").fetchone()

print(f"Total conversations: {stats['total_conversations']}")
print(f"Total messages: {stats['total_messages']}")
print(f"Average messages per conversation: {stats['avg_messages_per_conversation']:.1f}")
print(f"Longest conversation: {stats['max_messages']} messages")

# Find most common topics
topics = conn.execute("""
    SELECT title, message_count
    FROM (
        SELECT c.id, c.title, COUNT(m.id) as message_count
        FROM conversations c
        JOIN messages m ON c.id = m.conversation_id
        WHERE c.title IS NOT NULL
        GROUP BY c.id
    )
    ORDER BY message_count DESC
    LIMIT 10
""").fetchall()

print("\nMost active conversations:")
for topic in topics:
    print(f"  {topic['title']}: {topic['message_count']} messages")

conn.close()
```

### Build a Custom Exporter

```python
from chatgpt_archive.exporters.base import BaseExporter
from typing import Dict, List

class PlainTextExporter(BaseExporter):
    """Export conversations to plain text format."""
    
    def export(self, conversation: Dict, messages: List[Dict]) -> str:
        """Export to plain text.
        
        Args:
            conversation: Conversation metadata
            messages: List of message dicts
            
        Returns:
            Plain text formatted string
        """
        lines = []
        
        # Header
        lines.append(f"Conversation: {conversation['title']}")
        lines.append(f"Created: {conversation.get('create_time', 'Unknown')}")
        lines.append(f"Messages: {len(messages)}")
        lines.append("=" * 60)
        lines.append("")
        
        # Messages
        for msg in messages:
            role = msg['role'].upper()
            content = msg.get('content', '').strip()
            
            if content:
                lines.append(f"[{role}]")
                lines.append(content)
                lines.append("")
        
        return "\n".join(lines)

# Usage
from chatgpt_archive.db import get_connection, get_conversation_by_id, get_conversation_messages

conn = get_connection()
conv = get_conversation_by_id(conn, "some-id")
messages = get_conversation_messages(conn, conv['id'])

conv_dict = dict(conv)
messages_list = [dict(msg) for msg in messages]

exporter = PlainTextExporter()
text = exporter.export(conv_dict, messages_list)

with open("conversation.txt", "w") as f:
    f.write(text)

conn.close()
```

### Web API Example (Flask)

```python
from flask import Flask, jsonify, request
from chatgpt_archive.db import get_connection, list_conversations
from chatgpt_archive.search import execute_search

app = Flask(__name__)

@app.route('/api/conversations')
def get_conversations():
    """List conversations with pagination."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    conn = get_connection()
    conversations, total = list_conversations(conn, limit=limit, offset=offset)
    conn.close()
    
    return jsonify({
        'total': total,
        'offset': offset,
        'limit': limit,
        'conversations': [dict(c) for c in conversations]
    })

@app.route('/api/search')
def search_conversations():
    """Search conversations."""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    conn = get_connection()
    results = execute_search(conn, query, limit=limit)
    conn.close()
    
    return jsonify({
        'query': query,
        'total': len(results),
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

## See Also

- [README.md](../README.md) - Quick start and overview
- [CLI Reference](user-guide/usage.md) - CLI command reference
- [Contributing](../CONTRIBUTING.md) - Development guide
- [Database Schema](../specs/001-archive-search-export/data-model.md) - Full schema documentation
