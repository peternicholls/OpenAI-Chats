<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 2.0.0 (MAJOR: principles materially redefined around repo architecture, TDD, and pragmatic clean-code delivery)
Modified principles:
  - I. Data-First Architecture → I. Source-of-Truth Boundaries
  - II. CLI-First Interface → II. Thin Adapters, Shared Core
  - III. Fast Search & Retrieval → III. Test-Driven Delivery (NON-NEGOTIABLE)
  - IV. Format-Agnostic Export → IV. Clean Code, Small Surfaces, Pragmatic Simplicity
  - V. Simplicity & Composability → V. End-to-End Validation Before Completion
Added sections:
  - Architecture Boundaries
  - Delivery Workflow
Removed sections:
  - Data Integrity
  - Export Formats
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
  - .specify/templates/commands/ ⚠ not present in this repository
Runtime guidance reviewed:
  - CONTRIBUTING.md ✅ updated
  - README.md ✅ reviewed, no direct constitutional reference to update
Follow-up TODOs: None
-->

# OpenAI-Chats Constitution

## Core Principles

### I. Source-of-Truth Boundaries

The extracted OpenAI archive and the shared core library in `chatgpt_archive/` MUST
remain the source of truth for archive parsing, SQLite schema and migrations, search,
embeddings, and export behavior. Contributors and agents MUST extend existing
cross-layer pipelines before creating parallel implementations. Internal SQLite IDs and
public OpenAI IDs MUST remain distinct. Changes to transcript rendering MUST update the
backend formatter, API response models, and frontend rendering path together. Rationale:
the project already spans CLI, API, and web surfaces; correctness depends on one shared
domain model rather than per-surface drift.

### II. Thin Adapters, Shared Core

`api/` MUST stay HTTP-focused and `web/` MUST consume shared client contracts instead of
ad hoc data access. Business rules belong in the core library or in explicitly shared
service layers, not duplicated inside routers, React components, or endpoint handlers.
New code MUST prefer existing repository patterns, use clear names, small functions, and
explicit dependencies. Abstractions MUST be introduced only when they remove repeated
complexity that already exists. Rationale: thin adapters keep behavior coherent and make
tests meaningful at the correct layer.

### III. Test-Driven Delivery (NON-NEGOTIABLE)

Behavior changes MUST follow a red-green-refactor loop. Contributors and agents MUST
start by defining or updating the smallest automated test that proves the behavior,
observe that it fails for the intended reason, then implement the minimum code needed to
make it pass, and only then refactor. Skipping the failing-test step is allowed only for
pure documentation changes or non-behavioral maintenance with no executable impact. Bug
fixes MUST begin with a regression test whenever the failure can be reproduced in an
automated test. Rationale: this repository spans Python, FastAPI, Next.js, and transcript
formatting pipelines; TDD is the fastest way to prevent regressions while still moving
quickly.

### IV. Clean Code, Small Surfaces, Pragmatic Simplicity

Clean code in this repository means code that is easy to remove, easy to test, and easy
to trace across layers. Every change MUST choose the smallest viable design that solves
the user problem without speculative generalization. Contributors and agents MUST prefer
clarity over cleverness, keep public functions typed, avoid one-off fetch paths when a
shared client exists, and remove or reshape incidental complexity they directly touch
when doing so is low-risk. They MUST NOT perform broad opportunistic rewrites, invent new
framework layers, or add abstractions in anticipation of hypothetical future needs.
Rationale: pragmatism is a quality constraint, not a shortcut; the cleanest solution here
is usually the one that fits the existing architecture with the fewest moving parts.

### V. End-to-End Validation Before Completion

No change is complete until the smallest validation stack that proves it has been run.
Contributors and agents MUST run the narrowest relevant automated checks, rebuild the
smallest affected surface when runtime behavior changes, and verify browser-facing
changes in the built-in VS Code browser. For `web/` changes, `cd web && npx tsc --noEmit`
MUST run before any rebuild. When containerized behavior, deployment configuration, or
cross-service integration changes, validation MUST include the relevant Docker Compose
path. Rationale: local correctness in one layer is insufficient for a repository whose
main value is the behavior users see across CLI, API, and web flows.

## Architecture Boundaries

- `chatgpt_archive/` MUST remain the home of archive import, SQLite schema and
  migrations, FTS5 search, embeddings, and export formats.
- `api/` MUST limit itself to HTTP orchestration, validation, progress reporting, and
  response shaping.
- `web/` MUST use the shared API client and aligned contract types instead of ad hoc
  request code.
- Media MUST stay filesystem-backed; blobs MUST NOT be moved into SQLite without a new
  constitutional amendment.
- Specs, plans, and tasks MUST name the real files and layers affected by a change, and
  any exception to these boundaries MUST be justified in the plan's complexity tracking
  section.

## Delivery Workflow

- Work MUST begin by checking repository guidance, the current branch, and any matching
  `specs/NNN-*` directory.
- Plans MUST state the intended test strategy, affected layer boundaries, and the
  smallest user-visible increment.
- Tasks MUST put executable test work ahead of implementation work for each behavior
  change and MUST include explicit validation tasks.
- Browser-accessible changes MUST be exercised locally after rebuild, not only reasoned
  about from static code review.
- Multi-step work SHOULD record meaningful progress and decisions so later contributors
  can understand why a path was chosen.

## Governance

This constitution supersedes conflicting local process preferences for this repository.
Compliance review is required in every plan, task list, implementation, and review.
Amendments MUST document the rationale, the affected principles or sections, any template
or workflow updates, and any migration impact on existing specs or active work. Versioning
follows semantic versioning for the constitution itself: MAJOR for incompatible principle
changes or removals, MINOR for new principles or materially expanded governance, PATCH for
clarifications that do not change expected behavior. If a change intentionally violates a
principle, that exception MUST be explicit, narrow, and justified in the relevant plan
before implementation proceeds.

**Version**: 2.0.0 | **Ratified**: 2026-01-26 | **Last Amended**: 2026-04-13
