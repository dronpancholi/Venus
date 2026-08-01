"""
First-run setup wizard for Genesis.

Guides the user through:
  - Workspace location
  - AI provider & API key
  - Theme & desktop preferences
  - Automatic workspace creation
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from genesis.config.settings import (
    config,
    ensure_workspace,
    get_config_path,
)

console = Console()

AI_PROVIDERS = [
    ("openai", "OpenAI", "GPT-4, GPT-4o, GPT-3.5"),
    ("anthropic", "Anthropic", "Claude 3.5 Sonnet, Claude 3 Opus"),
    ("google", "Google", "Gemini 1.5 Pro, Gemini 1.5 Flash"),
    ("nvidia_nim", "NVIDIA NIM Cloud", "Llama, Nemotron, Mistral, Qwen via cloud API"),
    ("local", "Local (Ollama)", "Run models locally via Ollama"),
    ("lm_studio", "LM Studio", "Local models via LM Studio (OpenAI-compatible)"),
    ("none", "Skip", "Set up AI provider later"),
]

THEMES = ["dark", "light"]


def show_welcome():
    rprint()
    console.print(Panel(
        Text.from_markup(
            "[bold cyan]Welcome to Genesis![/bold cyan]\n\n"
            "Genesis is your Engineering Computing Platform — "
            "a unified environment for\n"
            "understanding, building, and evolving software systems.\n\n"
            "Let's get you set up in a few quick steps."
        ),
        title="✨ GENESIS SETUP",
        subtitle="First-run configuration wizard",
        border_style="cyan",
    ))
    rprint()


def ask_workspace() -> str:
    default = os.path.expanduser("~/Genesis")
    rprint()
    console.print("[bold]Workspace Location[/bold]")
    console.print("Genesis will store your projects, knowledge, and data here.")
    path = Prompt.ask("  Path", default=default)
    return os.path.expanduser(path)


def ask_ai_provider() -> tuple[str, str, str]:
    rprint()
    console.print("[bold]AI Provider[/bold]")
    console.print("Genesis uses an AI provider for engineering assistance.")
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Models", style="white")
    for key, name, models in AI_PROVIDERS:
        table.add_row(f"  {key}", name, models)
    console.print(table)

    provider = Prompt.ask(
        "  Choose a provider",
        choices=[p[0] for p in AI_PROVIDERS],
        default="none",
    )

    if provider == "none":
        return "", "", ""

    api_key = ""
    model = ""

    providers_map = {p[0]: p[1] for p in AI_PROVIDERS}
    if provider in ("openai", "anthropic", "google", "nvidia_nim"):
        api_key = Prompt.ask(
            f"  API Key for {providers_map[provider]}",
            password=True,
        )
        if provider == "openai":
            model = Prompt.ask("  Model", default="gpt-4o")
        elif provider == "anthropic":
            model = Prompt.ask("  Model", default="claude-sonnet-4-20250514")
        elif provider == "google":
            model = Prompt.ask("  Model", default="gemini-1.5-pro")
        elif provider == "nvidia_nim":
            model = Prompt.ask(
                "  Model (leave empty to list available models)",
                default="",
            )
            if not model:
                model = "nvidia/llama-3.1-nemotron-70b-instruct"
    elif provider == "local":
        model = Prompt.ask("  Ollama model", default="codellama")
    elif provider == "lm_studio":
        api_key = Prompt.ask(
            "  API Key (leave empty if none)",
            default="",
            password=True,
        )
        base_url = Prompt.ask(
            "  Base URL",
            default="http://localhost:1234/v1",
        )
        config.ai_base_url = base_url
        model = Prompt.ask("  Model name", default="")

    return provider, api_key, model


def ask_theme() -> str:
    rprint()
    console.print("[bold]Theme[/bold]")
    theme = Prompt.ask(
        "  Choose a theme",
        choices=THEMES,
        default="dark",
    )
    return theme


def ask_desktop() -> tuple[int, int]:
    rprint()
    console.print("[bold]Desktop Preferences[/bold]")
    width = int(Prompt.ask("  Terminal width (columns)", default="120"))
    height = int(Prompt.ask("  Terminal height (rows)", default="80"))
    return width, height


def show_summary(workspace: str, provider: str, theme: str, width: int, height: int):
    rprint()
    table = Table(title="Configuration Summary", box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Workspace", workspace)
    table.add_row("AI Provider", provider or "(not set)")
    table.add_row("Theme", theme)
    table.add_row("Desktop", f"{width}×{height}")
    console.print(table)


def run_setup(quiet: bool = False) -> bool:
    """Run the first-time setup wizard. Returns True if setup completed."""

    if not quiet:
        show_welcome()

    # -- workspace --
    workspace = ask_workspace()
    ws_path = Path(workspace)

    # -- AI provider --
    provider, api_key, model = ask_ai_provider()

    # -- theme --
    theme = ask_theme()

    # -- desktop --
    width, height = ask_desktop()

    # -- summary --
    if not quiet:
        show_summary(workspace, provider, theme, width, height)

    if not quiet:
        confirm = Confirm.ask("\n  Apply these settings?", default=True)
        if not confirm:
            console.print("[yellow]Setup cancelled.[/yellow]")
            return False

    # -- apply --
    config.workspace_path = str(ws_path.resolve())
    config.ai_provider = provider if provider != "none" else ""
    config.ai_api_key = api_key
    config.ai_model = model
    config.theme = theme
    config.desktop_width = width
    config.desktop_height = height
    config.setup_complete = True
    config.setup_version = config.version

    # create workspace directory structure
    ensure_workspace(ws_path)

    # persist
    cfg_path = config.save()
    if not quiet:
        rprint()
        console.print(f"[green]✓[/green] Configuration saved to [bold]{cfg_path}[/bold]")
        console.print(f"[green]✓[/green] Workspace created at [bold]{ws_path}[/bold]")
        rprint()
        console.print(Panel(
            "[bold green]Setup complete![/bold green]\n\n"
            "Run [bold cyan]genesis[/bold cyan] to launch the Desktop,\n"
            "or [bold cyan]genesis --help[/bold cyan] to see all available commands.",
            border_style="green",
        ))

    return True


def run(quiet: bool = False):
    """Entry point for 'genesis setup'."""
    run_setup(quiet=quiet)


if __name__ == "__main__":
    run()
