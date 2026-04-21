# Frontend UI Pattern Notes

Use this document for shared frontend presentation guidance that may be referenced by both Codex and GitHub-side instructions.

## Default Approach

- Preserve existing visual language when working inside an established UI.
- Use expressive typography and deliberate spacing rather than generic template layouts.
- Prefer a clear design direction over safe but interchangeable styling.

## Styling Decisions

- Define CSS custom properties for reusable tokens.
- Use motion with intent, not as filler.
- Favor composition and layout primitives over deeply nested utility overrides.

## Responsiveness

- Design for both desktop and mobile from the start.
- Prefer component-level responsiveness when the UI is modular.
- Validate that typography and spacing still work at narrow widths.

## Accessibility

- Maintain visible focus states.
- Preserve readable contrast.
- Respect reduced-motion preferences when adding non-essential animation.
