# M134 — Engineering Observatory

## File
`genesis/observatory/engine.py`, `genesis/observatory/__init__.py`

## Purpose
Historical engineering analytics and trend analysis. Records metric samples over time, computes trends (increasing/decreasing/stable), and provides snapshot reports.

## Key Components

### EngineeringObservatory
- `record(metric, value, label)` — stores a timestamped sample
- `trend(metric, window)` — computes trend over recent window: current, min, max, avg, direction, change percentage
- `snapshot()` — returns all metrics with trend analysis
- `auto_record()` — automatically records kernel stats (events, services, messages, executor)

### Trend Detection
- Compares first half vs second half of the sample window
- Change > 10% → "increasing"/"decreasing"
- Change within 10% → "stable"

## Integration
- **FabricKernel.observatory** — lazy-loaded, auto-booted
- **EngineeringRegistry** — registered as SERVICE object
- **AutomationEngine** — can trigger observatory recording on events
