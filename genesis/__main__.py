#!/usr/bin/env python3
"""
Genesis — Engineering Computing Platform.

Usage:
  genesis                  Launch Desktop (default)
  genesis desktop          Launch Desktop application
  genesis studio           Launch Genesis Studio reference app
  genesis serve            Start local web server
  genesis terminal         Start engineering REPL
  genesis dev              Development mode with hot reload
  genesis doctor           Run system diagnostics
  genesis status           Show platform status summary
  genesis config           Show current configuration
  genesis workspace        Show or open workspace
  genesis import <path>    Import a repository/project
  genesis setup            Run first-run setup wizard
  genesis version          Show version information
  genesis --help           Show this help
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path


def _print_help():
    help_text = """
[bold cyan]Genesis — Engineering Computing Platform[/bold cyan]

[bold]Usage:[/bold]
  [green]genesis[/green]                    Launch Desktop (default)
  [green]genesis desktop[/green]            Launch Desktop application
  [green]genesis studio[/green]             Launch Genesis Studio reference app
  [green]genesis serve[/green]              Start local web server
  [green]genesis terminal[/green]           Start engineering REPL
  [green]genesis dev[/green]                Development mode with hot reload
  [green]genesis doctor[/green]             Run system diagnostics
  [green]genesis status[/green]             Show platform status summary
  [green]genesis config[/green]             Show current configuration
  [green]genesis workspace[/green]          Show or open workspace
  [green]genesis import[/green] <path>      Import a repository/project
  [green]genesis karpathy[/green] <goal>    Run Karpathy goal-driven execution
  [green]genesis apply-rules[/green] <path>  Inject Karpathy rules (CLAUDE.md, Cursor)
  [green]genesis setup[/green]              Run first-run setup wizard
  [green]genesis version[/green]            Show version information
  [green]genesis --help[/green]             Show this help

[bold]First time?[/bold]
  Run [green]genesis setup[/green] to configure your workspace and AI provider.
"""
    try:
        from rich import print as rprint
        rprint(help_text)
    except ImportError:
        print(help_text.replace("[bold cyan]", "").replace("[/bold cyan]", "")
              .replace("[bold]", "").replace("[/bold]", "")
              .replace("[green]", "").replace("[/green]", "")
              .replace("[dim]", "").replace("[/dim]", ""))


def _print_version():
    try:
        from genesis import __version__
    except ImportError:
        __version__ = "1.0.0"
    print(f"Genesis v{__version__}")


# ---------------------------------------------------------------------------
# Bootstrap — ensure config is loaded before any command runs
# ---------------------------------------------------------------------------
def _ensure_config():
    """Load config from ~/.genesis/config.json if it exists."""
    try:
        from genesis.config.settings import init_config
        init_config()
    except Exception:
        pass


def _auto_setup_if_needed():
    """If config doesn't exist, run the setup wizard automatically."""
    from genesis.config.settings import first_run_file_exists, config
    is_tty = sys.stdin.isatty()
    if not first_run_file_exists():
        if is_tty:
            try:
                from genesis.setup import run_setup
                run_setup(quiet=False)
                from genesis.config.settings import init_config
                init_config()
                return True
            except ImportError:
                pass
        else:
            # Non-TTY first run — create default config silently
            from genesis.config.settings import ensure_workspace, get_config_path
            config.setup_complete = True
            config.setup_version = config.version
            ensure_workspace(config.workspace_path)
            config.save()
    return False


def _banner():
    try:
        from rich import print as rprint
        rprint("[dim]Genesis — Engineering Computing Platform[/dim]")
    except ImportError:
        print("Genesis — Engineering Computing Platform")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_desktop(args: list[str]):
    """Launch the Genesis Desktop application."""
    _banner()
    _ensure_config()
    _auto_setup_if_needed()
    from genesis.desktop import run_desktop
    from genesis.fabric.kernel import FabricKernel
    kernel = FabricKernel.instance()
    kernel.boot()
    run_desktop()


