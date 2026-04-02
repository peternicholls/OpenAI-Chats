# Shared AI Guidance

This directory is the shared source of truth for AI-facing guidance in this repository.

Use it for material that should be reused by multiple tools, including Codex skills and GitHub Copilot instructions.

## Layout

```text
.ai/
  standards/   # Rules, policies, and defaults
  patterns/    # Reusable implementation guidance and examples
  skills/      # Canonical shared skill definitions
```

## Authoring Rules

- Keep tool-specific trigger logic in the tool's native folder (`.codex/skills/`, `.github/instructions/`).
- Put reusable engineering guidance and canonical skill definitions in `.ai/`.
- Reference shared documents from `.codex/skills/...` and `.github/...` instead of copying content.
- Treat `.ai/` documents as canonical unless a tool-specific file explicitly overrides them.
