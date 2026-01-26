# Research: ChatGPT Archive Search & Export

**Feature**: 001-archive-search-export | **Date**: 2026-01-26

## Research Tasks Completed

### 1. OpenAI Export Format Structure

**Decision**: Parse `conversations.json` as array of conversation objects with nested message tree

**Rationale**: Analysis of actual export (251MB, 1,778 conversations) revealed:
- Top-level keys: `title`, `create_time`, `update_time`, `mapping`, `conversation_id`, `id`, `default_model_slug`
- `mapping` is a dict of message nodes forming a tree (parent/children references)
- Each node: `{id, message, parent, children}`
- Message structure: `{id, author.role, content.content_type, content.parts[], create_time, status, metadata}`
- `author.role` values: "user", "assistant", "system"
- `content.parts[0]` contains actual text content

**Alternatives considered**: 
- Streaming JSON parser (rejected: adds complexity, file fits in memory)
- Custom format detection (rejected: OpenAI format is stable)

---

### 2. Full-Text Search Technology

**Decision**: SQLite FTS5 with porter tokenizer and unicode61

**Rationale**:
- Built into SQLite (no additional dependencies)
- FTS5 is the latest and most performant FTS module
- `porter` stemming improves search relevance (finds "running" when searching "run")
- `unicode61` handles international characters properly
- `bm25()` function provides relevance ranking
- `snippet()` and `highlight()` generate search result previews

**Implementation**:
```sql
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    tokenize='porter unicode61'
);

-- Search with relevance ranking
SELECT conversation_id, snippet(messages_fts, 0, '<b>', '</b>', '...', 50) 
FROM messages_fts 
WHERE messages_fts MATCH ?
ORDER BY bm25(messages_fts);
```

**Alternatives considered**:
- Whoosh (rejected: additional dependency, slower for this scale)
- Elasticsearch (rejected: requires server, violates Constitution V)
- LIKE queries (rejected: too slow for 250MB+ content)

---

### 3. CLI Framework

**Decision**: Click with command groups

**Rationale**:
- Industry standard for Python CLIs
- Clean decorator-based API
- Built-in support for subcommands via `@click.group()`
- Handles argument parsing, help generation, exit codes
- Easy testing with `CliRunner`

**Implementation**:
```python
@click.group()
def cli():
    """ChatGPT Archive Search & Export tool."""
    pass

@cli.command()
@click.argument('archive_dir', type=click.Path(exists=True))
@click.option('--db', default='~/.chatgpt-archive/chats.db')
def import_(archive_dir, db):
    """Import conversations from ChatGPT export."""
    ...
```

**Alternatives considered**:
- argparse (rejected: more verbose, less elegant subcommand support)
- typer (rejected: additional dependency for similar functionality)
- fire (rejected: less control over CLI design)

---

### 4. Database Schema Design

**Decision**: Normalized schema with separate tables for conversations and messages

**Rationale**:
- Preserves original OpenAI IDs as unique identifiers
- Foreign key constraints ensure data integrity
- Separate FTS5 table for efficient full-text search
- Supports tree structure via parent_id for message branching

**Alternatives considered**:
- Single denormalized table (rejected: redundant data, harder to maintain)
- Document store/JSON column (rejected: slower search, SQLite FTS5 is faster)
- Separate files per conversation (rejected: harder to search across)

---

### 5. Export Format Implementation

**Decision**: Separate exporter module per format with common base class

**Rationale**:
- Each format has unique requirements (escaping, structure)
- Easy to add new formats without modifying existing code
- Common interface allows format selection via CLI flag
- Uses stdlib for JSON and XML; only pyyaml is external dependency

**Formats**:
| Format | Library | Output Structure |
|--------|---------|------------------|
| Markdown | stdlib (string formatting) | Human-readable conversation |
| JSON | json (stdlib) | Structured, re-importable |
| YAML | pyyaml | Structured, human-editable |
| HTML | stdlib (string formatting) | Browser-viewable with CSS |
| XML | xml.etree (stdlib) | Legacy integration |

**Alternatives considered**:
- Jinja2 templates (rejected: overkill for simple formats)
- Single exporter with format switch (rejected: becomes unwieldy)

---

## Unresolved Questions

None - all technical decisions made.

## Dependencies Confirmed

| Package | Version | Purpose |
|---------|---------|---------|
| click | ≥8.0 | CLI framework |
| pyyaml | ≥6.0 | YAML export |
| pytest | ≥7.0 | Testing (dev) |
| pytest-cov | ≥4.0 | Coverage (dev) |

All other functionality uses Python stdlib (sqlite3, json, xml.etree).
