# M171: Application Ecosystem

**Status:** Foundation exists in GenesisAppPlatform, extended with health/observability/graph awareness

## Existing Platform

The `GenesisAppPlatform` already supports:
- App lifecycle (registered → started → running → stopped)
- App manifests with name, description, version, author, dependencies, permissions
- Integration with state engine and engineering registry
- 6 built-in apps

## Cycle 020 Enhancements

Apps now have access to:
- `kernel.health_engine` — health-aware applications
- `kernel.observability` — auto-recorded app actions
- `kernel.graph.primary` — canonical graph for app data
- `kernel.boot_engine` — lifecycle-aware boot

## Next Steps

1. **App installation from files** — `genesis app install path/to/app.json`
2. **App marketplace** — catalog of installable applications
3. **Desktop integration** — app screens in desktop TUI
4. **AI integration** — apps can expose AI capabilities
5. **Permission system** — fine-grained app access control
