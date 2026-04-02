---
name: modern-css
description: Specialized knowledge for writing modern high-quality CSS. Trigger this skill when starting a new CSS project/file, when the user asks about new CSS features (e.g. Masonry, View Transitions, Container Queries, Scroll-driven animations), or requests refactoring of legacy styles to modern standards.
---

# Modern CSS

This skill is the Codex-specific entry point for CSS work in this repository.

## When To Use

- Starting a new CSS file or styling system
- Refactoring legacy CSS to modern platform features
- Answering questions about modern CSS capabilities
- Implementing or reviewing advanced responsive, color, typography, or motion behavior

## Shared Guidance

Use these shared documents as the canonical reference before making CSS decisions:

- [`../../../.ai/standards/css-guidelines.md`](../../../.ai/standards/css-guidelines.md)
- [`../../../.ai/patterns/frontend-ui.md`](../../../.ai/patterns/frontend-ui.md)
- [`../../../.ai/standards/ai-collaboration.md`](../../../.ai/standards/ai-collaboration.md)

## Codex Workflow

1. Read the shared CSS guidance before proposing or writing styles.
2. Preserve the existing design system unless the user asks for a new visual direction.
3. Prefer modern CSS primitives when they simplify the implementation and browser support is acceptable.
4. Call out progressive-enhancement assumptions when using newer platform features.
5. Keep tool-specific reasoning here and shared engineering standards in `.ai/...`.

## Output Expectations

- Produce CSS that is modern, readable, and maintainable.
- Reuse shared standards from `.ai/...` instead of restating them in the skill.
- Keep examples in shared docs when they may also be useful to GitHub Copilot instructions.
