# AI Collaboration Standard

This document defines how shared AI guidance should be organized across Codex and GitHub Copilot in this repository.

## Source Of Truth

- Codex skills live in `.codex/skills/...`.
- GitHub Copilot and GitHub-side agent instructions live in `.github/...`.
- Shared standards and reusable guidance live in `.ai/...`.

## Directory Responsibilities

### `.codex/skills`

Use this for:

- Skill trigger conditions
- Codex-specific workflows
- Short instructions on when to load shared guidance

Do not use this for long reusable engineering standards that may also be needed by other tools.

### `.github`

Use this for:

- Copilot instructions
- GitHub prompt files
- Workflow-specific automation text

Keep these files concise and point them at canonical shared guidance in `.ai/...`.

### `.ai`

Use this for:

- Engineering standards
- UI and architecture patterns
- Review criteria
- Shared glossaries and terminology

## Reuse Rules

- Do not duplicate the same long-form guidance across `.codex`, `.github`, and `.ai`.
- When the same rules apply to multiple tools, store them once in `.ai/...`.
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
