# Cycle 016 — UX Audit

## First-Run Experience

**Problem: Blank screen at startup.**
On first launch, the user sees a dark terminal with zero content for up to 30 seconds (the first timer interval). There is no splash screen, no loading indicator, no "booting kernel..." message, no onboarding prompt.

**Problem: No guided onboarding.**
After the first render, the user sees a dense information dashboard with no explanation of what anything means. There is no welcome screen, no tutorial, no tooltip system.

**Problem: No sample data.**
If no agents, events, or conversations exist yet, every screen shows "[dim]No data available[/]" or similar empty states. There is no "Add your first agent" or "Run genesis demo" prompt.

## Navigation

**Problem: Back navigation crashes or shows blank screen.**
The core `navigate_to` method pops the current screen before pushing the new one. When the user presses Escape, the app pops the (only) remaining screen, leaving an empty stack. This is a showstopper bug that will crash or blank the app on any Escape press after navigation.

**Problem: No breadcrumb or navigation history.**
Users cannot see where they are in the screen hierarchy. No "Home > Agents > Agent Detail" trail. No way to go back to the previous screen without remembering which screen that was.

**Problem: Screen switching destroys context.**
Every `navigate_to` call pops and pushes screens. The old screen is destroyed. All scroll position, selection state, and data are lost. There is no state persistence across navigations.

## Data Freshness

**Problem: All screens poll on a 30-second timer.**
Data refreshes are timer-driven, not event-driven. The event subscription system exists but is secondary to polling. Users must wait up to 30 seconds to see new data.

**Problem: No manual refresh affordance on most screens.**
Only some screens implement `action_refresh`. Most screens require the user to wait for the next timer tick.

**Problem: No "last updated" timestamp.**
Users cannot tell how stale the data on screen is. No "last updated 3s ago" indicator on any widget.

## Interactivity

**Problem: Clickable elements don't look clickable.**
The AI provider list looks like a list but doesn't respond to clicks (P0-6). Agent names in the collaboration screen can be clicked to see details, but there is no visual affordance (cursor change, hover highlight).

**Problem: No confirmation for destructive actions.**
Terminate agent (one keystroke) and Ctrl+Q quit have no confirmation dialog. Critical operations happen instantly with no undo.

**Problem: Action feedback is inconsistent.**
Some actions show a notification ("Agent paused"), others complete silently. Notifications appear in the bottom-right and auto-dismiss in 5 seconds — easy to miss.

## Information Architecture

**Problem: Screen naming is inconsistent.**
- "Engineering Command Center" → actually a dashboard
- "Fabric Inspector" → actually event/metric/session viewer
- "Knowledge Graph 2.0" → no graph visualization
- "Settings" → read-only system info

**Problem: Settings is a misnomer.**
Users naturally expect to configure Genesis from a "Settings" screen. Instead it shows read-only information with a dead-end AI Providers panel that says "check AI Command Center."

**Problem: Timeline vs Memory Explorer confusion.**
TimelineScreen (80% code-duplicated from MemoryExplorer) shows Events, Audit, Conversations, Tasks — the same first 4 views in MemoryExplorer. Users will be confused about which screen to use.

## Keyboard UX

**Problem: No visible keyboard shortcut help.**
The `/` key focuses the filter input, `?` is not bound to show help. New users have no way to discover keyboard shortcuts except reading source code or the (non-existent) help screen.

**Problem: Inconsistencies in key bindings.**
- `M` in Inspector shows Metrics, but `P` in Agents shows delegation (not Pause)
- `[R]eports` in subtitle but binding uses `p` (memory screen)
- Tab mentioned in SearchEverywhere footer but not bound

**Problem: No keyboard navigation on Settings screen.**
Settings has only one binding (Escape). The user cannot navigate to individual setting groups with the keyboard.

## Visual Feedback

**Problem: No loading states.**
Every screen has zero loading indicators. On first render, widgets are empty until the first timer-driven refresh. During data fetches, the UI does not indicate activity.

**Problem: Error messages are generic.**
When data fetch fails, users see "[dim]No events available[/]" whether the cause is "no events exist" or "database is disconnected" or "kernel is not booted."

**Problem: "All systems normal" is misleading.**
The Command Center's AttentionWidget shows "All systems normal" when no agents/tasks are in error — but the rest of the system could be on fire.

## Empty States

**Problem: No actionable empty states.**
Empty states say "No agents registered" or "No events available" but never suggest what the user should DO next. There's no "Add an agent" button, no "Run a task to generate events" prompt.

**Problem: Reports directory assumed to exist.**
ReportsScreen gracefully handles a missing Reports directory, but MemoryExplorer's Reports view does not — it crashes with a filesystem error.

## Mobile/Resize

**Problem: No responsive layout.**
All screens use CSS grid/columns with fixed percentages. Resizing the terminal to a narrow width will likely break layouts. Minimum terminal size is not documented.

**Problem: No scroll indicators.**
DataPanel widgets with overflow content do not show visual scroll indicators. Users must try to scroll to discover hidden content.

## Accessibility

**Problem: No color-blind friendly mode.**
Color is used as the sole differentiator for agent status (green/yellow/red/blue), event severity (green/yellow/red/custom), and task status. No text labels or icons accompany color codes.

**Problem: Emoji usage without fallback.**
Reports view shows `📄` emoji which may not render in all terminals. No text fallback.

**Problem: No screen reader support.**
Textual's accessibility features are not leveraged. No ARIA labels, no semantic screen descriptions.

## UX Score: 4/10

| Dimension | Score | Key Issues |
|-----------|-------|------------|
| First Run | 2/10 | Blank screen, no onboarding, no sample data |
| Navigation | 3/10 | navigate_to crash, no breadcrumbs, context destroyed |
| Data Freshness | 4/10 | 30s poll, no event-driven priority, no staleness indicator |
| Interactivity | 3/10 | Non-functional lists, no confirmation, inconsistent feedback |
| Information Architecture | 5/10 | Misleading screen names, Settings misnomer, Timeline vs Memory |
| Keyboard UX | 6/10 | Good coverage but no discoverability, inconsistent bindings |
| Visual Feedback | 3/10 | No loading states, generic errors, misleading health indicators |
| Empty States | 2/10 | No action prompts, crash on missing directory |
| Responsiveness | 4/10 | Fixed layouts, no scroll indicators |
| Accessibility | 2/10 | Color-only differentiation, no screen reader support |
