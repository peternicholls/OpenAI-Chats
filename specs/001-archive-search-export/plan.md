# Implementation Plan: ChatGPT Archive Search & Export

**Branch**: `001-archive-search-export` | **Date**: 2026-01-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-archive-search-export/spec.md`

## Summary

Build a CLI tool to import ChatGPT conversation archives into a SQLite database with FTS5 full-text search, enabling fast keyword search, conversation viewing, and multi-format export (Markdown, JSON, YAML, HTML, XML). The tool treats the original archive as source of truth while providing a fast queryable index.

## Technical Context

**Language/Version**: Python 3.8+ (cross-platform, no compilation)  
**Primary Dependencies**: click (CLI), pyyaml (YAML export), sqlite3 (stdlib), json (stdlib), xml.etree (stdlib)  
**Storage**: SQLite with FTS5 virtual tables (portable, single file, no server)  
**Testing**: pytest with pytest-cov  
**Target Platform**: macOS, Linux, Windows (cross-platform CLI)  
**Project Type**: single (CLI tool package)  
**Performance Goals**: <60s import for 250MB/1700+ conversations, <500ms search, <2s export  
**Constraints**: Fully offline, database <2x original JSON size, no data loss  
**Scale/Scope**: Single-user, ~2000 conversations, ~250MB archives

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Data-First | Archive is source of truth, DB is derived | ✅ PASS | Import creates index, never modifies archive |
| II. CLI-First | All features via CLI | ✅ PASS | 5 commands: import, search, list, view, export |
| III. Fast Search | <500ms search with FTS5 | ✅ PASS | FTS5 indexed at import time |
| IV. Format-Agnostic | MD, JSON, YAML, HTML, XML export | ✅ PASS | All 5 formats implemented |
| V. Simplicity | SQLite single file, YAGNI | ✅ PASS | No server, minimal dependencies |
| Data Integrity | Validate JSON, preserve IDs | ✅ PASS | Idempotent imports, OpenAI IDs as keys |

**Gate Result**: ✅ ALL PASS - Proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/001-archive-search-export/
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - database schema
├── quickstart.md        # Phase 1 output - getting started guide
├── contracts/           # Phase 1 output - CLI interface spec
│   └── cli.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
chatgpt_archive/
├── __init__.py          # Package init, version
├── __main__.py          # Entry point for python -m
├── cli.py               # Click command group and commands
├── db.py                # Database connection, schema setup
├── models.py            # Data classes for Conversation, Message
├── importer.py          # JSON parsing, database insertion
├── search.py            # FTS5 query building, result formatting
└── exporters/
    ├── __init__.py      # Exporter registry
    ├── base.py          # Abstract base exporter
    ├── markdown.py      # Markdown format
    ├── json_export.py   # JSON format
    ├── yaml_export.py   # YAML format
    ├── html.py          # HTML format
    └── xml_export.py    # XML format

tests/
├── conftest.py          # Shared fixtures
├── unit/
│   ├── test_importer.py
│   ├── test_search.py
│   └── test_exporters.py
└── integration/
    └── test_cli.py

pyproject.toml           # Package config with [project.scripts]
README.md                # User documentation
```

**Structure Decision**: Single project layout chosen per Constitution Principle V (Simplicity). CLI tool with no frontend/backend split needed.

## Complexity Tracking

> No violations - design follows all constitution principles

| Aspect | Decision | Justification |
|--------|----------|---------------|
| Database | SQLite with FTS5 | Constitution V: single file, no server |
| CLI | Click with @click.group | Standard Python CLI, subcommand pattern |
| Export | Separate modules per format | Maintainability without over-engineering |
