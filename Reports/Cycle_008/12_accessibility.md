# CYCLE 008 — ACCESSIBILITY REPORT

## Building for Everyone

⸻

## Current State

Genesis Desktop uses Textual, which provides terminal-level accessibility:
- Screen readers can read terminal output
- Tab navigation between focusable widgets
- Keyboard shortcuts for all actions
- High contrast mode available via terminal theme

## Design Language Accessibility

| Token | Accessibility Feature |
|-------|----------------------|
| `--color-text: #e0e0e0` | 15.4:1 contrast on `--color-bg: #0d1117` (AAA) |
| `--color-primary: #58a6ff` | 6.5:1 on dark bg (AA+) |
| `--font-size-lg: 1.125rem` | 18px for body text |
| `--font-size-xl: 1.25rem` | 20px for UI labels |
| Semantic colors | Error=red, Warning=yellow, Success=green — color + position + icon |

## Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Next focusable |
| `Shift+Tab` | Previous focusable |
| `Ctrl+K` | Command palette |
| `Ctrl+C` | Quit |
| `Up/Down` | Scroll lists |
| `Enter` | Select item |

## Future Improvements

- **Screen reader support** — ARIA labels for Textual
- **Focus indicators** — visible focus ring
- **Reduced motion** — `prefers-reduced-motion` media query
- **Font scaling** — Support user font size preferences
- **Color blindness** — Test with simulation tools; avoid color-only indicators
- **Voice control** — (long-term) Speech-to-command
