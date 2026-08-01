# Cycle 016 — Genesis SDK Design (M118)

## Current State
Plugin system exists (`PluginManager`, `PluginManifest`, `Sandbox`) but:
- No plugin CLI (`genesis plugin create`)
- No plugin templates
- No example plugins
- Sandbox not enforced (`validate_module` never called)
- No documentation or developer guide
- No SDK package (`genesis/sdk/`)

## Target SDK Package Structure
```
genesis/sdk/
├── __init__.py          # GenesisPlugin base class, create_plugin()
├── types.py             # PluginManifest, PluginHook, PluginConfig
├── api.py               # GenesisAPI client (HTTP + WS)
├── templates/           # Plugin/template/workflow templates
│   ├── plugin/          # Plugin template
│   ├── theme/           # Theme template
│   ├── widget/          # Widget template
│   ├── screen/          # Screen template
│   └── provider/        # AI provider template
└── cli/                 # CLI commands
    └── commands.py      # genesis plugin create <name>
```

## Plugin Developer Workflow
```bash
genesis plugin create my-plugin
cd my-plugin
# Edit manifest.yaml + plugin.py
genesis plugin install .
genesis plugin activate my-plugin
```

## Key Design Decisions
- Plugin base class will be `GenesisPlugin` with `on_boot/on_event/on_shutdown` hooks
- Permissions declared in manifest, enforced by Sandbox
- Version resolution with semver (not yet implemented)
- Topological dependency sorting (not yet implemented)
- Circular dependency detection (not yet implemented)

## Deferred to Cycle 017
SDK extraction, CLI, templates, documentation, and sandbox enforcement.
