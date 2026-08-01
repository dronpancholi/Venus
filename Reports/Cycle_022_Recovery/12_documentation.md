# Documentation Audit

## Existing Documentation

| File | Status | Notes |
|---|---|---|
| `README.md` | ✓ Updated | Accurate install + usage docs based on verified functionality |

## Documentation Accuracy

Every claim in README.md has been verified:

- **Install commands** — tested on clean venv ✓
- **Commands table** — all 14 commands verified ✓
- **Modes section** — Desktop, Web, Terminal, Dev all verified ✓
- **First run flow** — tested with config deletion ✓
- **Workspace structure** — matches actual auto-created layout ✓
- **Configuration** — config stored at `~/.genesis/config.json` ✓
- **Architecture layers** — matches actual modules ✓
- **Troubleshooting** — `genesis doctor` verified ✓
- **Extras** — `[server]`, `[watch]`, `[all]` all tested ✓

## What Documentation Does NOT Claim (correctly)

- Does NOT claim there's a web frontend (there isn't)
- Does NOT claim import builds Digital Twin (it doesn't)
- Does NOT claim AI provider auto-connects (it's optional)
- Does NOT claim desktop works without TTY (it requires one)
- Does NOT claim macOS/Windows/Docker packaging (it doesn't exist)

## Documentation Principles

- Only document functionality that has been verified to work
- Mark optional features clearly
- Include troubleshooting section with `genesis doctor`
- Include known limitations
