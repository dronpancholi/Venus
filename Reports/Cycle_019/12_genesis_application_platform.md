# M156 — Genesis Application Platform

## File
`genesis/app_platform/engine.py`, `genesis/app_platform/__init__.py`

## Purpose
Genesis as a platform capable of hosting applications. Applications use Engineering Objects, Knowledge, Timeline, Memory, AI, Search, Projects, Workspace, Events, Plugins, Automation, Fabric, Desktop, and Agent Runtime without rebuilding infrastructure.

## Key Components

### AppManifest
- `name`, `description`, `version`, `author`, `dependencies`, `permissions`, `entry_points`

### GenesisApp
- `manifest`, `status` (registered/running/stopped), `started_at`, `health`

### GenesisAppPlatform
- `register(manifest)` — register an app
- `start(name)` / `stop(name)` — lifecycle management
- `get(name)`, `list()`, `stats()`

### Built-in Apps
1. **buildit** — Engineering build system
2. **venus** — Strategic engineering platform
3. **architecture_studio** — Design and visualize architecture
4. **deployment_studio** — Manage deployments
5. **documentation_studio** — Auto-generate documentation
6. **agentos** — Agent Operating System v2.0.0

## Integration
- **kernel.app_platform** — lazy-loaded, auto-booted
- **EngineeringState** — stores app count
- **EngineeringRegistry** — apps registered as APP_MODULE objects
- **Events** — emits app.registered, app.started
