# Cycle 006 — Genesis Design System

## Philosophy

The Genesis Design System is not a component library. It is a visual philosophy expressed
through code. Every visual decision must serve the engineering experience — reducing
cognitive load, revealing structure, and making the repository's state immediately
understandable.

## Design Principles

1. **Calm** — minimal visual noise. White space is a feature.
2. **Premium** — every pixel intentional. No rough edges.
3. **Intelligent** — surfaces what matters, not everything.
4. **Minimal** — default to simplest possible presentation.
5. **Fluid** — transitions are meaningful, not decorative.
6. **Fast** — 100ms response or show a progress indicator.
7. **Predictable** — consistent patterns everywhere.

## Visual Foundations

### Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-mono` | `'SF Mono', 'JetBrains Mono', 'Cascadia Code', monospace` | Code, data, metrics |
| `--font-sans` | `'Inter', -apple-system, 'SF Pro', sans-serif` | UI text, labels |
| `--font-size-xs` | 11px | Code annotations, timestamps |
| `--font-size-sm` | 13px | Body text, descriptions |
| `--font-size-base` | 14px | Default UI text |
| `--font-size-lg` | 16px | Section headers |
| `--font-size-xl` | 20px | Page titles |
| `--font-size-2xl` | 28px | Welcome screen headings |
| `--font-weight-normal` | 400 | Body text |
| `--font-weight-medium` | 500 | Buttons, active items |
| `--font-weight-semibold` | 600 | Headers, labels |
| `--font-weight-bold` | 700 | Page titles |
| `--line-height-tight` | 1.2 | Headings |
| `--line-height-normal` | 1.5 | Body text |

### Spacing Scale

| Token | Value |
|-------|-------|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 24px |
| `--space-6` | 32px |
| `--space-8` | 48px |
| `--space-10` | 64px |
| `--space-12` | 96px |

### Colors (Dark Mode Default)

```
--bg-primary:        #0A0A0B    (deepest background)
--bg-secondary:      #121214    (cards, panels)
--bg-tertiary:       #1C1C1F    (input fields, hover states)
--bg-elevated:       #252529    (dropdowns, modals)
--bg-glass:          rgba(18, 18, 20, 0.85)  (glass panels)

--text-primary:      #F5F5F7    (headings, primary content)
--text-secondary:    #A1A1AA    (body text)
--text-tertiary:     #63636E    (labels, hints)
--text-inverse:      #0A0A0B    (on colored backgrounds)

--accent-blue:       #5E9EFF
--accent-purple:     #A78BFA
--accent-green:      #4ADE80
--accent-orange:     #FB923C
--accent-red:        #F87171
--accent-cyan:       #67E8F9

--border-primary:    #27272A
--border-secondary:  #18181B
--border-focus:      #5E9EFF

--graph-node:        #5E9EFF
--graph-edge:        #27272A
--graph-highlight:   #A78BFA
```

### Light Mode

All same tokens, different values. Dark mode is primary (developers work at night).

### Motion Language

- **Duration-fast**: 150ms (hover, click feedback)
- **Duration-base**: 250ms (panel open, navigation)
- **Duration-slow**: 400ms (page transitions)
- **Easing**: `cubic-bezier(0.16, 1, 0.3, 1)` (custom ease-out)

All animations serve a purpose: direction, focus, state change.

## Component Hierarchy

### Atoms
- Typography — Text, Heading, Code, Mono
- Icon — SVG-based, 24 default size
- Badge — status, count, label
- Divider — horizontal, vertical
- Spacer

### Molecules
- Button — primary, secondary, ghost, danger; sizes sm/md/lg
- Input — text, search, number, password; with icon, error, hint
- Select — dropdown, multi-select, searchable
- Toggle — boolean switch
- Checkbox, Radio
- Slider
- Chip, Tag
- Tooltip
- Progress — linear, circular, step
- Skeleton — loading placeholder

### Organisms
- Card — panel with header, body, footer; interactive, draggable
- Table — sortable, filterable, resizable columns
- Tree — expandable, selectable, with icons
- Tabs — horizontal, vertical, pill
- Accordion
- Dialog — modal, sheet, alert
- CommandPalette — searchable action list
- Sidebar — collapsible, with sections
- TopBar — with breadcrumbs, actions, search
- Dock — macOS-style application dock
- ContextMenu
- Breadcrumbs
- Timeline — vertical event stream
- ActivityFeed — live-updating event list
- Console — terminal emulator
- GraphView — interactive knowledge graph visualization
- Chart — line, bar, area, pie

### Templates
- Home — dashboard with cards, activity, status
- Repository — file tree + content + metadata
- Architecture — layer graph + dependency view
- Knowledge — graph view + search + detail
- Memory — timeline + search + detail
- Agents — agent list + detail + conversation
- Tasks — kanban board + detail + timeline
- Governance — policy list + rule detail + audit log
- Settings — grouped sections, searchable

## Grid System

24-column grid. 8px base unit. Containers at 1024/1280/1440px breakpoints.

## Accessibility

- All components keyboard-navigable
- Focus indicators visible
- ARIA labels on interactive elements
- Minimum contrast ratio 4.5:1
- Respects `prefers-reduced-motion`
- Screen-reader-friendly semantic markup

## Implementation

The design system lives in `genesis/ui/` as pure CSS custom properties + vanilla
web components. No framework dependency — wrappers can be written for React, Vue,
Svelte, or desktop frameworks.

```
genesis/ui/
  tokens.css          — Design tokens
  reset.css           — CSS reset
  base.css            — Typography, spacing, grid
  components/         — Component CSS + light DOM HTML
  templates/          — Page layout templates
  icons/              — SVG icon library
  fonts/              — Font-face declarations
```
