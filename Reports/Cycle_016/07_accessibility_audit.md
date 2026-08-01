# Cycle 016 — Accessibility Audit

## Color Usage

Color is used as the **sole differentiator** in multiple places:

| Widget | Colors | Differentiation |
|--------|--------|-----------------|
| Agent status indicator | `green`/`yellow`/`red`/`blue` | Color only |
| Event severity | `green`/`yellow`/`red`/`magenta`/`cyan` | Color only |
| Task status | `green`/`yellow`/`red`/`blue`/`dim` | Color only |
| Connection status | `green`/`red`/`yellow`/`dim` | Color only |

**No text labels accompany any color code.** A color-blind user cannot distinguish critical errors from informational events.

## Terminal Requirements

| Requirement | Current | Notes |
|-------------|---------|-------|
| True color | Required | `#rrggbb` hex codes used throughout |
| Unicode | Required | Emoji, arrows, special chars used |
| Min width | ~120 chars | Column layouts break below |
| Min height | ~40 lines | Most screens scroll below |

**No grace mode** for terminals that don't support true color or unicode.

## Keyboard Navigation

### Strengths
- 13 keyboard bindings mapped
- Command Palette (ctrl+k) for screen switching
- Search Everywhere (ctrl+p) for data search
- Filters focusable via `/` key
- Escape consistently closes modals

### Weaknesses
- No keyboard shortcut reference screen
- Settings has only 1 binding (Escape)
- No tab-order navigation between widgets
- No `?` key to show help
- `navigate_to` crash on Escape after navigation

## Screen Reader Support

- Textual has built-in screen reader support but it is not leveraged
- No ARIA labels on any widget
- No semantic roles (navigation, main, complementary)
- DataPanel has no accessible description
- Status changes (agent paused, task completed) not announced to screen reader
- No `data-` attributes for assistive technology

## Contrast & Readability

| Element | Contrast | Notes |
|---------|----------|-------|
| Body text on dark bg | Good | White `#ffffff` on dark `#1e1e1e` |
| Dim text (`[dim]`) | Poor | `#666666` on `#1e1e1e` = low contrast |
| Status colors | Varies | Green on dark = readable, Yellow on dark = poor |
| Headers | Good | Bold white on dark |
| Links | N/A | No clickable links in UI |

## Motor Accessibility

- All actions are keyboard-accessible (no click-required paths)
- No double-click or long-press required
- No drag-and-drop interactions exist
- 30-second auto-refresh destroys scroll position — problematic for users who read slowly

## Accessibility Score: 2/10

| Dimension | Score | Key Issues |
|-----------|-------|------------|
| Color Usage | 1/10 | Color-only differentiation throughout |
| Terminal Compat | 4/10 | Requires true color + unicode, no fallback |
| Keyboard Nav | 5/10 | Good coverage but no help screen, Settings broken |
| Screen Readers | 1/10 | Not leveraged at all |
| Contrast | 5/10 | Dim text is hard to read |
| Motor | 6/10 | Keyboard accessible, but scroll destroy is problematic |
