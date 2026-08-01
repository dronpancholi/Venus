# Genesis — Engineering Computing Platform

A unified environment for understanding, building, and evolving software systems.

## Quick Start

```bash
git clone <repository>
cd genesis
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
genesis
```

On first run, Genesis will open a setup wizard to configure your
workspace and AI provider. After setup, the Desktop opens automatically.

## Requirements

- Python 3.11 or later
- pip

## Installation

### Minimal (Desktop only)
```bash
pip install -e .
```

### All features (recommended)
```bash
pip install -e ".[all]"
```

### Server only
```bash
pip install -e ".[server]"
```

## Commands

| Command | Description |
|---|---|
| `genesis` | Launch Desktop application |
| `genesis desktop` | Launch Desktop application |
| `genesis studio` | Show Studio reference app manifest |
| `genesis serve` | Start local web server (port 8080) |
| `genesis terminal` | Start engineering REPL |
| `genesis dev` | Development mode with hot reload |
| `genesis doctor` | Run system diagnostics |
| `genesis status` | Show platform status summary |
| `genesis config` | Show current configuration |
| `genesis workspace` | Show or open workspace |
| `genesis import <path>` | Import a repository/project |
| `genesis setup` | Run first-run setup wizard |
| `genesis version` | Show version information |
| `genesis --help` | Show help |

## Modes

### Desktop Mode (default)
```bash
genesis
```
Full TUI desktop with experience-first navigation:
Understand Project, Review Architecture, Continue Work,
Investigate Problem, Improve Repository.

Requires a terminal with TTY support (xterm-256color).

### Web Server Mode
```bash
genesis serve
```
Boots Genesis and exposes REST API + WebSocket at `http://localhost:8080`.
23 API endpoints + Swagger UI at `/docs`. No frontend HTML.

### Terminal Mode
```bash
genesis terminal
```
Engineering REPL with 15 commands (status, events, agents, apps,
providers, knowledge, search, memory, timeline, services, health,
resources, lifecycle). Type `help` for available commands.

### Development Mode
```bash
genesis dev
```
Watches source files and auto-restarts on changes. Uses watchdog
for file monitoring and subprocess management.

## First Run

On first launch, Genesis:
1. Detects no configuration exists
2. Opens the setup wizard automatically
3. Collects workspace location, AI provider, API key, theme
4. Creates workspace at `~/Genesis/` with 11 subdirectories
5. Saves configuration to `~/.genesis/config.json`
6. Launches the Desktop

## Project Import

```bash
genesis import /path/to/your/project
```

Imports a repository by:
- Scanning all files (27K files in ~7 seconds for a large project)
- Building a catalog organized by file type
- Creating a project entry in the workspace
- Registering an Engineering Object (in-memory)

**Note**: Full import (Digital Twin, Knowledge Graph, Insights) is
not yet wired. The import currently catalogs files and creates
project metadata.

## Workspace Structure

```
~/Genesis/
  Projects/       — Imported repository metadata
  Knowledge/      — File catalogs
  Memory/         — (future use)
  Reports/        — (future use)
  Logs/           — (future use)
  Settings/       — Workspace state
  Applications/   — (future use)
  Cache/          — (future use)
  Plugins/        — (future use)
  Backups/        — (future use)
  Exports/        — (future use)
```

## Configuration

Stored at `~/.genesis/config.json`. View with:
```bash
genesis config
```

Settings include: workspace path, AI provider, API key, theme,
desktop dimensions, log level, API host/port.

## Troubleshooting

```bash
# Run diagnostics
genesis doctor

# Re-run setup
genesis setup

# Check platform status
genesis status

# Debug mode (full tracebacks)
genesis --debug <command>
# or
GENESIS_DEBUG=1 genesis <command>
```

## Web API

When the server is running (`genesis serve`):

| Endpoint | Description |
|---|---|
| `/v1/health` | Health check |
| `/v1/events` | Query and emit events |
| `/v1/search` | Search across all subsystems |
| `/v1/agents` | List AI agents |
| `/v1/providers` | List AI providers |
| `/v1/services` | List platform services |
| `/v1/tasks` | List and manage tasks |
| `/v1/kernel/stats` | Kernel statistics |
| `/v1/storage` | Storage information |
| `/v1/metrics` | Performance metrics |
| `/v1/audit` | Audit log |
| `/v1/auth/status` | Authentication status |
| `/v1/repository` | Repository information |
| `/v1/conversations` | Conversation management |
| `/v1/execution` | Execution status |
| `/v1/watch` | Watch service status |
| `/v1/events/emit` | Emit a new event (POST) |
| `/docs` | Swagger UI documentation |
| `/redoc` | ReDoc documentation |
| `ws://host/ws` | WebSocket for real-time events |

## Architecture

Genesis is organized in layers:

- **L1** — Foundations: model, compiler, validation, graph, runtime, memory
- **L2** — Core OS: plugin, capability, package management
- **L3** — Services: knowledge graph, digital twin, evolution, brain
- **L4** — Infrastructure: lifecycle, resources, performance, query, hardening
- **L5** — Constitution: governance, validation, certification

## Development Status: Alpha

Genesis is installable and usable. See
`Reports/Cycle_022_Recovery/14_final_readiness.md` for the full
readiness assessment.

### Known Gaps
- Engineering Objects are in-memory (no persistence across restarts)
- Digital Twin and Knowledge Graph not wired into import flow
- No web frontend (API only)
- No binary packaging (.app, .exe, Docker)
- Desktop requires TTY (no headless mode)
- API keys stored in plaintext config

## Extras

```bash
# Server dependencies
pip install ".[server]"

# File watching (dev mode)
pip install ".[watch]"

# Everything
pip install ".[all]"
```

## License

Proprietary — Venus Research
