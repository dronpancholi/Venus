"""Genesis Desktop — M157 Experience-First Workspace.

Experience-first navigation replacing subsystem-based screens:
- Understand Project, Review Architecture, Continue Work, Investigate Problem, Improve Repository
- Activity Center with notification management
- Workspace Memory for persisting state across sessions
- Backward compatible: all original subsystem screens still available
"""

from genesis.desktop.app import GenesisDesktop
from genesis.desktop.memory import WorkspaceMemory
from genesis.desktop.activity import ActivityCenter, Notification, NotificationSeverity
from genesis.desktop.experiences import (
    UnderstandProject, ReviewArchitecture, ContinueWork,
    InvestigateProblem, ImproveRepository,
)
from genesis.desktop.activity_screen import ActivityCenterScreen


def run_desktop():
    """Launch the Genesis Desktop application."""
    from genesis.fabric.kernel import FabricKernel
    kernel = FabricKernel.instance()
    app = GenesisDesktop()
    app.run()


__all__ = [
    "GenesisDesktop", "run_desktop",
    "WorkspaceMemory", "ActivityCenter", "Notification", "NotificationSeverity",
    "UnderstandProject", "ReviewArchitecture", "ContinueWork",
    "InvestigateProblem", "ImproveRepository", "ActivityCenterScreen",
]
