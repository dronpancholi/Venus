# Design System

## Visual Identity
- **Theme**: Dark, minimal, Apple-inspired
- **Colors**: Genesis blue (#0c8ee7) accent, dark surfaces (#0a0a0a, #141414, #1a1a1a)
- **Typography**: System fonts (-apple-system, SF Pro, Helvetica Neue)
- **Corner radius**: 12px (cards), 8px (buttons), 6px (skeleton)
- **Borders**: 1px solid #1a1a1a/#232323

## Components
| Component | Description |
|-----------|-------------|
| Sidebar | Fixed 240px, collapsible, Navigator links with icons and shortcuts, ⌘K search trigger at bottom |
| StatusBar | 32px height, WebSocket status, health indicators, version |
| SearchDialog | Modal overlay (⌘K), debounced search, type icons, keyboard navigation |
| CopilotPanel | Slide-in from right (300px), chat messages, Send on Enter, engine status |
| StatCard | Small card with icon, label, value, hover elevation |
| Card | Bordered container with consistent padding |

## Animations
- Page transitions: `opacity 0→1, y: 10→0` (0.3s ease-out)
- Card hover: `y: -1` (0.15s ease)
- Search dialog: `scale: 0.95→1, opacity: 0→1` (0.15s ease)
- Copilot panel: spring slide from right (damping: 25, stiffness: 300)
- Sidebar: width animation (0.2s ease)

## Spacing
- Page padding: 24px (p-6)
- Card padding: 16px (p-4)
- Section gap: 24px (space-y-6)
- Grid gap: 12px (gap-3)
- List items: 8px/4px

## Responsive
- Grid layouts adapt: `grid-cols-1` → `grid-cols-2` → `grid-cols-3/4/6`
- Max content width: 1280px (max-w-7xl)
- Sidebar collapses to 0 width on mobile (not fully implemented)
