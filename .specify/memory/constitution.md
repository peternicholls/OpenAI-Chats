<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0 (MAJOR: Initial constitution)
Modified principles: N/A (initial)
Added sections: Core Principles (5), Data Integrity, Export Formats, Governance
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (compatible - uses generic Constitution Check)
  - .specify/templates/spec-template.md ✅ (compatible - no constitutional references)
  - .specify/templates/tasks-template.md ✅ (compatible - no constitutional references)
Follow-up TODOs: None
-->

# ChatGPT Archive Search Constitution

## Core Principles

Important: the development enviorment is on MacOS.

### I. Data-First Architecture

All features MUST treat the ChatGPT export archive as the single source of truth.
- The original JSON export structure MUST be preserved and never modified
- Database serves as a derived index; archive remains canonical
- Import operations MUST be idempotent and re-runnable without data loss
- Clear separation between raw archive data and derived/indexed data

### II. CLI-First Interface

Every capability MUST be accessible via command-line interface before any GUI.
- Text in/out protocol: stdin/args → stdout, errors → stderr
- All output formats MUST be selectable via CLI flags
- Human-readable output by default; machine-readable (JSON) via `--json` flag
- Exit codes MUST follow Unix conventions (0 = success, non-zero = error)

### III. Fast Search & Retrieval

Search operations MUST prioritize speed and relevance.
- Full-text search MUST return results in under 500ms for typical archives
- Search indexing MUST happen at import time, not query time
- Results MUST include context (conversation title, date, message preview)
- Support filtering by date range, conversation title, and message content

### IV. Format-Agnostic Export

Export functionality MUST support multiple output formats without data loss.
- Supported formats: Markdown, JSON, YAML, HTML, XML (minimum requirement)
- Each format MUST preserve conversation structure and metadata
- Export MUST work for single conversations or batch operations
- Format selection via CLI flag or interactive prompt

### V. Simplicity & Composability

Start simple; complexity MUST be justified.
- Single SQLite database file by default (portable, no server required)
- YAGNI: Do not add features until explicitly needed
- Unix philosophy: small tools that compose well
- Configuration via environment variables or simple config file

## Data Integrity

Data integrity is NON-NEGOTIABLE.
- Import MUST validate JSON structure before processing
- Database schema MUST include foreign keys and constraints
- Backup mechanism MUST exist before any destructive operation
- Conversation IDs from OpenAI export MUST be preserved as primary identifiers

## Export Formats

All export formats MUST meet these requirements:

| Format   | Structure     | Use Case                          |
|----------|---------------|-----------------------------------|
| Markdown | Conversational | Human reading, documentation     |
| JSON     | Structured    | Programmatic access, re-import   |
| YAML     | Structured    | Configuration, human-editable    |
| HTML     | Visual        | Browser viewing, sharing         |
| XML      | Structured    | Legacy system integration        |

## Governance

This constitution supersedes all other development practices for this project.
- Amendments require: documentation of change, rationale, and migration impact
- Version follows semantic versioning (MAJOR.MINOR.PATCH)
- All implementation decisions MUST reference applicable principles
- Complexity beyond these principles MUST be explicitly justified in specs

**Version**: 1.0.0 | **Ratified**: 2026-01-26 | **Last Amended**: 2026-01-26
