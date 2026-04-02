# CSS Guidelines

This document is the canonical shared CSS standard for AI-assisted work in this repository.

Codex skills and GitHub Copilot instructions should reference this file instead of copying CSS guidance into tool-specific files.

## Layout And Responsiveness

### Container Queries

Prefer component-scoped responsiveness where possible.

```css
.card {
  container: --card / inline-size;
}

@container --card (width < 40ch) {
  /* Component-specific responsive adjustments */
}

@container (20ch < width < 50ch) {
  /* Range syntax is preferred over min/max pairs when readable */
}
```

Useful container units:

- `cqi`
- `cqb`
- `cqw`
- `cqh`

### Media Query Range Syntax

Prefer range syntax over older `min-` and `max-` forms when browser support is acceptable for the target surface.

```css
@media (width <= 1024px) { }
@media (360px < width < 1024px) { }
```

### Grid

- Use `subgrid` when nested layouts should inherit parent track alignment.
- Consider masonry-style layouts only when the UX benefits from uneven content stacking and the target surface supports it.

## Color And Theming

### Color Scheme

Use `color-scheme` intentionally. Do not opt into dark mode by default unless the product already supports it.

```css
:root {
  color-scheme: light dark;
  --surface-1: light-dark(white, #222);
  --text-1: light-dark(#222, #fff);
}
```

### Modern Color Spaces

Prefer `oklch` or `oklab` for authoring when high-fidelity color control matters.

```css
.vibrant {
  background: oklch(72% 75% 330);
}

.gradient {
  background: linear-gradient(
    to right in oklch,
    color(display-p3 1 0 .5),
    color(display-p3 0 1 1)
  );
}
```

### Color Manipulation

Use modern color functions instead of hard-coded variants when maintainability benefits.

```css
.lighten {
  background: color-mix(in oklab, var(--brand), white);
}

.lighter {
  background: oklch(from blue 75% c h);
}

.semi-transparent {
  background: oklch(from var(--color) l c h / 50%);
}
```

## Typography

### Wrapping

```css
h1 {
  text-wrap: balance;
  max-inline-size: 25ch;
}

p {
  text-wrap: pretty;
  max-inline-size: 50ch;
}
```

### Fluid Type

Use `clamp()` for fluid sizing when it improves responsiveness without creating abrupt breakpoints.

```css
.heading {
  font-size: clamp(1rem, 1rem + 0.5vw, 2rem);
}
```

### Viewport Units

Use modern viewport units where mobile browser UI behavior matters:

- `dvh` / `dvw`
- `svh` / `svw`
- `lvh` / `lvw`

## Motion

### Scroll-Driven Animation

Use scroll-linked motion sparingly and only when it adds clear value.

```css
.parallax {
  animation: slide-up linear both;
  animation-timeline: scroll();
}

.fade-in {
  animation: fade linear both;
  animation-timeline: view();
  animation-range: cover -75cqi contain 20cqi;
}
```

### View Transitions

Use same-document view transitions where they improve continuity. Treat cross-document transitions as a progressive enhancement.

```css
@view-transition {
  navigation: auto;
}

nav {
  view-transition-name: --persist-nav;
}
```

### Easing

Prefer authored easing curves for distinctive motion rather than default browser easing.

```css
.springy {
  --spring: linear(
    0, 0.14 4%, 0.94 17%, 1.15 24% 30%, 1.02 43%, 0.98 51%, 1 77%, 1
  );
  transition: transform 1s var(--spring);
}
```

## Implementation Rules

- Match the repo's existing design system unless the task explicitly asks for a new visual direction.
- Use CSS variables for shared tokens.
- Prefer progressive enhancement for newer platform features.
- Avoid adding complexity when plain layout primitives solve the problem.
- Document browser support assumptions when using cutting-edge features in production code.