def cmd_studio(args: list[str]):
    """Show Genesis Studio reference app manifest."""
    _banner()
    _ensure_config()
    _auto_setup_if_needed()
    from rich import print as rprint
    from rich.table import Table
    from genesis.studio import STUDIO_MANIFEST

    rprint(f"\n[bold]Genesis Studio[/bold] — {STUDIO_MANIFEST['description']}")
    rprint()
    table = Table(title="Studio Manifest")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Name", STUDIO_MANIFEST["name"])
    table.add_row("Version", STUDIO_MANIFEST["version"])
    table.add_row("Capabilities", str(len(STUDIO_MANIFEST["capabilities"])))
    table.add_row("Permissions", str(len(STUDIO_MANIFEST["permissions"])))
    table.add_row("Screens", str(len(STUDIO_MANIFEST.get("screens", []))))
    rprint(table)
    rprint()
    rprint("[dim]Studio is a reference app. Launch the Desktop with 'genesis desktop' to use the full UI.[/dim]")


def cmd_serve(args: list[str]):
    """Start the local web server."""
    _banner()
    _ensure_config()
    _auto_setup_if_needed()

    host = os.environ.get("GENESIS_HOST", "127.0.0.1")
    port = int(os.environ.get("GENESIS_PORT", "8080"))

    try:
        from genesis.server import run_server
    except ImportError as e:
        print(f"Error: Server dependencies not installed. {e}")
        print("Install with: pip install 'genesis[server]'")
        sys.exit(1)

    from genesis.fabric.kernel import FabricKernel
    kernel = FabricKernel.instance()
    kernel.boot()

    from pathlib import Path
    frontend_dir = Path(__file__).parent.parent / "web" / "dist"
    if not frontend_dir.is_dir():
        frontend_dir = None

    from rich import print as rprint
    rprint()
    rprint("[bold green]Genesis started.[/bold green]")
    rprint()
    if frontend_dir:
        rprint(f"  [bold]Web:[/bold]      [cyan]http://{host}:{port}/[/cyan]")
        rprint(f"  [bold]Desktop:[/bold]  [cyan]http://{host}:{port}/desktop[/cyan]")
    rprint(f"  [bold]API:[/bold]       [cyan]http://{host}:{port}/docs[/cyan]")
    rprint(f"  [bold]WebSocket:[/bold] [cyan]ws://{host}:{port}/v1/ws[/cyan]")
    rprint()
    from genesis.fabric.kernel import FabricKernel as FK
    k = FK.instance()
    h = k.health()
    rprint(f"  [dim]Status: {h.status} | "
           f"{h.services_count} services | {h.messages_sent} messages[/dim]")
    rprint()

    run_server(host=host, port=port, frontend_dir=str(frontend_dir) if frontend_dir else None)


def cmd_terminal(args: list[str]):
    """Start the engineering REPL terminal."""
    _ensure_config()
    try:
        from rich import print as rprint
    except ImportError:
        rprint = print

    from genesis.fabric.kernel import FabricKernel
    from genesis.lifecycle import PlatformLifecycle
    from genesis.terminal import EngineeringTerminal

    kernel = FabricKernel.instance()
    kernel.boot()

    lifecycle = PlatformLifecycle(kernel)
    t = EngineeringTerminal(kernel=lifecycle._kernel, lifecycle=lifecycle)

    rprint("[bold cyan]Genesis Terminal — type 'help' for commands, 'exit' to quit[/bold cyan]")
    rprint()
    while True:
        try:
            line = input("genesis> ")
        except (EOFError, KeyboardInterrupt):
            rprint()
            break
        if line.strip().lower() in ("exit", "quit", "q"):
            break
        if not line.strip():
            continue
        result = t.execute(line.strip())
        if result.error:
            rprint(f"[red]{result.error}[/red]")
        elif result.text:
            rprint(result.text)
        elif result.data:
            if result.format == "json":
                import json
                rprint(json.dumps(result.data, indent=2, default=str))
            else:
                rprint(str(result.data))


def cmd_dev(args: list[str]):
    """Development mode with hot reload."""
    _ensure_config()
    _auto_setup_if_needed()
    from genesis.dev import run_dev
    run_dev(args)


def cmd_doctor(args: list[str]):
    """Run system diagnostics."""
    from genesis.doctor import run
    run(verbose="--verbose" in args or "-v" in args)


