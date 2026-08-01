# CYCLE 008 — MIGRATION REPORT

## Upgrading from Cycle 007

⸻

## Breaking Changes

**None.** All Cycle 007 APIs are backward compatible.

## New APIs

| API | Type | Stabilization |
|-----|------|---------------|
| `genesis.watch.start()` | Stable | Iterate in Cycle 009 |
| `genesis.watch.stop()` | Stable | Iterate in Cycle 009 |
| `genesis.watch.status()` | Stable | Iterate in Cycle 009 |
| `GenesisAPI(host, port)` | Alpha | May change to config object |
| `GenesisDesktop()` | Alpha | Screens may be restructured |

## Deprecations

None.

## Migration Path

```bash
# Before (Cycle 007):
python -m genesis

# After (Cycle 008):
python -m genesis desktop
```

## Backward Compatibility

- `genesis.__main__` still runs CLI when no arguments given
- All Fabric v2 APIs unchanged
- All AI provider APIs unchanged
- All MCP APIs unchanged

## Upgrade Checklist

- [x] Backward compatibility verified (3225 tests)
- [x] No breaking changes
- [x] New modules in correct layers
- [x] Architecture tests pass
- [x] All existing tests pass
