# Copilot CLI Habit Tips for the USER

## 1. Check active instructions first

Use `/instructions` before restating repo rules in prose.

- I often rely on repo-specific guidance under `.github/`
- `/instructions` makes the active instruction sources explicit
- This should reduce “please remember these constraints” follow-up turns

## 2. Pick the right agent early for sprint/spec work

Use `/agent` when the work is really planning, specification, or task-generation.

- This repo already has `speckit.*` agents in `.github/agents/`
- Use those for spec-heavy work
- Use the standard agent for normal coding and editing passes

## 3. Use `/fleet` and `/tasks` for broad repo analysis

For asks like “analyze the codebase”, “check consistency”, or other cross-cutting reviews:

- Start with `/fleet` to parallelize the work
- Use `/tasks` to monitor background jobs
- Prefer this over stuffing all orchestration into one long prompt

## 4. Write long prompts in the external editor and attach files directly

Use `ctrl+g` for multi-part prompts and `@` to mention files.

- My prompts often combine workflow rules, architecture preferences, and corrections
- Bare follow-ups like `all`, `both`, `y`, or pasted paths are easy to misread
- `ctrl+g` + `@file` should make requests clearer and more reproducible

## 5. Use `/review` for consistency passes

When I want “check that this is consistent and aligned”, prefer `/review`.

- Keep freeform prompts for requests to build or change things
- Use the review agent when the main goal is correctness and architectural consistency
- This should reduce the amount of manual framing needed

## Working pattern to practice

`/instructions` -> `/agent` or `/review` -> `/fleet` / `/tasks` when the job is broad