def cmd_status(args: list[str]):
    """Show platform status."""
    _ensure_config()
    from rich.console import Console
    from rich.table import Table
    from genesis.config.settings import config, first_run_file_exists

    console = Console()

    table = Table(title="Genesis Platform Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")

    table.add_row("Configuration", "Ready" if first_run_file_exists() else "Not configured")
    table.add_row("Workspace", config.workspace_path)

    import importlib
    for mod, label in [("genesis.fabric.kernel", "Fabric Kernel"),
                       ("genesis.lifecycle", "Lifecycle"),
                       ("genesis.desktop", "Desktop"),
                       ("genesis.server", "API Server"),
                       ("genesis.terminal", "Terminal"),
                       ("genesis.resources", "Resources"),
                       ("genesis.performance", "Performance"),
                       ("genesis.data", "Data Platform"),
                       ("genesis.query", "Query Engine"),
                       ("genesis.runtime", "App Runtime"),
                       ("genesis.workspace", "Workspace"),
                       ("genesis.marketplace", "Marketplace"),
                       ("genesis.contracts", "Contracts"),
                       ("genesis.hardening", "Hardening")]:
        try:
            importlib.import_module(mod)
            status = "[green]✓[/green]"
        except ImportError:
            status = "[dim]—[/dim]"
        table.add_row(label, status)

    console.print(table)
    console.print(f"\n  [dim]Genesis v{config.version} — {config.workspace_path}[/dim]")


