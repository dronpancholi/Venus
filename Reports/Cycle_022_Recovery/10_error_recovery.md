# Error Recovery Audit

## Before
Raw Python tracebacks printed to console on any failure.

## After
All command handlers wrapped in try/except in `genesis/__main__.py`:

```python
try:
    # ... dispatch to command handler ...
except (ImportError, ModuleNotFoundError) as e:
    _handle_error(e, command)
except KeyboardInterrupt:
    print("\nInterrupted.")
    sys.exit(130)
except Exception as e:
    if "--debug" in args or os.environ.get("GENESIS_DEBUG"):
        raise  # Developer mode: show full traceback
    _handle_error(e, command)
```

## Error Format

```
Error running 'genesis <command>':
  <ErrorType>: <message>

Suggested fix: <actionable advice>
```

## Error Types Handled

| Error | Message | Suggested Fix |
|---|---|---|
| ImportError | Missing module | `pip install 'genesis[group]'` |
| FileNotFoundError | Path doesn't exist | Check path |
| PermissionError | Access denied | Check permissions |
| ConnectionError | Service unavailable | Check service |
| KeyboardInterrupt | User pressed Ctrl+C | Clean exit |
| Generic Exception | Any other error | Run `genesis doctor` |

## Developer Mode

```
genesis --debug <command>
# or
GENESIS_DEBUG=1 genesis <command>
```

Shows full Python traceback instead of human-readable error.

## Diagnostics

`genesis doctor` runs 8 checks and provides actionable output for
common issues. All checks handle their own errors gracefully.

## Known Gaps

- Startup error from within textual (Desktop) is caught by textual
  framework, not by Genesis error handler
- Web server errors during uvicorn.run() are caught by uvicorn,
  not by Genesis error handler
