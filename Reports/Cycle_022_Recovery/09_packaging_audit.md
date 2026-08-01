# Packaging Audit

## Entry Points

```toml
[project.scripts]
genesis = "genesis.__main__:main"
genesis-desktop = "genesis.__main__:main"
genesis-server = "genesis.__main__:main"
genesis-terminal = "genesis.__main__:main"
genesis-doctor = "genesis.__main__:main"

[project.gui-scripts]
genesis-desktop = "genesis.__main__:main"
```

All 5 console scripts route through the same `main()` function, which
dispatches based on `sys.argv[0]` or `sys.argv[1:]`.

## Path Audit

| Concern | Status |
|---|---|
| Hardcoded absolute paths in code | None found |
| Relative paths for assets | Desktop uses textual built-in assets |
| Configuration path | `~/.genesis/config.json` (portable, no hardcode) |
| Workspace path | `~/Genesis` default, configurable via setup |

## Future Packaging Targets

| Target | Prerequisites | Status |
|---|---|---|
| macOS .app | py2app or briefcase | Not started |
| Windows .exe | PyInstaller | Not started |
| Linux AppImage | linuxdeploy + python | Not started |
| Docker | Dockerfile with pip install | Not started |
| Homebrew | Formula with python dependency | Not started |
| pip (current) | pyproject.toml | ✓ Working |

## What's Missing for Packaging

- No application icon (`icon.png`, `icon.ico`)
- No desktop entry file (`.desktop` for Linux)
- No Info.plist (for macOS .app)
- No build scripts for any packaging format
- No version pinning in dependencies (uses `>=` ranges)
