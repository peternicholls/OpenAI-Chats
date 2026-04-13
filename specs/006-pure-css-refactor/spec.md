# Feature Specification: Pure Modern CSS Refactor

**Feature Branch**: `006-pure-css-refactor`
**Created**: 2026-04-13
**Status**: Draft
**Input**: User description: "Refactor away from Tailwind / React frameworks into a pure modern CSS design paradigm"

## User Scenarios & Testing *(mandatory)*

Every story, acceptance scenario, and edge case in this document MUST be specific enough
to drive failing automated tests before implementation begins.

### User Story 1 — Visual Parity After Migration (Priority: P1)

A user navigates the application after the CSS refactor and sees the same layout, colors, typography, spacing, and interactive states they saw before the migration. No page or component looks broken, misaligned, or visually different from the pre-migration baseline.

**Why this priority**: If the refactor introduces visual regressions, no other goal matters — the product is broken from the user's perspective. Pixel-accurate parity is the foundation that every other story depends on.

**Independent Test**: Take full-page screenshots of every major view (conversation list, conversation detail, search results, export dialog, favorites) before and after the migration. Overlay them and verify no meaningful visual differences exist.

**Acceptance Scenarios**:

1. **Given** the application is running with the new CSS, **When** a user loads the conversation list page, **Then** the layout, card styling, pagination, and spacing match the pre-migration baseline.
2. **Given** the application is running with the new CSS, **When** a user opens a conversation detail view, **Then** message bubbles, code blocks, markdown rendering, attachment thumbnails, and all interactive elements match the pre-migration baseline.
3. **Given** the application is running with the new CSS, **When** a user resizes the browser from desktop to mobile widths, **Then** all responsive breakpoints produce the same layout behavior as the pre-migration baseline.
4. **Given** the application is running with the new CSS, **When** a user interacts with hover states, focus rings, transitions, and animations, **Then** all interactive feedback matches the pre-migration baseline.

---

### User Story 2 — Tailwind Fully Removed From the Build (Priority: P1)

A developer inspects the project and confirms that Tailwind CSS, its configuration, its PostCSS plugin, and the `cn()` / `tailwind-merge` utility are completely absent from the dependency tree, build pipeline, and source code. No Tailwind utility classes remain in any component.

**Why this priority**: Leaving partial Tailwind artifacts would create a confusing hybrid that defeats the purpose of the migration. Full removal is a hard gate for the refactor to be considered complete.

**Independent Test**: Search the entire source tree for Tailwind class names, `cn(` calls, Tailwind config files, and Tailwind-related dependencies. All searches return zero results.

**Acceptance Scenarios**:

1. **Given** the migration is complete, **When** a developer searches for Tailwind utility class patterns (e.g., `flex`, `bg-`, `text-`, `p-`, `m-`, `rounded-`) used as CSS class names in JSX, **Then** zero results are found.
2. **Given** the migration is complete, **When** a developer inspects `package.json`, **Then** `tailwindcss`, `@tailwindcss/postcss`, `tailwind-merge`, and any Tailwind plugins are absent from both `dependencies` and `devDependencies`.
3. **Given** the migration is complete, **When** a developer searches for the `cn(` utility function, **Then** zero usages and zero definitions are found.
4. **Given** the migration is complete, **When** a developer runs the production build, **Then** the build succeeds without any Tailwind-related tooling in the pipeline.

---

### User Story 3 — Component Styling Uses Modern CSS Patterns (Priority: P1)

A developer opens any component and finds its styles expressed through modern CSS — custom properties for design tokens, CSS nesting, `:has()`, container queries, and standard selectors — rather than utility class strings embedded in markup. Styles are co-located or scoped to their component.

**Why this priority**: The styling paradigm shift is the core deliverable. Without this, the refactor is merely deletion rather than a meaningful architectural improvement.

**Independent Test**: Open any five components at random. Verify each uses CSS custom properties for shared values, standard CSS selectors for styling, and has no inline utility class strings for layout or appearance.

