# Contributing to ChatGPT Archive

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

- Python 3.8 or higher
- pip and virtualenv (or similar)
- Git
- SQLite 3.x (usually pre-installed on macOS/Linux)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/peternicholls/OpenAI-Chats.git
cd OpenAI-Chats

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev,semantic]"

# Verify installation
chatgpt-archive --version
```

### Development Dependencies

The `[dev]` extra includes:
- `pytest` - Testing framework
- `black` - Code formatter
- `mypy` - Type checker
- `ruff` - Fast linter (replaces flake8, isort, etc.)

The `[semantic]` extra includes:
- `openai` - OpenAI API client
- `numpy` - Numerical operations
- `sqlite-vec` - Vector similarity search

---

## Project Structure

```
OpenAI-Chats/
├── chatgpt_archive/           # Main package
│   ├── __init__.py           # Package metadata
│   ├── __main__.py           # Entry point
│   ├── cli.py                # CLI commands
│   ├── db.py                 # Database connection & schema
│   ├── models.py             # Data models (dataclasses)
│   ├── importer.py           # Import logic
│   ├── search.py             # Search functionality
│   ├── embeddings.py         # Semantic search (optional)
│   └── exporters/            # Export formats
│       ├── __init__.py       # Exporter registry
│       ├── base.py           # Base exporter class
│       ├── markdown.py       # Markdown exporter
│       ├── json_export.py    # JSON exporter
│       ├── yaml_export.py    # YAML exporter
│       ├── html.py           # HTML exporter
│       └── xml_export.py     # XML exporter
├── tests/                    # Test suite
│   ├── test_cli.py          # CLI tests
│   ├── test_db.py           # Database tests
│   ├── test_importer.py     # Import tests
│   ├── test_models.py       # Model tests
│   └── test_real_archive.py # Integration tests
├── specs/                    # Design documents
│   └── 001-archive-search-export/
│       ├── spec.md          # Requirements
│       ├── plan.md          # Technical design
│       ├── data-model.md    # Database schema
│       └── contracts/       # API contracts
├── docs/                     # User documentation
│   ├── USAGE.md             # Command reference
│   ├── TROUBLESHOOTING.md   # Common issues
│   └── API.md               # Programmatic usage
├── pyproject.toml            # Package configuration
├── README.md                 # Project overview
└── CONTRIBUTING.md           # This file
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Or bug fix branch
git checkout -b fix/issue-123
```

### 2. Make Changes

Follow existing code patterns and conventions. Key principles:

- **Keep it simple**: Prefer clarity over cleverness
- **Type hints**: Use type hints for function parameters and returns
- **Docstrings**: Add Google-style docstrings for public functions
- **Error handling**: Use descriptive error messages
- **Testing**: Write tests for new features

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_importer.py

# Run with coverage
pytest --cov=chatgpt_archive

# Run tests in verbose mode
pytest -v
```

### 4. Format and Lint

```bash
# Format code with black
black chatgpt_archive/ tests/

# Lint with ruff
ruff check chatgpt_archive/ tests/

# Type check with mypy
mypy chatgpt_archive/
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: export to CSV format"

# Push to your fork
git push origin feature/my-new-feature
```

### 6. Submit Pull Request

1. Push your branch to GitHub
2. Open a Pull Request against `main` branch
3. Describe your changes clearly
4. Link related issues (if any)
5. Wait for review

---

## Running Tests

### Test Structure

Tests are organized by layer:

**Core Library** (`tests/`):
- `test_cli.py` - CLI command tests
- `test_db.py` - Database schema and queries
- `test_importer.py` - Import functionality
- `test_models.py` - Data model validation
- `test_real_archive.py` - Integration tests with real archive

**API Backend** (`api/tests/`):
- `test_health.py` - Health check endpoint
- `test_conversations.py` - Conversation CRUD endpoints
- `test_search.py` - Search functionality
- `test_export.py` - Export endpoints
- `test_import.py` - Import endpoints
- `test_tags.py` - Tag management
- `test_favorites.py` - Favorites management

**Frontend** (`web/__tests__/`):
- `services/api.test.ts` - API client tests
- `hooks/useDebounce.test.ts` - Hook tests
- `hooks/useSearch.test.ts` - Search hook tests
- `components/*.test.tsx` - React component tests
- `e2e/*.spec.ts` - Playwright E2E tests

### Running Tests

```bash
# === Core Library Tests ===
pytest tests/

# Specific file
pytest tests/test_importer.py

# With coverage
pytest --cov=chatgpt_archive --cov-report=html
open htmlcov/index.html

# === API Backend Tests ===
# Activate venv first
source .venv/bin/activate

# Run all API tests
pytest api/tests/ -v

# With coverage
pytest api/tests/ --cov=api --cov-report=term-missing

# === Frontend Tests ===
cd web

# Run unit/component tests
npm test

# Watch mode during development
npm run test:watch

# With coverage report
npm test -- --coverage

# === E2E Tests (Playwright) ===
cd web

# Run E2E tests (starts dev server on port 3030)
npm run test:e2e

# Run with UI
npx playwright test --ui

# Run specific test file
npx playwright test __tests__/e2e/home.spec.ts
```

### Writing Tests

Example test structure:

```python
import pytest
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

### Python Style Guide

Follow PEP 8 with these conventions:

- **Line length**: 100 characters (not 79)
- **Imports**: Group stdlib, third-party, local (separated by blank line)
- **Quotes**: Double quotes for strings, single for dict keys
- **Type hints**: Use for all function signatures

### Formatting with Black

Black is the code formatter - it handles most style automatically:

```bash
black chatgpt_archive/ tests/
```

### Linting with Ruff

Ruff checks for issues and enforces style:

```bash
# Check for issues
ruff check chatgpt_archive/ tests/

# Auto-fix where possible
ruff check --fix chatgpt_archive/ tests/
```

### Type Checking with Mypy

Add type hints and check with mypy:

```bash
mypy chatgpt_archive/
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

- [ ] Code is formatted with `black`
- [ ] Code passes `ruff` linting
- [ ] Type hints added and `mypy` passes
- [ ] Tests added for new functionality
- [ ] All tests pass (`pytest`)
- [ ] Documentation updated (README, USAGE, etc.)
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
3. **Review design docs** - Check `specs/` for architecture
4. **Plan implementation** - Consider impact on existing code

### Implementation Checklist

For a new feature:

- [ ] Update data model if needed (`chatgpt_archive/models.py`)
- [ ] Add database schema changes (`chatgpt_archive/db.py`)
- [ ] Implement core logic (e.g., `chatgpt_archive/importer.py`)
- [ ] Add CLI command or option (`chatgpt_archive/cli.py`)
- [ ] Write comprehensive tests (`tests/`)
- [ ] Add documentation (`docs/USAGE.md`)
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

4. **Write tests** in `tests/test_exporters.py`:

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
   - `docs/USAGE.md` - Add CSV examples
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
