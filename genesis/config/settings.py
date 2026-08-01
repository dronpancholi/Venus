"""
Platform configuration — persisted to ~/.genesis/config.json.

Powers the Genesis local development experience:
- First-run detection and setup wizard trigger
- Workspace location and directory structure
- AI provider and API key storage
- Theme and desktop preferences
- All platform settings from the original PlatformConfig
"""

import json
import os
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()


CONFIG_DIR_NAME = ".genesis"
CONFIG_FILE_NAME = "config.json"
DEFAULT_WORKSPACE = os.path.expanduser("~/Genesis")


# ---------------------------------------------------------------------------
# Workspace directory structure
# ---------------------------------------------------------------------------
WORKSPACE_DIRS = [
    "Projects",
    "Knowledge",
    "Memory",
    "Reports",
    "Logs",
    "Settings",
    "Applications",
    "Cache",
    "Plugins",
    "Backups",
    "Exports",
]


def get_config_dir() -> Path:
    if "GENESIS_CONFIG_DIR" in os.environ:
        return Path(os.environ["GENESIS_CONFIG_DIR"])
    home_cfg = Path(os.path.expanduser("~")) / CONFIG_DIR_NAME
    try:
        home_cfg.mkdir(parents=True, exist_ok=True)
        return home_cfg
    except Exception:
        local_cfg = Path.cwd() / CONFIG_DIR_NAME
        local_cfg.mkdir(parents=True, exist_ok=True)
        return local_cfg


def get_config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME


def ensure_config_dir() -> Path:
    return get_config_dir()


def first_run_file_exists() -> bool:
    return get_config_path().exists()


def ensure_workspace(workspace_path: str | Path) -> Path:
    """Create the full workspace directory structure and return the path."""
    ws = Path(workspace_path)
    ws.mkdir(parents=True, exist_ok=True)
    for sub in WORKSPACE_DIRS:
        (ws / sub).mkdir(parents=True, exist_ok=True)
    return ws


# ---------------------------------------------------------------------------
# Platform configuration
# ---------------------------------------------------------------------------
class PlatformConfig:
    """Genesis platform configuration — persisted across sessions."""

    def __init__(self):
        # --- identity ---
        self.version: str = "1.0.0"
        self.name: str = "Genesis"

        # --- first-run tracking ---
        self.setup_complete: bool = False
        self.setup_version: str = ""

        # --- workspace ---
        self.workspace_path: str = DEFAULT_WORKSPACE
        self.workspace_auto_create: bool = True

        # --- AI provider ---
        self.ai_provider: str = ""
        self.ai_api_key: str = ""
        self.ai_model: str = ""
        self.ai_base_url: str = ""

        # --- theme & display ---
        self.theme: str = "dark"
        self.desktop_width: int = 120
        self.desktop_height: int = 80

        # --- legacy platform settings ---
        self.debug: bool = False
        self.plugin_dirs: list[str] = ["_plugins"]
        self.compiler_output: str = "_build"
        self.graph_store: str = "_graph"
        self.metadata_store: str = "_metadata"
        self.catalog_store: str = "_catalog"
        self.log_level: str = "INFO"
        self.api_host: str = "localhost"
        self.api_port: int = 8080
        self.studio_enabled: bool = True
        self.diagnostics_interval: int = 3600
        self.cache_enabled: bool = True
        self.sandbox_enabled: bool = True

    # -- persistence -------------------------------------------------------

    def config_path(self) -> Path:
        return get_config_path()

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path else get_config_path()
        ensure_config_dir()
        target.write_text(self.to_json(indent=2), encoding="utf-8")
        return target

    def load(self, path: str | Path | None = None):
        target = Path(path) if path else get_config_path()
        try:
            if target.exists():
                raw = target.read_text(encoding="utf-8")
                if not raw.strip():
                    return
                data = json.loads(raw)
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except (OSError, json.JSONDecodeError):
            pass

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items()
            if (include_private or not k.startswith("_"))
            and not callable(v)
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    # -- backward compatibility: workspace_root -> workspace_path --
    @property
    def workspace_root(self) -> str:
        return self.workspace_path

    @workspace_root.setter
    def workspace_root(self, value: str):
        self.workspace_path = value

    def __repr__(self) -> str:
        return f"<PlatformConfig workspace={self.workspace_path} setup={self.setup_complete}>"


# Global singleton
config = PlatformConfig()


def init_config():
    """Load persisted config if it exists, else load defaults."""
    if first_run_file_exists():
        config.load()
    return config
