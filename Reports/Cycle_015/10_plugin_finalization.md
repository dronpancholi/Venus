# Cycle 015 — Plugin Ecosystem Finalization (M107)

## Consolidation Decision

3 competing plugin systems → **1 canonical: PluginManager** (`genesis/plugin/manager.py`)

| System | Fate | Rationale |
|--------|------|-----------|
| `plugin/manager.py` | ✅ Canonical | Full lifecycle, manifests, hooks, deps, hot-reload, sandbox |
| `kernel/plugin_loader.py` | 🔜 Deprecate | Primitive — module discovery only |
| `plugin/registry.py` | ✅ Keep | Different purpose — lightweight engine registry for OmegaLoop |

## PluginManager Capabilities

| Feature | Status | Details |
|---------|--------|---------|
| Manifest-driven | ✅ | YAML/JSON: name, version, entry_point, dependencies, hooks, commands |
| Lifecycle | ✅ | registered → loaded → active → inactive |
| Dependency resolution | ✅ | Recursive with optional deps |
| Hook system | ✅ | 4 types: runtime, validation, memory, compiler |
| Hot-reload | ✅ | `hot_reload(name)` — deactivate, rescan, reload, reactivate |
| Sandbox | ⚠️ | Module whitelist exists but not enforced at Python level |
| EventBus integration | ✅ | Emits plugin.registered, plugin.activated, plugin.deactivated |
| Validation | ✅ | Manifest field validation via PluginManifest |
| Discovery | ✅ | Directory scanning for *.yaml and *.json manifests |

## Desktop Integration Gap

**Current state:** PluginManager is completely disconnected from the desktop.

**Required for M90 (Plugin Platform 2.0):**
1. New hook types: `desktop.screen`, `desktop.widget`, `desktop.command`, `desktop.keybinding`
2. PluginManagerScreen: list/install/activate/deactivate/configure plugins
3. CommandPalette integration: plugins register commands via manifest
4. Screen registry integration: plugins register screens dynamically
5. Example plugin: demo the full API

## SDK Requirements

| Component | Priority | Description |
|-----------|----------|-------------|
| Plugin SDK package | P1 | `genesis.plugin.sdk` — base classes + decorators |
| Plugin generator | P2 | Cookiecutter template for new plugins |
| Plugin validator | P1 | Validate manifest + entry point before installation |
| Plugin debugger | P2 | Runtime inspection of active plugins |
| Documentation | P1 | Plugin developer guide with examples |
| Marketplace schema | P3 | JSON schema for plugin distribution |

## API Stability Guarantee

Once M90 ships, the Plugin API must remain backward-compatible for 3+ cycles:
- `PluginManager` public methods are stable
- `PluginManifest` schema is versioned
- Hook signatures are frozen
- Plugin base class interface is frozen
