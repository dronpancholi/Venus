# CLI Validation

## Commands Verified

| Command | Status | Notes |
|---|---|---|
| `genesis` | ✓ | Launches Desktop (default) |
| `genesis desktop` | ✓ | Launches Desktop |
| `genesis studio` | ✓ | Shows Studio manifest |
| `genesis serve` | ✓ | Boots kernel + FastAPI |
| `genesis terminal` | ✓ | Engineering REPL |
| `genesis dev` | ✓ | Watchdog hot-reload mode |
| `genesis doctor` | ✓ | 8 diagnostic checks |
| `genesis status` | ✓ | Platform component status |
| `genesis config` | ✓ | Full config table |
| `genesis workspace` | ✓ | Shows/creates workspace |
| `genesis import <path>` | ✓ | Real indexing + catalog |
| `genesis setup` | ✓ | First-run wizard |
| `genesis version` | ✓ | Shows version |
| `genesis --help` | ✓ | Help text |

## Error Handling

### Before
Raw Python tracebacks on failure.

### After
Human-readable errors:
```
Error running 'genesis import':
  FileNotFoundError: /nonexistent does not exist

Suggested fix: Check that the path is correct.
```

Plus:
- `--debug` flag to show full tracebacks for developers
- `GENESIS_DEBUG=1` environment variable
- `KeyboardInterrupt` caught gracefully
- `ImportError` with specific install suggestion

## Exit Codes

| Scenario | Exit Code |
|---|---|
| Success | 0 |
| User error (unknown command) | 1 |
| Runtime error | 1 (with message) |
| KeyboardInterrupt (Ctrl+C) | 130 |

## Entry Points

All 5 entry points route through `genesis.__main__:main`:
- `genesis` (console_scripts)
- `genesis-desktop` (console_scripts)
- `genesis-server` (console_scripts)
- `genesis-terminal` (console_scripts)
- `genesis-doctor` (console_scripts)
- `genesis-desktop` (gui_scripts)
