# Workspace Validation

## Directory Structure

Auto-created at `~/Genesis/` (configurable) with 11 subdirectories:

```
~/Genesis/
  Projects/       — Imported repository metadata
  Knowledge/      — File catalogs (catalog.json)
  Memory/         — (empty — future use)
  Reports/        — (empty — future use)
  Logs/           — (empty — future use)
  Settings/       — workspace_state.json
  Applications/   — (empty — future use)
  Cache/          — (empty — future use)
  Plugins/        — (empty — future use)
  Backups/        — (empty — future use)
  Exports/        — (empty — future use)
```

## Verification

```
$ genesis workspace
✓ All 11 directories exist
✓ Project 31A visible in workspace
✓ Settings/workspace_state.json contains pinned + recent entries
```

## Workspace State Persistence

File: `~/Genesis/Settings/workspace_state.json`
```json
{
  "pinned": ["Project 31A"],
  "recent": ["/Users/dronpancholi/Developer/01_Strategic/Project 31A"]
}
```

## Config File

Location: `~/.genesis/config.json`

Contents: All PlatformConfig fields (workspace_path, ai_provider, theme,
desktop preferences, etc.)

## Workspace Commands

| Command | Effect |
|---|---|
| `genesis workspace` | Show workspace status, open Finder (macOS) |
| `genesis config` | Show full configuration |
| `genesis setup` | Re-run setup wizard (overwrites workspace) |
