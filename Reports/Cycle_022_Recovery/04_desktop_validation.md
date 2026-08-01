# Desktop Validation

## Verified

- `GenesisDesktop` class imports successfully
- `run_desktop()` function executes
- `FabricKernel.instance().boot()` succeeds (all subsystems initialized)
- All 11 screen classes import successfully:
  - GenesisHome, FabricInspectorScreen, AgentCollaborationScreen
  - EngineeringMemoryExplorer, EngineeringTimelineScreen
  - KnowledgeGraphScreen, RepositoryScreen, AIOrchestrationCenter
  - ContinuousEngineeringScreen, ReportsScreen, SettingsScreen
- All 5 experience screens import:
  - UnderstandProject, ReviewArchitecture, ContinueWork
  - InvestigateProblem, ImproveRepository
- Command palette: CommandPalette, SearchEverywhere
- Activity system: ActivityCenter, Notification, ActivityCenterScreen
- WorkspaceMemory, StatusBar

## Test Flow

The desktop boot sequence:
```
genesis
  → _ensure_config()            Load ~/.genesis/config.json
  → _auto_setup_if_needed()     First-run detection
  → FabricKernel.instance()     Kernel singleton
  → kernel.boot()               All subsystems
  → run_desktop()               GenesisDesktop (textual App).run()
```

## Limitation

Desktop requires a TTY for textual rendering. Cannot be verified in
headless/CI environments. Full rendering test requires a terminal
with `TERM` set (xterm-256color or similar).

Manual verification steps:
1. Open a terminal
2. Run `genesis`
3. Desktop should appear with:
   - Experience navigation bar (Understand, Architecture, Continue, Investigate, Improve)
   - Home screen with project list
   - Status bar at bottom
   - Command palette accessible via Ctrl+P
