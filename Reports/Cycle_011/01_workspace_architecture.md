# CYCLE 011 — WORKSPACE ARCHITECTURE REPORT

## From Monolithic File to Multi-File Package

---

## REFACTORING DECISION

### Before
`genesis/desktop.py` — 750-line monolith containing:
- 6 widget classes
- 6 screen classes  
- 1 application class
- All CSS (700+ lines of it)
- Command palette logic
- Event polling logic

This file had grown to the point where any change risked breaking unrelated screens. Adding new screens required scrolling through hundreds of lines.

### After
```
genesis/desktop/
├── __init__.py      (18 lines)   — Public API: GenesisDesktop, run_desktop
├── app.py           (210 lines)  — Application class + CSS + bindings
├── widgets.py       (220 lines)  — Shared widgets (StatusBar, EventLog, etc.)
├── screens.py       (540 lines)  — All 10 screens with data connections
└── palette.py       (280 lines)  — CommandPalette + SearchEverywhere
```

Total: ~1,270 lines (vs 750), but with clear separation of concerns.

### Why a Package Instead of a File
1. **Discoverability** — each file has a single purpose
2. **Isolation** — widget changes don't risk breaking screens
3. **Testability** — widgets, screens, and palette can be tested independently
4. **Scalability** — adding a new screen means adding one method, not scrolling through 750 lines
5. **Import hygiene** — no circular imports between screens and widgets

## FILE RESPONSIBILITIES

| File | Responsibility |
|------|---------------|
| `__init__.py` | Public API surface — exactly what `__main__.py` needs |
| `app.py` | Wire everything together: screen registry, keyboard bindings, workspace CSS, app lifecycle |
| `widgets.py` | Pure presentational widgets with polling logic — no screen-level logic |
| `screens.py` | Screen composition — which widgets to show, how to arrange them |
| `palette.py` | Modal screens — command execution, search results, keyboard-first UX |

## CSS ARCHITECTURE

The CSS is in `app.py` as a single string (`WORKSPACE_CSS`). This was kept together because:
- Textual's CSS is app-level, not file-level
- Splitting CSS across files would require a CSS loader
- The CSS is ~200 lines, manageable as a single block

## BACKWARD COMPATIBILITY

The old `genesis.desktop` module was a single file. The new one is a package. Both expose:
```python
from genesis.desktop import GenesisDesktop
from genesis.desktop import run_desktop
```

The old `genesis/desktop.py` was deleted after verifying all imports resolve correctly.