def cmd_config(args: list[str]):
    """Show current configuration."""
    _ensure_config()
    from rich.console import Console
    from rich.table import Table
    from genesis.config.settings import config

    console = Console()
    table = Table(title="Genesis Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for k, v in sorted(config.to_dict().items()):
        if k == "ai_api_key" and v:
            v = "****" + v[-4:]
        table.add_row(k, str(v))

    console.print(table)


def cmd_workspace(args: list[str]):
    """Show or open workspace."""
    _ensure_config()
    from genesis.config.settings import config, ensure_workspace, WORKSPACE_DIRS
    from rich.console import Console
    from rich.table import Table
    from pathlib import Path

    ws = Path(config.workspace_path)
    console = Console()

    if not ws.exists():
        console.print(f"[yellow]Workspace {ws} does not exist. Creating...[/yellow]")
        ensure_workspace(ws)
        console.print(f"[green]✓ Created workspace at {ws}[/green]")

    table = Table(title=f"Workspace: {ws}")
    table.add_column("Directory", style="cyan")
    table.add_column("Exists", style="green")
    table.add_column("Items", style="white")

    for d in WORKSPACE_DIRS:
        dp = ws / d
        exists = dp.exists()
        items = len(list(dp.iterdir())) if exists else 0
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        table.add_row(d, status, str(items))

    console.print(table)

    # Try to open in Finder on macOS
    if sys.platform == "darwin":
        try:
            import subprocess
            subprocess.Popen(["open", str(ws)])
        except Exception:
            pass


def cmd_import_project(args: list[str]):
    """Import a repository/project into Genesis."""
    _ensure_config()
    from rich.console import Console
    from rich.prompt import Prompt
    from pathlib import Path
    import json
    import time

    console = Console()

    # determine path
    if args and args[0] not in ("--help", "-h"):
        repo_path = Path(args[0]).resolve()
    else:
        repo_path = Path(Prompt.ask("  Repository path")).resolve()

    if not repo_path.exists() or not repo_path.is_dir():
        console.print(f"[red]Error: {repo_path} does not exist or is not a directory[/red]")
        return

    project_name = repo_path.name
    console.print(f"\n[bold]Importing:[/bold] [cyan]{project_name}[/cyan]")
    console.print(f"  [dim]Path: {repo_path}[/dim]")
    console.print()

    from genesis.config.settings import config, ensure_workspace

    ws = Path(config.workspace_path)
    ensure_workspace(ws)
    projects_dir = ws / "Projects"
    knowledge_dir = ws / "Knowledge"
    project_dir = projects_dir / project_name

    start = time.time()
    summary_data = {}
    catalog = {}
    total = 0

    # ── Step 1: Index repository ──
    console.print(f"  [yellow]⟳[/yellow] Indexing repository...")
    try:
        from genesis.indexer.indexer import RepositoryIndexer
        indexer = RepositoryIndexer(repo_path)
        summary_data = indexer.scan()
        catalog = getattr(indexer, "catalog", None) or {}
        total = summary_data.get("total_files", 0)
        by_type = summary_data.get("by_type", {})
        console.print(f"  [green]✓[/green] {total} files indexed ({by_type.get('script',0)} source, "
                      f"{by_type.get('documentation',0)} docs, {by_type.get('config',0)} config)")
    except ImportError:
        console.print(f"  [yellow]⚠ Indexer not available — skipping scan[/yellow]")

    # ── Step 2: Create project entry ──
    console.print(f"  [yellow]⟳[/yellow] Creating project entry...")
    project_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "name": project_name,
        "path": str(repo_path),
        "imported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_files": total,
        "total_size_bytes": summary_data.get("total_size_bytes", 0),
    }
    (project_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    console.print(f"  [green]✓[/green] Project entry at {project_dir}")

    # ── Step 3: Save catalog to Knowledge ──
    console.print(f"  [yellow]⟳[/yellow] Saving knowledge catalog...")
    project_knowledge = knowledge_dir / project_name
    project_knowledge.mkdir(parents=True, exist_ok=True)
    if catalog:
        (project_knowledge / "catalog.json").write_text(
            json.dumps(catalog, indent=2, default=str)
        )
        console.print(f"  [green]✓[/green] Catalog saved ({len(catalog)} entries)")
    else:
        console.print(f"  [yellow]⚠ No catalog data[/yellow]")

    # ── Step 4: Build Engineering Object ──
    console.print(f"  [yellow]⟳[/yellow] Registering Engineering Object...")
    try:
        from genesis.engineering.registry import EngineeringRegistry
        from genesis.engineering.object import EngineeringObject, EngineeringObjectType
        er = EngineeringRegistry()
        obj = EngineeringObject(
            name=project_name,
            object_type=EngineeringObjectType.PROJECT,
            description=f"Project imported from {repo_path}",
            metadata=meta,
        )
        er.register(obj)
        console.print(f"  [green]✓[/green] {project_name} registered as Engineering Object")
    except ImportError:
        console.print(f"  [yellow]⚠ Engineering registry not available[/yellow]")

    # ── Step 5: Initialize workspace tracking ──
    console.print(f"  [yellow]⟳[/yellow] Linking to workspace...")
    try:
        from genesis.workspace import WorkspaceManager
        wm = WorkspaceManager()
        wm._pinned_projects.append(project_name)
        wm._recent_work.append(str(repo_path))
        # persist workspace state
        ws_state = ws / "Settings" / "workspace_state.json"
        state = {"pinned": wm._pinned_projects, "recent": wm._recent_work}
        ws_state.write_text(json.dumps(state, indent=2))
        console.print(f"  [green]✓[/green] Project linked to workspace")
    except ImportError:
        console.print(f"  [yellow]⚠ Workspace linking not available[/yellow]")

    # ── Step 6: Provision Karpathy Rules ──
    console.print(f"  [yellow]⟳[/yellow] Provisioning Karpathy guidelines...")
    try:
        from genesis.karpathy_provisioning import provision_karpathy_rules
        prov_res = provision_karpathy_rules(repo_path)
        console.print(f"  [green]✓[/green] Rules injected ({', '.join(prov_res.keys())})")
    except Exception as e:
        console.print(f"  [yellow]⚠ Rule provisioning skipped: {e}[/yellow]")

    elapsed = time.time() - start
    console.print()
    console.print(f"[bold green]✓[/bold green] [bold]'{project_name}' imported successfully (in {elapsed:.1f}s)[/bold]")
    console.print(f"  [dim]Run [cyan]genesis[/cyan] to open the Desktop.[/dim]")


def cmd_karpathy(args: list[str]):
    """Run Karpathy goal-driven execution."""
    _ensure_config()
    from rich.console import Console
    console = Console()
    if not args:
        console.print("[red]Error: Goal description required.[/red]")
        console.print("Usage: genesis karpathy \"<goal description>\" [verification_command]")
        return
    goal = args[0]
    verify_cmd = args[1] if len(args) > 1 else "pytest"

    console.print(f"\n[bold cyan]Genesis Karpathy Execution Engine[/bold cyan]")
    console.print(f"  [bold]Goal:[/bold] {goal}")
    console.print(f"  [bold]Verify Command:[/bold] {verify_cmd}\n")

    from genesis.agentos.karpathy import KarpathyExecutionEngine
    engine = KarpathyExecutionEngine(".")
    res = engine.execute_goal(goal, verify_cmd)

    console.print(f"  [bold]Thought Assumptions:[/bold] {res.thought.assumptions}")
    console.print(f"  [bold]Tradeoffs Surface:[/bold] {res.thought.tradeoffs}")
    if res.success:
        console.print(f"\n[bold green]✓ Goal Verified & Passed![/bold green] (Iterations: {res.iterations})")
    else:
        console.print(f"\n[bold red]✗ Goal Verification Failed[/bold red] (Iterations: {res.iterations})")
        console.print(f"Output:\n{res.final_verification_output}")


def cmd_apply_rules(args: list[str]):
    """Inject Karpathy rules into a target project."""
    from rich.console import Console
    from pathlib import Path
    console = Console()
    target = Path(args[0]).resolve() if args else Path(".").resolve()
    from genesis.karpathy_provisioning import provision_karpathy_rules
    res = provision_karpathy_rules(target)
    console.print(f"[bold green]✓ Karpathy Guidelines Provisioned at {target}:[/bold green]")
    for k, v in res.items():
        console.print(f"  - {k}: {v}")


def _handle_error(e: BaseException, command: str):
    """Print a human-readable error instead of a raw traceback."""
    msg = str(e)
    from rich.console import Console
    console = Console()
    console.print(f"\n[red]Error running 'genesis {command}':[/red]")
    console.print(f"  [bold]{type(e).__name__}:[/bold] {msg}")
    console.print()
    if "No module named" in msg:
        missing = msg.split("'")[1] if "'" in msg else "?"
        console.print(f"[yellow]Suggested fix:[/yellow] Install missing dependency:")
        console.print(f"  [bold cyan]pip install 'genesis[{missing}]'[/bold cyan]")
    elif "connection refused" in msg.lower() or "timeout" in msg.lower():
        console.print("[yellow]Suggested fix:[/yellow] Check that the required service is running.")
    elif "permission" in msg.lower() or "denied" in msg.lower():
        console.print("[yellow]Suggested fix:[/yellow] Check file permissions.")
    elif "does not exist" in msg or "not found" in msg.lower():
        console.print("[yellow]Suggested fix:[/yellow] Check that the path is correct.")
    else:
        console.print(f"[yellow]Suggested fix:[/yellow] Run [bold cyan]genesis doctor[/bold cyan] for diagnostics.")
        console.print(f"[yellow]Or:[/yellow] Run [bold cyan]genesis setup[/bold cyan] to reconfigure.")
    console.print()
    sys.exit(1)


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    command = args[0] if args else "desktop"

    try:
        if not args or args[0] in ("desktop", "ui", "tui"):
            cmd_desktop(args[1:])
        elif args[0] in ("studio",):
            cmd_studio(args[1:])
        elif args[0] in ("server", "serve", "api"):
            cmd_serve(args[1:])
        elif args[0] in ("terminal", "console", "repl"):
            cmd_terminal(args[1:])
        elif args[0] in ("dev", "develop", "development"):
            cmd_dev(args[1:])
        elif args[0] in ("doctor", "diagnose", "check"):
            cmd_doctor(args[1:])
        elif args[0] in ("status", "info"):
            cmd_status(args[1:])
        elif args[0] in ("config", "configuration", "settings"):
            cmd_config(args[1:])
        elif args[0] in ("workspace", "ws"):
            cmd_workspace(args[1:])
        elif args[0] in ("import", "import-project", "add"):
            if "--help" in args or "-h" in args:
                print("Usage: genesis import <path>")
                print("Import a repository/project into Genesis.")
                return
            cmd_import_project(args[1:])
        elif args[0] in ("karpathy", "goal-run"):
            cmd_karpathy(args[1:])
        elif args[0] in ("apply-rules", "provision-rules"):
            cmd_apply_rules(args[1:])
        elif args[0] in ("setup", "configure", "init", "wizard"):
            if "--help" in args or "-h" in args:
                _print_help()
                return
            from genesis.setup import run
            run()
        elif args[0] in ("version", "--version", "-V"):
            _print_version()
        elif args[0] in ("--help", "-h", "help"):
            _print_help()
        else:
            print(f"Unknown command: {args[0]}")
            _print_help()
            sys.exit(1)
    except (ImportError, ModuleNotFoundError) as e:
        _handle_error(e, command)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        if "--debug" in args or os.environ.get("GENESIS_DEBUG"):
            raise
        _handle_error(e, command)


if __name__ == "__main__":
    main()