**Acceptance Scenarios**:

1. **Given** the migration is complete, **When** a developer opens a component file, **Then** visual styling is expressed in CSS files (global stylesheet or CSS modules) rather than in `className` strings containing layout/appearance utilities.
2. **Given** the migration is complete, **When** a developer inspects the global stylesheet, **Then** design tokens (colors, spacing scale, typography, radii, shadows) are defined as CSS custom properties and referenced throughout component styles.
3. **Given** the migration is complete, **When** a developer reviews responsive behavior, **Then** breakpoints are handled through standard CSS media queries or container queries rather than responsive utility prefixes.

---

### User Story 4 — Shared UI Primitives Remain Functional (Priority: P2)

A user interacts with all shared UI components — buttons, dialogs, dropdowns, tabs, form inputs, badges, scroll areas, and other primitives — and they behave identically to the pre-migration versions: correct keyboard navigation, focus management, screen-reader announcements, and visual states.

**Why this priority**: The application relies on a library of shared UI primitives currently provided by shadcn/ui. These must continue to work with full accessibility support after their styles are rewritten.

**Independent Test**: Exercise every shared UI primitive through its keyboard and mouse interactions. Verify focus order, ARIA attributes, and visual states are preserved.

**Acceptance Scenarios**:

1. **Given** the migration is complete, **When** a user opens a dialog, **Then** focus is trapped inside the dialog, Escape closes it, and focus returns to the trigger element.
2. **Given** the migration is complete, **When** a user navigates a dropdown menu with the keyboard, **Then** arrow keys move between items, Enter selects, and Escape closes the menu.
3. **Given** the migration is complete, **When** a user tabs through form elements, **Then** focus rings are visible and follow a logical order.
4. **Given** the migration is complete, **When** a screen reader reads a button or input, **Then** the accessible name and role are announced correctly.

---

### User Story 5 — Dark Mode / Theme Support Preserved (Priority: P2)

A user who has their system set to dark mode (or who toggles a theme preference if one exists) sees the application correctly themed with appropriate colors, contrast, and readability — matching the pre-migration dark mode experience.

**Why this priority**: Theme support is a baseline expectation for modern applications. If the migration breaks dark mode, users in that cohort have a degraded experience.

**Independent Test**: Toggle between light and dark system preferences. Verify every page renders with the correct color scheme and meets WCAG AA contrast ratios.

**Acceptance Scenarios**:

1. **Given** the user's system preference is set to dark mode, **When** they load the application, **Then** all backgrounds, text, borders, and accents use the dark theme palette.
2. **Given** the user switches from light to dark mode while the application is open, **When** the preference change is detected, **Then** the application transitions to the dark theme without a page reload.
3. **Given** the application is in dark mode, **When** a user reads conversation content, **Then** all text meets WCAG AA contrast requirements (4.5:1 for normal text, 3:1 for large text).

---

### User Story 6 — Build Size and Performance Maintained or Improved (Priority: P3)

A developer compares the production CSS bundle size and page load metrics before and after the migration. The new CSS output is equal to or smaller than the Tailwind-generated output, and no page loads slower than the pre-migration baseline.

**Why this priority**: The refactor must not introduce a performance penalty. Users should not pay a cost for an internal architectural improvement.

**Independent Test**: Measure the production CSS bundle size and run Lighthouse on the three most-visited pages. Compare against pre-migration baselines.

**Acceptance Scenarios**:

1. **Given** the migration is complete, **When** a developer builds for production, **Then** the total CSS output is no larger than the pre-migration Tailwind CSS output.
2. **Given** the migration is complete, **When** a user loads the conversation list page on a standard connection, **Then** the page reaches interactive state within the same time threshold as the pre-migration version.

---

### Edge Cases

- What happens when a third-party dependency injects its own Tailwind-style classes? Styles must not conflict with or be overridden by the new global CSS.
- How does the system handle extremely long conversation threads (1000+ messages) — does the CSS refactor introduce any layout performance regressions with deeply nested selectors?
- What happens when a user has browser-level font size overrides or zoom levels between 75% and 200%? All layouts must remain functional.
- How does the system behave when CSS custom properties are not supported (very old browsers)? Graceful degradation or a clear minimum browser requirement must be established.

