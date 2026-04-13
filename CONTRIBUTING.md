# Contributing to OpenAI-Chats

Thank you for your interest in contributing! This guide will help you get started with development.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Adding Features](#adding-features)
- [Reporting Issues](#reporting-issues)

---

## Development Setup

### Prerequisites

- Python 3.11+ for API and full-stack work
- Python 3.10+ for CLI-only work
- Node.js 20+ and npm for frontend development
- Docker 24+ with Compose v2 for containerized validation
- pip and virtualenv (or similar)
- Git
- SQLite 3.x (usually pre-installed on macOS/Linux)

### Clone and Install

```bash
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev,excel]"
(cd api && pip install -e ".[dev]")

cd web
npm ci
cd ..

# Optional semantic search support
pip install -e ".[semantic]"
```

### Development Dependencies

The main tooling used in active development is:

- `pytest` for core and API testing
- `ruff` and `black` for Python linting and formatting
- `Vitest`, Testing Library, and Playwright for frontend testing
- `Next.js`, `React Query`, and the shared frontend API client for browser flows
- `sqlite-vec`, `openai`, and related extras only when semantic search work is in scope

---

## Project Structure

```
OpenAI-Chats/
├── chatgpt_archive/        # Core library, CLI, DB layer, import/search/export logic
├── api/                    # FastAPI app, routers, middleware, backend services, API tests
├── web/                    # Next.js frontend, TypeScript source, web tests
├── tests/                  # Core package tests, unit tests, integration tests
├── docs/                   # User guide plus Python and REST API docs
├── specs/                  # Feature specs, plans, contracts, and task artifacts
├── docker/                 # Dockerfiles and nginx config
├── docker-compose.yml      # Local multi-service stack
├── .github/copilot-instructions.md
├── .specify/memory/constitution.md
└── CONTRIBUTING.md
```

---

## Development Workflow

### 1. Read the Rules First

Before changing code, read:

- `.github/copilot-instructions.md` for repository workflow, architecture, and validation rules
- `.specify/memory/constitution.md` for the non-negotiable governance rules
- The current branch name and any matching `specs/NNN-*` directory for scope and terminology

### 2. Create or Use the Right Branch

```bash
# Example feature branch aligned with a spec
git checkout -b 004-frontend-formatting

# Or a focused bug-fix branch
git checkout -b fix/issue-123
```

If a numbered spec already exists, prefer a branch name that matches it.

### 3. Make Changes

Follow existing code patterns and conventions. Key principles:

- **Keep it simple**: Prefer clarity over cleverness
- **Use TDD by default**: Start with the smallest failing automated test for behavior changes, then implement, then refactor
- **Type hints**: Use type hints for function parameters and returns
- **Docstrings**: Add Google-style docstrings for public functions
- **Error handling**: Use descriptive error messages
- **Testing**: Add or update regression coverage for new features and bug fixes
- **Respect layer boundaries**: Keep shared logic in `chatgpt_archive/`, keep `api/` thin, and use the shared frontend client in `web/`

Additional repository rules:

- Extend `chatgpt_archive/` before creating duplicate business logic elsewhere
- Keep internal SQLite IDs separate from public OpenAI IDs
- Update the full transcript rendering pipeline together when rendering behavior changes: backend formatter, API response models, and frontend rendering
- Use shared frontend API services and React Query hooks instead of ad hoc `fetch` calls
- Prefer the smallest viable change over speculative abstractions or broad rewrites

### 4. Validate the Smallest Affected Surface

```bash
# Core library tests
source .venv/bin/activate && pytest tests/ -v --tb=short --ignore=tests/unit -q

# Core unit tests
source .venv/bin/activate && pytest tests/unit/ -v --tb=short

# API tests
source .venv/bin/activate && pytest api/tests/ -v --tb=short

# Frontend checks
cd web && npm run lint
cd web && npx tsc --noEmit
cd web && npm run test
cd web && npm run build

# E2E example
cd web && npx playwright test __tests__/e2e/conversation.spec.ts
```

When changing behavior, write the smallest relevant test first and confirm it fails for the
intended reason before implementing the fix.

Validation rules from the constitution and repository instructions:

- Run the smallest check that proves the change
- Rebuild the smallest affected runtime surface when behavior changes
- For `web/` changes, run `cd web && npx tsc --noEmit` before any rebuild
- Test browser-facing changes in the built-in VS Code browser before considering the work complete
- Use Docker Compose validation only when container behavior, deployment configuration, or cross-service integration changed

### 5. Format and Lint

```bash
source .venv/bin/activate && ruff check chatgpt_archive/ api/
source .venv/bin/activate && black --check chatgpt_archive/ api/
cd web && npm run lint
cd web && npx tsc --noEmit
```

### 6. Commit Changes

```bash
git add <files>
git commit -m "docs: align contributing guide with constitution"
```

Stage only the files relevant to your change. Do not include unrelated working tree changes.

### 7. Submit Pull Request

1. Push your branch to GitHub
2. Open a Pull Request against `main` branch
3. Describe your changes clearly
4. Link related issues (if any)
5. Wait for review

---

## Running Tests

### Test Structure

Tests are organized by layer:

- `tests/` and `tests/unit/` for the core Python package
- `api/tests/` for FastAPI behavior using temporary SQLite databases and shared fixtures
- `web/__tests__/` for frontend unit tests, MSW-backed service tests, and Playwright specs under `web/__tests__/e2e`

### Running Tests

```bash
# === Core package ===
source .venv/bin/activate && pytest tests/ -v --tb=short --ignore=tests/unit -q
source .venv/bin/activate && pytest tests/unit/ -v --tb=short
source .venv/bin/activate && pytest tests/unit/test_search.py::test_sanitize_query_empty_raises -q

# === API ===
source .venv/bin/activate && pytest api/tests/ -v --tb=short
source .venv/bin/activate && pytest api/tests/test_formatting_service.py::test_build_render_segments_returns_markdown_for_plain_text -q

# === Python lint / format ===
source .venv/bin/activate && ruff check chatgpt_archive/ api/
source .venv/bin/activate && black --check chatgpt_archive/ api/

# === Frontend ===
cd web && npm run lint
cd web && npx tsc --noEmit
cd web && npm run test
cd web && npm run test:coverage
cd web && npm run build

# === E2E ===
cd web && npx playwright test __tests__/e2e/conversation.spec.ts

# === Full stack ===
docker compose up -d
```

### Writing Tests

Example test structure:

```python
import pytest
import sqlite3
from pathlib import Path
from chatgpt_archive import importer

def test_import_validates_archive(tmp_path):
    """Test that import validates archive structure."""
    # Arrange
    invalid_dir = tmp_path / "invalid"
    invalid_dir.mkdir()
    
    # Act & Assert
    with pytest.raises(importer.InvalidArchiveError):
        importer.import_archive(invalid_dir, tmp_path / "test.db")

def test_import_creates_database(tmp_path, sample_archive):
    """Test that import creates database with correct schema."""
    # Arrange
    db_path = tmp_path / "test.db"
    
    # Act
    importer.import_archive(sample_archive, db_path)
    
    # Assert
    assert db_path.exists()
    conn = sqlite3.connect(str(db_path))
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    assert ("conversations",) in tables
    assert ("messages",) in tables
```

### Test Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def sample_archive(tmp_path):
    """Create a sample ChatGPT export archive."""
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    conversations_file = archive_dir / "conversations.json"
    # Create sample data...
    return archive_dir

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database."""
    db_path = tmp_path / "test.db"
    from chatgpt_archive.db import init_db
    conn = init_db(db_path)
    yield db_path
    conn.close()
```

---

## Code Style

### Repository Rules

- Follow existing file and naming conventions before introducing new patterns
- Add type hints to public Python functions
- Keep API code HTTP-focused; move shared logic into `chatgpt_archive/` or shared service layers
- Use functional React components; default to server components and add `'use client'` only when interactivity requires it
- Reuse the shared frontend API client and contract types instead of ad hoc requests
- Prefer short, explicit functions and the smallest viable abstraction

### Python Formatting and Linting

```bash
source .venv/bin/activate && ruff check chatgpt_archive/ api/
source .venv/bin/activate && black --check chatgpt_archive/ api/
```

### Frontend Validation

```bash
cd web && npm run lint
cd web && npx tsc --noEmit
```

Example type hints:

```python
from typing import Optional, List, Dict, Any
from pathlib import Path
import sqlite3

def get_conversation_by_id(
    conn: sqlite3.Connection, 
    openai_id: str
) -> Optional[sqlite3.Row]:
    """Retrieve a conversation by ID.
    
    Args:
        conn: Database connection
        openai_id: The OpenAI conversation ID
        
    Returns:
        Row with conversation data, or None if not found
    """
    # Implementation...
```

### Docstring Style

Use Google-style docstrings:

```python
def process_data(items: List[str], filter_empty: bool = True) -> Dict[str, int]:
    """Process a list of items and return counts.
    
    This function takes a list of string items, optionally filters out
    empty strings, and returns a dictionary mapping each unique item
    to its occurrence count.
    
    Args:
        items: List of string items to process
        filter_empty: Whether to exclude empty strings (default: True)
        
    Returns:
        Dictionary mapping items to their counts
        
    Raises:
        ValueError: If items list is None
        
    Example:
        >>> process_data(["a", "b", "a", ""])
        {"a": 2, "b": 1}
    """
    # Implementation...
```

---

## Submitting Changes

### Pull Request Checklist

Before submitting:

- [ ] The change follows the constitution in `.specify/memory/constitution.md`
- [ ] A failing automated test was added or updated first for each behavior change
- [ ] Shared logic stays in the correct layer and does not duplicate existing behavior
- [ ] The smallest relevant validation steps were run successfully
- [ ] For `web/` changes, `cd web && npx tsc --noEmit` ran before any rebuild
- [ ] Browser-facing changes were checked in the built-in VS Code browser
- [ ] Documentation updated where behavior or workflow changed
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with `main`

### Commit Message Format

Use conventional commit format:

```
type(scope): Short description

Longer explanation if needed. Wrap at 72 characters.

- Bullet points for details
- Reference issues: Fixes #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Build/tooling changes

**Examples**:
```
feat(export): Add CSV export format

Implements CSV exporter with configurable delimiters and quoting.
Includes tests and documentation updates.

Closes #45
```

```
fix(search): Handle special characters in FTS5 queries

Escape special characters before passing to FTS5 to prevent
query syntax errors.

Fixes #78
```

### Code Review Process

1. Submit PR with clear description
2. CI tests run automatically
3. Maintainer reviews code
4. Address feedback if requested
5. PR merged when approved

---

## Adding Features

### Planning a New Feature

1. **Check existing issues** - Someone may have requested it already
2. **Open a discussion** - Describe the feature and get feedback
3. **Review design docs** - Check the active `specs/NNN-*` directory and repository instructions
4. **Plan implementation** - Name the affected layers, tests, and validation steps before coding

### Implementation Checklist

For a new feature:

- [ ] Start with the smallest failing automated test that proves the feature or regression
- [ ] Update data model or schema in `chatgpt_archive/` if shared behavior changes
- [ ] Keep `api/` limited to HTTP orchestration and response shaping
- [ ] Use `web/src/services/api.ts` and aligned frontend contract types for browser work
- [ ] If transcript rendering changes, update the backend formatter, API response models, and frontend renderer together
- [ ] Add or update the smallest relevant tests in `tests/`, `api/tests/`, or `web/__tests__/`
- [ ] Add documentation in `docs/user-guide/usage.md`, `docs/user-guide/web-ui.md`, or other affected guides
- [ ] Update README if user-facing
- [ ] Add to CHANGELOG

### Example: Adding a New Export Format

1. **Create exporter class** in `chatgpt_archive/exporters/csv_export.py`:

```python
from chatgpt_archive.exporters.base import BaseExporter

class CSVExporter(BaseExporter):
    """Export conversations to CSV format."""
    
    def export(self, conversation: dict, messages: list) -> str:
        """Export to CSV format.
        
        Args:
            conversation: Conversation metadata dict
            messages: List of message dicts
            
        Returns:
            CSV formatted string
        """
        # Implementation...
```

2. **Register exporter** in `chatgpt_archive/exporters/__init__.py`:

```python
from chatgpt_archive.exporters.csv_export import CSVExporter

EXPORTERS = {
    "md": MarkdownExporter,
    "json": JSONExporter,
    "csv": CSVExporter,  # Add this
    # ...
}
```

3. **Update CLI** in `chatgpt_archive/cli.py`:

```python
@main.command()
@click.option("--format", "-f", "fmt",
              type=click.Choice(["md", "json", "yaml", "html", "xml", "csv"]),  # Add csv
              # ...
```

4. **Write tests** in `tests/unit/test_exporters.py`:

```python
def test_csv_export(sample_conversation, sample_messages):
    """Test CSV export format."""
    exporter = CSVExporter()
    output = exporter.export(sample_conversation, sample_messages)
    assert "role,content,timestamp" in output
    # More assertions...
```

5. **Update documentation**:
   - `README.md` - Add CSV to export formats table
   - `docs/user-guide/usage.md` - Add CSV examples
   - Add docstrings to new code

---

## Reporting Issues

### Bug Reports

Include:

1. **Description** - What happened vs. what was expected
2. **Steps to reproduce** - Minimal example that triggers the bug
3. **Environment**:
   ```bash
   chatgpt-archive --version
   python --version
   uname -a  # OS info
   ```
4. **Error messages** - Full error output (with `--json` if possible)
5. **Database stats** (if relevant):
   ```bash
   sqlite3 ~/.chatgpt-archive/chats.db "SELECT COUNT(*) FROM conversations;"
   ```

### Feature Requests

Include:

1. **Use case** - What problem does this solve?
2. **Proposed solution** - How should it work?
3. **Alternatives** - Other ways to achieve the goal?
4. **Examples** - Mock CLI commands or API calls

---

## Development Tips

### Debugging

Use Python debugger:

```python
import pdb; pdb.set_trace()  # Set breakpoint

# Or use breakpoint() in Python 3.7+
breakpoint()
```

### Database Inspection

```bash
# Open database
sqlite3 ~/.chatgpt-archive/chats.db

# View schema
.schema

# Query data
SELECT COUNT(*) FROM conversations;
SELECT * FROM messages LIMIT 5;

# Check FTS5 index
SELECT COUNT(*) FROM messages_fts;
```

### Testing with Real Archive

Use `test_real_archive.py` for integration testing:

```bash
# Set path to real ChatGPT export
export CHATGPT_TEST_ARCHIVE=/path/to/export

# Run integration tests
pytest tests/test_real_archive.py -v
```

### Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
importer.import_archive(archive_path, db_path)

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumtime')
stats.print_stats(20)  # Top 20 slowest functions
```

---

## Questions?

- **GitHub Issues**: [Report bugs or request features](https://github.com/peternicholls/OpenAI-Chats/issues)
- **GitHub Discussions**: Ask questions or share ideas
- **Review existing PRs**: See how others contribute

Thank you for contributing! 🎉
