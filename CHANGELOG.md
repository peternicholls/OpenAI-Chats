# Changelog

All notable changes to the ChatGPT Archive project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes
- **Python 3.10+ required for CLI/library**: The minimum Python version for the ChatGPT Archive CLI and core library has been raised from 3.8 to 3.10. Users on Python 3.8 or 3.9 must upgrade before installing this version. The API backend and API Docker image continue to require Python 3.11+.

### Added
- **Web UI Test Suite**: Comprehensive testing infrastructure for the web UI feature
  - API integration tests (62 tests) covering all endpoints
  - Frontend unit tests (55 tests) with vitest and testing-library
  - E2E tests (27 tests) with Playwright
  - MSW mocking for API requests
  - Test utilities and fixtures

### Work in Progress
- Documentation improvements and polish

## [0.1.0] - 2026-02-12

### Added

#### Core Features
- **Import**: Import ChatGPT export archives into SQLite database
  - Idempotent imports (safe to re-import same archive)
  - Automatic title fallback (uses first user message or "[Untitled]")
  - Attachment detection and storage
  - Progress tracking with callbacks
  - JSON and human-readable output formats
  
- **Search**: Full-text search across all conversations
  - FTS5-powered keyword search with BM25 ranking
  - Advanced query syntax (AND, OR, NOT, phrases, proximity)
  - Date range filtering (--from, --to)
  - Configurable result limits
  - Snippet generation with match highlighting
  - JSON output for scripting
  
- **Semantic Search**: AI-powered semantic search (optional)
  - Vector embeddings using OpenAI API
  - Support for text-embedding-3-small and text-embedding-3-large
  - Hybrid search combining keyword and semantic approaches
  - Resumable embedding generation
  - Cost estimation before generation
  - Progressive embedding during import (optional)
  
- **View**: Display full conversations in terminal
  - Chronological message ordering
  - Automatic pagination for long conversations (1000+ messages)
  - JSON output support
  - Hidden system message filtering
  - Readable formatting with role labels and timestamps
  
- **Export**: Export conversations to multiple formats
  - Markdown (.md) - Human-readable documentation
  - JSON (.json) - Structured data for programmatic access
  - YAML (.yaml) - Human-editable structured format
  - HTML (.html) - Styled web pages for browser viewing
  - XML (.xml) - Formal schema for legacy systems
  - Stdout or file output
  - Batch export support via scripting
  
- **List**: Browse all imported conversations
  - Sort by date, title, or message count
  - Ascending/descending order
  - Pagination with offset/limit
  - Message count per conversation
  - JSON output for scripting

#### Database
- SQLite-based storage with FTS5 full-text search
- WAL mode for better concurrent read performance
- Automatic schema creation with triggers
- Foreign key constraints
- Optimized indexes for common queries
- Support for custom database locations via --db flag or environment variable
- Path expansion (~/ support)

#### CLI Features
- Global --db flag for custom database locations
- Global --json flag for machine-readable output
- CHATGPT_ARCHIVE_DB environment variable support
- --version flag
- Comprehensive help text for all commands
- Command aliases (ls → list, find → search, show → view)
- Proper exit codes for scripting
- All errors to stderr, data to stdout

#### Documentation
- Comprehensive README with quick start and examples
- Detailed USAGE.md with all commands and options
- TROUBLESHOOTING.md with common issues and solutions
- CONTRIBUTING.md with development setup guide
- API.md for programmatic usage
- Inline help for all commands
- Example scripts and use cases

#### Developer Features
- Type hints throughout codebase
- Modular architecture (db, importer, search, exporters)
- Extensible exporter system
- Test suite with pytest
- Development dependencies (black, ruff, mypy)
- Editable install support

### Technical Details

#### Database Schema
- `conversations` table with metadata and FTS5 integration
- `messages` table with tree structure support
- `attachments` table for file references
- `messages_fts` virtual table for full-text search
- `message_embeddings` table for semantic search (optional)
- Automatic FTS5 index updates via triggers

#### Performance Characteristics
- Import: ~60 seconds for 64,000 messages (SSD)
- Keyword search: <500ms typical
- Semantic search: 2-5 seconds typical
- Database size: 1.5-2x original JSON size
- Embedding generation: ~$2-5 for 64,000 messages (one-time)

#### Supported Formats
- **Input**: ChatGPT export archives (conversations.json)
- **Export**: Markdown, JSON, YAML, HTML, XML
- **Search**: FTS5 query syntax, natural language (semantic)
- **Database**: SQLite 3.x with FTS5 and optional sqlite-vec

### Dependencies
- **Required**: 
  - Python 3.10+
  - click (CLI framework)
  - pyyaml (YAML export support)
  
- **Optional (semantic search)**:
  - openai (OpenAI API client)
  - numpy (numerical operations)
  - sqlite-vec (vector similarity search)

### Installation
```bash
# Basic installation
pip install -e .

# With semantic search
pip install -e ".[semantic]"

# Development mode
pip install -e ".[dev,semantic]"
```

### Known Limitations
- Import only supports ChatGPT official export format
- Semantic search requires OpenAI API key and costs money
- Very long conversations (10,000+ messages) may be slow to view
- Export does not preserve code block syntax highlighting
- No built-in conversation editing or deletion (use SQL directly)

### Breaking Changes
None - this is the initial release.

---

## Version History

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **Major** (X.0.0): Breaking changes to CLI, API, or database schema
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, no new features

### Planned Features (Future Releases)

See GitHub Issues for planned enhancements:
- [ ] Conversation tagging system
- [ ] Delete/edit conversations via CLI
- [ ] CSV and Excel export formats
- [ ] Web interface with Flask
- [ ] Docker deployment
- [ ] Incremental import (only new conversations)
- [ ] Conversation statistics and charts
- [ ] Multi-database support
- [ ] Attachment file export

---

## Migration Guide

### From Direct SQL to CLI

If you were previously querying the database directly with SQL, the CLI provides easier access:

**Before**:
```bash
sqlite3 ~/.chatgpt-archive/chats.db \
  "SELECT * FROM messages_fts WHERE content MATCH 'python'"
```

**After**:
```bash
chatgpt-archive search "python"
```

### Database Schema Changes

None yet - this is the initial release.

Future schema changes will be documented here with migration SQL scripts.

---

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for the CLI framework
- Uses [SQLite FTS5](https://www.sqlite.org/fts5.html) for full-text search
- Optional semantic search powered by [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- Vector search via [sqlite-vec](https://github.com/asg017/sqlite-vec)
- Inspired by the need to search and preserve ChatGPT conversation history

---

## See Also

- [README.md](README.md) - Project overview and quick start
- [USAGE.md](docs/USAGE.md) - Complete command reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
- [API.md](docs/API.md) - Python API documentation
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues

---

## Links

- **Repository**: https://github.com/peternicholls/OpenAI-Chats
- **Issues**: https://github.com/peternicholls/OpenAI-Chats/issues
- **Releases**: https://github.com/peternicholls/OpenAI-Chats/releases
