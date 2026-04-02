# AI Collaboration Standard

This document defines how shared AI guidance should be organized across Codex and GitHub Copilot in this repository.

## Source Of Truth

- Canonical skill definitions live in `.ai/skills/...`.
- Codex-specific skill entry points (thin wrappers) live in `.codex/skills/...`.
- GitHub Copilot and GitHub-side agent instructions live in `.github/...`.
- Shared standards and reusable guidance live in `.ai/standards/...` and `.ai/patterns/...`.

## Directory Responsibilities

### `.codex/skills`

Use this for:

- Codex-specific skill trigger conditions
- Thin entry points that load from `.ai/skills/...`
- Codex-exclusive reference material

Do not duplicate skill content that lives in `.ai/skills/...`. Point at it instead.

### `.github`

Use this for:

- Copilot instructions
- GitHub prompt files
- Workflow-specific automation text

Keep these files concise and point them at canonical shared guidance in `.ai/...`.

### `.ai`

Use this for:

- Engineering standards (`standards/`)
- UI and architecture patterns (`patterns/`)
- Canonical skill definitions (`skills/`)
- Review criteria
- Shared glossaries and terminology

## Reuse Rules

- Do not duplicate the same long-form guidance across `.codex`, `.github`, and `.ai`.
- When the same rules apply to multiple tools, store them once in `.ai/...`.
- Canonical skill definitions go in `.ai/skills/`; tool-specific entry points go in `.codex/skills/` or `.github/instructions/`.
- When a tool needs extra constraints, add only the delta in that tool's native file.

## Writing Style

- Prefer stable guidance over task-specific prompts.
- Use short sections with clear headings.
- Include examples only when they materially improve consistency.
- Keep normative instructions explicit and testable.

## Change Management

- Update `.ai/...` first when changing shared policy.
- Update `.codex/...` or `.github/...` only when trigger logic or tool-specific framing changes.
- Avoid moving canonical guidance into generated or auto-maintained files.
