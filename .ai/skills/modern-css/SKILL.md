---
name: modern-css
description: "Specialized knowledge for writing modern high-quality CSS. Use when starting a new CSS file or styling system, when asked about new CSS features (e.g. Masonry, View Transitions, Container Queries, Scroll-driven animations), or when refactoring legacy styles to modern platform standards."
---

# Modern CSS

## When To Use

- Starting a new CSS file or styling system
- Refactoring legacy CSS to modern platform features
- Answering questions about modern CSS capabilities
- Implementing or reviewing advanced responsive, color, typography, or motion behavior

## Shared Guidance

Read these shared documents before making any CSS decisions:

- [css-guidelines.md](../../standards/css-guidelines.md) — Container queries, layout, design tokens
- [frontend-ui.md](../../patterns/frontend-ui.md) — Styling decisions, responsiveness, accessibility

## Workflow

1. Read the shared CSS guidance above before proposing or writing styles.
2. Preserve the existing design system unless the user asks for a new visual direction.
3. Prefer modern CSS primitives when they simplify the implementation and browser support is acceptable.
4. Call out progressive-enhancement assumptions when using newer platform features.

## Output Expectations

- Produce CSS that is modern, readable, and maintainable.
- Reuse shared standards from `.ai/standards/` and `.ai/patterns/` rather than restating them.
- Keep tool-specific framing in the tool's own entry point (`.codex/skills/` or `.github/instructions/`).
