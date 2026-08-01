# CYCLE 011 — DESIGN DECISIONS REPORT

---

## 1. Screen-Based Navigation vs Tabbed Layout

**Decision:** Use Textual's `push_screen` / `pop_screen` navigation instead of building a custom TabBar.

**Rationale:** Textual's Screen API provides:
- Automatic keyboard focus management
- Built-in animation (if desired)
- Escape-to-back behavior
- Clean `SCREENS` dict registry
- No need to manage tab state manually

The Activity Bar on the left serves as a visual navigation panel, with keyboard shortcuts (Ctrl+1-3) for fast switching.

**Trade-off:** No drag-to-reorder or split views yet. These can be added in a future cycle using Textual's `TabbedContent` within individual screens.

---

## 2. One App Class, Many Screen Classes

**Decision:** GenesisDesktop remains the single App, with each mission as a Screen subclass.

**Rationale:** 
- Screens are lazy-loaded from the `SCREENS` dict
- Each screen manages its own polling intervals
- Shared widgets live in `widgets.py` for reuse
- No complex state sharing needed — all read from FabricKernel singleton

---

## 3. FabricKernel Singleton for State

**Decision:** All screens read real-time data from `FabricKernel.instance()` rather than maintaining local state.

**Rationale:**
- Single source of truth for all system state
- Screens are stateless (just display logic)
- Polling intervals on each screen refresh independently
- No need for a separate state management layer

**Trade-off:** Implicit coupling to the kernel. If the kernel structure changes, all screens must be updated.

---

## 4. Package Structure Instead of Monolith

**Decision:** Split into 5 files by concern.

**Rationale:** (Detailed in workspace architecture report). The 750-line monolith was approaching maintainability limits.

---

## 5. Command Palette as ModalScreen

**Decision:** CommandPalette and SearchEverywhere are both `ModalScreen` subclasses.

**Rationale:**
- Modal screens overlay the current content without disrupting state
- User presses Escape to dismiss (standard UX pattern)
- Textual provides `push_screen`/`pop_screen` for modal behavior
- No need to save/restore screen state

---

## 6. Keyboard-First Navigation

**Decision:** Every screen and modal has keyboard bindings; mouse is secondary.

**Rationale:**
- Terminal users expect keyboard navigation
- Ctrl+K for commands, Ctrl+P for search (VS Code muscle memory)
- Nested key bindings (E/A/C/T for timeline views, P/S/T for agent ops)
- Escape always goes back

---

## 7. Error Resilience

**Decision:** Every screen wraps fabric data access in try/except.

**Rationale:**
- The kernel might not be fully booted when a screen mounts
- Background threads may fail silently
- Storage might not be connected
- Better to show "[dim]Data not available[/]" than crash the TUI
- `self.app.notify()` for actionable errors

---

## 8. Polling vs Event-Driven

**Decision:** Use polling intervals (1-10s) instead of event-driven push.

**Rationale:**
- Simpler to implement across all screens
- Textual handles `set_interval` cleanly
- The kernel's event system is async; polling is synchronous
- Future cycle: wire WebSocket-based push for true real-time updates
