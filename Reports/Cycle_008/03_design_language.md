# CYCLE 008 — DESIGN LANGUAGE REPORT

## Genesis Visual Identity

**File:** `genesis/ui/tokens.css`

⸻

## Purpose

The Design Language codifies Genesis's visual identity in a single source of truth.
Every future UI component — whether Textual, Web, or Native — derives its appearance
from these tokens.

## Token Categories

| Category | Count | Examples |
|----------|-------|----------|
| Typography | 8 | `--font-sans`, `--font-mono`, `--font-size-*`, `--line-height-*` |
| Colors (Dark) | 16 | `--color-bg`, `--color-surface`, `--color-text`, `--color-primary`, `--color-success`, `--color-warning`, `--color-error`, `--color-accent` |
| Colors (Light) | 16 | Same structure, light theme values |
| Color Semantics | 8 | `--color-on-primary`, `--color-on-surface`, `--color-primary-hover`, `--color-surface-hover` |
| Spacing | 6 | `--space-{xs,sm,md,lg,xl,xxl}` |
| Elevation | 4 | `--elevation-{1,2,3,4}` |
| Radius | 4 | `--radius-{sm,md,lg,xl}` |
| Motion | 4 | `--motion-{fast,normal,slow,page}` |
| Glass | 3 | `--glass-bg`, `--glass-border`, `--glass-blur` |
| Component | 12 | `--panel-bg`, `--panel-border`, `--input-bg`, `--input-border`, `--button-primary-bg`, `--button-primary-text`, `--badge-*` |

## Design Principles

1. **Monochromatic + Accent** — Surfaces are neutral; accent color provides hierarchy
2. **Semantic colors** — Success, warning, error map to intent, not hue
3. **Glass morphism** — Panels use subtle transparency for depth
4. **Low elevation** — 4 levels of shadow for UI depth
5. **Fast motion** — 150ms default transitions; pages animate at 300ms

## Theme Strategy

- **Dark-first** — Dark theme is the default; light theme overrides
- **CSS custom properties** — Framework-agnostic; works in any context
- **Progressive enhancement** — Base values in `:root`; themes in `[data-theme]`
- **No preprocessor** — Pure CSS; no build step needed

## Usage

```css
/* In any component */
.panel {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    box-shadow: var(--elevation-1);
}
```

```css
/* Theme override */
[data-theme="light"] {
    --color-bg: #ffffff;
    --color-surface: #f5f5f5;
    --color-text: #1a1a2e;
}
```
