# Agent Instruction Pointer

The authoritative repository-wide Copilot instructions live in `../copilot-instructions.md`.

Use that file for shared repository guidance, architecture, conventions, and commands.

Use this directory only for specialized agent instructions and workflow-specific handoffs.

## How To Use This Directory

- Start with `../copilot-instructions.md`.
- Open a more specific file in `.github/agents/` only when the task clearly maps to that workflow or agent.
- Avoid copying repository-wide guidance into agent files unless the workflow genuinely requires a local override.

## Repository Workflow Notes

- This repository may include generated or workflow-managed files in `.github/agents/`.
- If those files are updated by tooling, keep repository-wide guidance centralized in `../copilot-instructions.md` and leave this file as a thin pointer.
- Current feature context and recent stack changes have been consolidated into the main Copilot instruction file.
