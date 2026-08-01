"""
Genesis diagnostics — 'genesis doctor'.

Checks the health of the installation, configuration, workspace,
dependencies, and environment. Reports actionable issues.
"""

from __future__ import annotations

import importlib
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from genesis.config.settings import config, first_run_file_exists, WORKSPACE_DIRS

console = Console()

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

CheckResult = tuple[str, bool, str]  # (name, passed, message)


def check_python_version() -> CheckResult:
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 11
    msg = f"Python {v.major}.{v.minor}.{v.micro}" + (" (>=3.11 ✓)" if ok else " (need >=3.11)")
    return ("Python Version", ok, msg)


def check_genesis_import() -> CheckResult:
    try:
        import genesis
        v = getattr(genesis, "__version__", "?")
        return ("Genesis Package", True, f"genesis {v} imported from {os.path.dirname(genesis.__file__)}")
    except ImportError as e:
        return ("Genesis Package", False, f"Import failed: {e}")


def check_config() -> CheckResult:
    cfg_path = config.config_path()
    if cfg_path.exists():
        try:
            config.load()
            if config.setup_complete:
                return ("Configuration", True, f"Found at {cfg_path} (setup complete)")
            else:
                return ("Configuration", True, f"Found at {cfg_path} (setup NOT complete — run 'genesis setup')")
        except Exception as e:
            return ("Configuration", False, f"Corrupt config at {cfg_path}: {e}")
    else:
        return ("Configuration", False, "No config found — run 'genesis setup' first")


def check_workspace() -> CheckResult:
    ws = Path(config.workspace_path)
    if not ws.exists():
        return ("Workspace", False, f"Directory {ws} does not exist")
    missing = [d for d in WORKSPACE_DIRS if not (ws / d).exists()]
    if missing:
        return ("Workspace", False, f"Missing subdirectories: {', '.join(missing)}")
    return ("Workspace", True, f"Ready at {ws}")


def check_dependencies() -> CheckResult:
    required = ["rich", "textual"]
    missing = []
    for pkg in required:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        return ("Dependencies", False, f"Missing: {', '.join(missing)} — run 'pip install genesis[all]'")
    return ("Dependencies", True, "All core dependencies present")


def check_optional_dependencies() -> CheckResult:
    optional = {
        "fastapi": "server",
        "uvicorn": "server",
        "websockets": "server",
        "watchdog": "watch/dev mode",
    }
    missing = []
    for pkg, feature in optional.items():
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(f"{pkg} ({feature})")
    if missing:
        return ("Optional Dependencies", True, f"Missing: {', '.join(missing)} — install with 'pip install genesis[all]'")
    return ("Optional Dependencies", True, "All optional packages present")


def check_disk_space() -> CheckResult:
    ws = Path(config.workspace_path)
    if ws.exists():
        try:
            usage = shutil.disk_usage(ws)
            free_gb = usage.free / (1024 ** 3)
            ok = free_gb > 0.5
            msg = f"{free_gb:.1f} GB free" + (" ✓" if ok else " (< 0.5 GB — low disk space)")
            return ("Disk Space", ok, msg)
        except OSError:
            return ("Disk Space", True, "Could not check — skipping")
    return ("Disk Space", True, "Workspace not created yet")


def check_port_availability(port: int = 8080) -> CheckResult:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            if result == 0:
                return ("Port 8080", False, f"Port {port} is already in use")
            return ("Port 8080", True, f"Port {port} is available")
    except Exception as e:
        return ("Port 8080", True, f"Could not check: {e}")


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    check_python_version,
    check_genesis_import,
    check_config,
    check_workspace,
    check_dependencies,
    check_optional_dependencies,
    check_disk_space,
    check_port_availability,
]


def run_doctor(verbose: bool = False) -> list[CheckResult]:
    """Run all diagnostic checks and return results."""
    results = []
    for check_fn in ALL_CHECKS:
        try:
            results.append(check_fn())
        except Exception as e:
            results.append((check_fn.__name__, False, str(e)))
    return results


def print_results(results: list[CheckResult]):
    """Display diagnostic results in a formatted table."""
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)

    table = Table(title=f"Genesis Doctor — {passed}/{total} checks passed")
    table.add_column("Status", width=4)
    table.add_column("Check", style="cyan")
    table.add_column("Detail")

    for name, ok, msg in results:
        status = "[green]✓[/green]" if ok else "[red]✗[/red]"
        table.add_row(status, name, msg)

    console.print(table)

    failures = [(n, m) for n, ok, m in results if not ok]
    if failures:
        console.print()
        console.print(Panel(
            "\n".join(f"[red]•[/red] [bold]{n}[/bold]: {m}" for n, m in failures),
            title="Issues Found",
            border_style="red",
        ))
        console.print()
        console.print("[yellow]Tip:[/yellow] Run [bold cyan]genesis setup[/bold cyan] if configuration is missing.")
        console.print("[yellow]Tip:[/yellow] Install all extras with [bold cyan]pip install 'genesis[all]'[/bold cyan]")

    return len(failures) == 0


def run(verbose: bool = False) -> int:
    """Entry point for 'genesis doctor'."""
    results = run_doctor(verbose=verbose)
    ok = print_results(results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run(verbose=True))