## Requirements *(mandatory)*

Requirements in this section MUST be stated in testable terms and MUST avoid hidden
implementation work that crosses architecture boundaries without naming them explicitly.

### Functional Requirements

- **FR-001**: The application MUST render all existing pages and components with no visual regressions compared to the pre-migration baseline.
- **FR-002**: The application MUST NOT include Tailwind CSS, its PostCSS plugin, `tailwind-merge`, or any Tailwind-related packages in its dependency tree after migration.
- **FR-003**: The application MUST NOT contain any Tailwind utility class names in component source files after migration.
- **FR-004**: All design tokens (colors, spacing, typography, border radii, shadows, transitions) MUST be defined as CSS custom properties and referenced from a single source of truth.
- **FR-005**: All component styles MUST be expressed in CSS files (global stylesheet, CSS modules, or scoped style blocks) rather than as utility class strings in markup.
- **FR-006**: All responsive layouts MUST use standard CSS media queries or container queries.
- **FR-007**: All shared UI primitives (buttons, dialogs, dropdowns, tabs, inputs, badges, scroll areas, selects, checkboxes, cards, progress bars, skeletons, separators, popovers, calendars, alert dialogs, toasts) MUST preserve their current keyboard navigation, focus management, and ARIA attributes.
- **FR-008**: Dark mode MUST continue to function using CSS custom properties and the `prefers-color-scheme` media query (or an equivalent user-preference mechanism).
- **FR-009**: All existing hover, focus, active, and disabled visual states MUST be preserved for interactive elements.
- **FR-010**: The production build MUST succeed without Tailwind tooling in the build pipeline.
- **FR-011**: Shared UI primitives MUST both retain a `className` prop for one-off class-based overrides AND expose documented CSS custom properties for variant-level theming, providing maximum flexibility for consumers of those components.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of pages pass visual regression tests comparing pre- and post-migration screenshots with a pixel-difference threshold below 1%.
- **SC-002**: Zero Tailwind-related packages remain in the project dependency manifest.
- **SC-003**: Zero Tailwind utility class names appear in any component source file.
- **SC-004**: All 17 shared UI primitives pass their existing interaction and accessibility tests with no modifications to test assertions.
- **SC-005**: Production CSS bundle size is equal to or smaller than the pre-migration Tailwind CSS output.
- **SC-006**: Lighthouse Performance score on the three primary pages (conversation list, conversation detail, search) is equal to or higher than pre-migration baselines.
- **SC-007**: All WCAG AA contrast requirements are met in both light and dark themes.

## Assumptions

- The refactor is limited to the frontend layer (`web/`). No backend, API, or core library changes are needed.
- The Radix UI primitives underlying the current shadcn/ui components will be retained for their accessibility behavior; only their styling layer is being replaced.
- The existing visual design (colors, spacing, typography, layout structure) is the target — this refactor does not introduce a visual redesign.
- CSS Modules or a well-structured global stylesheet will provide component scoping. The specific CSS architecture will be determined during planning.
- Modern browser support is assumed (browsers supporting CSS nesting, `:has()`, custom properties, container queries). A minimum browser version will be documented during planning.
- The migration can proceed component-by-component, allowing incremental delivery rather than a single all-or-nothing switchover.

## Implementation Guardrails

- Capture full-page visual regression screenshots of every major view before any migration work begins. The first failing check should verify that no Tailwind classes appear in a migrated component while visual parity is maintained.
- The refactor MUST stay within the `web/` layer. No changes to `chatgpt_archive/`, `api/`, `tests/`, or `docker/` are permitted.
- Out of scope: visual redesign, new features, new pages, changes to component behavior or data flow, addition of CSS-in-JS libraries, changes to the build toolchain beyond removing Tailwind.
