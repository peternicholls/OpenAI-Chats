# Implementation Plan: Comprehensive Test Coverage

**Branch**: `002-web-ui` | **Date**: 2026-02-13 | **Spec**: [spec.md](spec.md)  
**Input**: User request: "Plan tests to ensure coverage"

## Summary

Add comprehensive test coverage across all layers of the ChatGPT Archive application:
- **Python Library** (chatgpt_archive): Expand existing tests for search, embeddings, exporters
- **API Backend** (api): New test suite for all REST endpoints
- **Web Frontend** (web): New test suite for React components, hooks, and API client

## Technical Context

**Language/Version**: Python 3.11, TypeScript 5.4, Node 20.x  
**Primary Dependencies**: pytest, httpx, Vitest, React Testing Library, MSW  
**Storage**: SQLite (in-memory for tests)  
**Testing**: pytest (Python), Vitest (TypeScript)  
**Target Platform**: macOS/Linux development, Docker production  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: Tests complete in <60s (unit), <5m (integration)  
**Constraints**: No external API calls during tests (mock OpenAI)  
**Scale/Scope**: ~150 test cases total (50 Python + 100 TypeScript)

## Constitution Check

*GATE: Pass ✅*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Data-First Architecture | ✅ | Tests use real JSON fixtures from archive format |
| II. CLI-First Interface | ✅ | CLI tests already exist (test_cli.py) |
| III. Fast Search & Retrieval | ✅ | Search tests will verify <500ms |
| IV. Format-Agnostic Export | ✅ | New exporter tests cover all 7 formats |
| V. Simplicity & Composability | ✅ | Tests use temp SQLite, no infrastructure |

## Test Coverage Gap Analysis

### Current State

| Module | Existing Tests | Coverage |
|--------|----------------|----------|
| chatgpt_archive/db.py | ✅ test_db.py | Good |
| chatgpt_archive/importer.py | ✅ test_importer.py | Good |
| chatgpt_archive/models.py | ✅ test_models.py | Good |
| chatgpt_archive/cli.py | ✅ test_cli.py | Partial |
| chatgpt_archive/search.py | ❌ | **NONE** |
| chatgpt_archive/embeddings.py | ❌ | **NONE** |
| chatgpt_archive/exporters/* | ❌ | **NONE** |
| api/routers/* | ❌ | **NONE** |
| api/services/* | ❌ | **NONE** |
| web/src/services/* | ❌ | **NONE** |
| web/src/hooks/* | ❌ | **NONE** |
| web/src/components/* | ❌ | **NONE** |

### Target State (100% endpoint coverage)

| Module | Tests Needed | Priority |
|--------|--------------|----------|
| Python exporters (7 formats) | 14 tests | P1 |
| Python search module | 8 tests | P1 |
| API conversations endpoint | 6 tests | P1 |
| API search endpoint | 4 tests | P1 |
| API export endpoint | 8 tests | P1 |
| API tags endpoint | 6 tests | P1 |
| API favorites endpoint | 4 tests | P1 |
| API import endpoint | 4 tests | P2 |
| API settings endpoint | 4 tests | P2 |
| Frontend API client | 15 tests | P1 |
| Frontend hooks | 20 tests | P2 |
| Frontend components | 30 tests | P2 |

## Project Structure

### Test Files to Create

```text
# Python Tests (pytest)
tests/
├── conftest.py                    # Shared fixtures
├── fixtures/
│   ├── sample_conversation.json   # Minimal conversation
│   └── sample_archive/            # Complete archive structure
├── unit/
│   ├── test_exporters.py          # All 7 export formats
│   ├── test_search.py             # FTS5 search module
│   └── test_embeddings.py         # Embedding generation
└── integration/
    ├── test_api_conversations.py  # Conversation CRUD
    ├── test_api_search.py         # Search endpoint
    ├── test_api_export.py         # Export endpoint
    ├── test_api_import.py         # Import endpoint
    ├── test_api_tags.py           # Tags endpoint
    ├── test_api_favorites.py      # Favorites endpoint
    └── test_api_settings.py       # Settings endpoint

# TypeScript Tests (Vitest)
web/
├── vitest.config.ts
├── vitest.setup.ts
├── __tests__/
│   ├── mocks/
│   │   └── handlers.ts            # MSW request handlers
│   ├── services/
│   │   └── api.test.ts            # API client tests
│   ├── hooks/
│   │   ├── useConversations.test.ts
│   │   ├── useSearch.test.ts
│   │   ├── useFavorites.test.ts
│   │   └── useTags.test.ts
│   └── components/
│       ├── ConversationCard.test.tsx
│       ├── MessageBubble.test.tsx
│       └── SearchBar.test.tsx
└── package.json                   # Add test dependencies
```

## Dependencies to Add

### Python (pyproject.toml)
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "httpx>=0.27",
    "pytest-mock>=3.12",
]
```

### TypeScript (web/package.json)
```json
{
  "devDependencies": {
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/user-event": "^14.5.0",
    "vitest": "^2.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "jsdom": "^24.0.0",
    "msw": "^2.3.0"
  }
}
```

## Test Specifications

See [contracts/test-specs.md](contracts/test-specs.md) for detailed test case specifications covering:
- **118 test cases** across Python and TypeScript
- Unit tests for exporters, search, embeddings
- Integration tests for all API endpoints
- Frontend component, hook, and service tests
- Test fixtures and sample data

## Complexity Tracking

*No violations - tests follow existing project patterns*
