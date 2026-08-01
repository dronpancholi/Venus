# Cycle 016 — Visual Audit

## Theme & Styling

### Current CSS (app.py WORKSPACE_CSS, ~300 lines inline)
- Dark theme: `$surface: #1e1e1e`, `$text: #ffffff`
- Consistent accent colors: `#4ec9b0` (teal), `#569cd6` (blue), `#ce9178` (orange)
- Good use of `#region` CSS annotations for organization
- Tree widget styling, DataTable styling, ScrollableContainer styling

### Problems
1. **CSS is inline in app.py** — a 300+ line raw string. Cannot be hot-reloaded. Cannot be shared. No syntax highlighting in editor.
2. **No light theme** — dark-only. No `@media (prefers-color-scheme: light)` support.
3. **No theme customization** — all colors are hardcoded. Users cannot customize.
4. **No focus indicators for keyboard navigation** — focused elements don't have visible outlines or highlights beyond default cursor.
5. **DataPanel widget has no borders or visual grouping** — panels blend together; hard to distinguish data regions at a glance.

## Screen Visual Quality

| Screen | Visual Score | Issues |
|--------|-------------|--------|
| Command Center | 6/10 | Clean 3-column layout, but dense with no breathing room |
| Inspector | 7/10 | Three views with color-coded events, clean metrics |
| Agent Collaboration | 5/10 | Text tree "graph", no visual hierarchy |
| Memory Explorer | 6/10 | Two-column nav + detail, filter input, clean |
| Timeline | 5/10 | Single-column, identical to Memory Explorer, bland |
| Knowledge Graph | 3/10 | "Graph 2.0" that is text-only — most visually disappointing screen |
| Repository | 5/10 | Tree widget + text panels, hardcoded architecture text |
| AI Orchestration | 4/10 | Broken provider list, hardcoded router text |
| CE | 6/10 | Clean watcher status, live event log |
| Reports | 5/10 | Tree navigation, truncated content, no search |
| Settings | 3/10 | Read-only panels, dead-end AI text, no visual interest |

## Layout & Spacing

### Strengths
- Consistent column percentages across screens
- Header with title + subtitle pattern
- Footer divider with timestamp markers

### Weaknesses
- No consistent margin/padding. Some screens use `padding: 1`, others hardcode margins
- No responsive layout — fixed column widths break on terminal resize
- No visual separation between DataPanel widgets — they blend into a wall of text
- No icon support (Textual doesn't support icons natively; text-based icons are inconsistent)

## Typography

- Body text: default terminal font (monospace)
- Headers: `bold` weight only
- Subtitle: `dim` style
- No hierarchy beyond bold/dim
- No variable-width font support for headers
- Long lines (120+ chars) are truncated without indication

## Score: 5/10

| Dimension | Score | Key Issues |
|-----------|-------|------------|
| Theme & Styling | 5/10 | Inline CSS, dark-only, no customization |
| Screen Consistency | 4/10 | Knowledge Graph and Settings are visually broken |
| Layout | 5/10 | No responsiveness, no margins, blending panels |
| Typography | 4/10 | Only bold/dim, monospace only, no hierarchy |
