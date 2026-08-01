# Phase 0 Delta: Plugin Systems

**Files:** 3 competing systems across 6 source files, ~581 lines  
**Tests:** 0 (plugin-specific), ~5 tests in test_platform.py + test_kernel.py

## System 1: `genesis/plugin/` — Full Lifecycle (476 lines)

**Files:** `manager.py` (236), `manifest.py` (123), `registry.py` (110)

**Features:**
- Manifest-driven (YAML/JSON) — name, version, entry_point, dependencies, hooks, commands, capabilities, permissions
- Lifecycle: registered → loaded → active → inactive
- Recursive dependency resolution with optional flag support
- 4 typed hook categories: runtime, validation, memory, compiler
- Hot-reload: `hot_reload(name)` deactivates, re-scans, re-loads, re-activates
- Module whitelist sandboxing (not enforced at Python level)
- EventBus integration for lifecycle events

## System 2: `genesis/kernel/plugin_loader.py` — Module Discovery (105 lines)

- Generic module discovery via `importlib` + `pkgutil`
- Free-form string hook names (no typed categories)
- Tracks load history with timestamps
- No manifest, no dependencies, no sandbox, no hot-reload

## System 3: `genesis/plugin/registry.py` — Engine Registry (110 lines)

- Minimal name-to-instance map for engine decoupling
- Lazy instantiation via factory callables
- `get_by_type(type)` for category-based discovery
- `dependencies` field exists but is never used for resolution

## Desktop Integration Gaps

| Gap | Impact |
|-----|--------|
| No plugin management screen | Users can't list/install/activate plugins |
| No desktop hook types | Can't register screens, widgets, commands |
| No palette integration | Plugins can't add commands to `ctrl+k` |
| No UI extension API | No way to add sidebar items, status indicators |
| No installation flow | PackageManager doesn't invoke PluginManager |
| No semver resolution | Dependencies check existence, not version compat |
| No remote discovery | No plugin registry to browse |

## Findings

1. Three systems exist because each solved a specific problem — no consolidation effort was made
2. `PluginManager` is production-ready but completely disconnected from desktop
3. `ModulePluginRegistry` was created (per EDR-001) specifically to decouple OmegaLoop from 6+ engine imports
4. No plugin has ever been created — zero example plugins in the repo
5. Sandbox is purely documentary (whitelist checked but not enforced)

## Recommendations

1. Consolidate: deprecate `PluginLoader` + `ModulePluginRegistry`, keep `PluginManager`
2. Add desktop hook types: `desktop.screen`, `desktop.widget`, `desktop.command`, `desktop.keybinding`
3. Create `PluginManagerScreen` in desktop that wraps `PluginManager.to_dict()` + `validate_all()`
4. Extend `CommandPalette` to pull from registered plugin commands
5. Implement real sandbox using `subprocess` with restricted Python
6. Write an example plugin to validate the API before M90
