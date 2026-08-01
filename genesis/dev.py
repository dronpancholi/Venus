"""
Genesis development mode — 'genesis dev'.

Watches the source tree for changes and auto-restarts the target process.
Provides verbose logging, debug tools, and a developer console overlay.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

DEV_ASSETS = Path(__file__).resolve().parent


def _find_genesis_package() -> Path:
    """Return the root of the genesis package."""
    return DEV_ASSETS


def _restart_process(args: list[str], env: dict[str, str] | None = None) -> subprocess.Popen:
    """Start (or restart) the genesis subprocess."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    merged_env.setdefault("GENESIS_DEV", "1")
    merged_env.setdefault("PYTHONUNBUFFERED", "1")

    python = sys.executable
    cmd = [python, "-m", "genesis"] + args

    return subprocess.Popen(
        cmd,
        env=merged_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )


def run_dev(args: list[str] | None = None) -> int:
    """
    Run genesis in development mode with hot reload.

    Watches the genesis source tree for changes and restarts automatically.
    """
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    target_args = args or []
    watch_path = _find_genesis_package()
    process: subprocess.Popen | None = None
    restart_event: list[bool] = [False]
    last_restart: list[float] = [0.0]
    debounce_seconds = 0.5

    class ChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith(".py"):
                now = time.time()
                if now - last_restart[0] > debounce_seconds:
                    console.print(f"[dim]Change detected: {event.src_path}[/dim]")
                    restart_event[0] = True
                    last_restart[0] = now

        def on_created(self, event):
            if event.src_path.endswith(".py"):
                now = time.time()
                if now - last_restart[0] > debounce_seconds:
                    console.print(f"[dim]New file: {event.src_path}[/dim]")
                    restart_event[0] = True
                    last_restart[0] = now

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=True)
    observer.start()

    console.print(Panel(
        Text.from_markup(
            "[bold cyan]Genesis Dev Mode[/bold cyan]\n"
            f"Watching: [green]{watch_path}[/green]\n"
            "Press [bold]Ctrl+C[/bold] to stop."
        ),
        border_style="cyan",
    ))

    try:
        while True:
            if process is None or restart_event[0]:
                if process is not None:
                    console.print("[yellow]Restarting...[/yellow]")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                restart_event[0] = False
                process = _restart_process(target_args)

            if process is not None and process.stdout:
                try:
                    line = process.stdout.readline()
                    if line:
                        print(line, end="")
                except (IOError, ValueError):
                    pass

            time.sleep(0.05)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutting down dev mode...[/bold yellow]")
    finally:
        observer.stop()
        observer.join()
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    return 0


if __name__ == "__main__":
    sys.exit(run_dev(sys.argv[1:]))
