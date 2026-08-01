"""Genesis Desktop Application — M157 Experience-First Workspace."""

from __future__ import annotations

from typing import Any

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.screen import Screen
    from textual.widgets import Button, Static
except ImportError:
    raise ImportError("Textual is required. Install with: pip install textual")

from genesis.fabric.kernel import FabricKernel
from genesis.desktop.widgets import StatusBar
from genesis.desktop.activity import ActivityCenter
from genesis.desktop.memory import WorkspaceMemory
from genesis.desktop.experiences import (
    UnderstandProject, ReviewArchitecture, ContinueWork,
    InvestigateProblem, ImproveRepository,
)
from genesis.desktop.screens import (
    GenesisHome, FabricInspectorScreen,
    AgentCollaborationScreen, EngineeringMemoryExplorer,
    EngineeringTimelineScreen, KnowledgeGraphScreen,
    RepositoryScreen, AIOrchestrationCenter,
    ContinuousEngineeringScreen, ReportsScreen, SettingsScreen,
)
from genesis.desktop.palette import CommandPalette, SearchEverywhere


WORKSPACE_CSS = """
Screen {
    background: #0D0D10;
}
Static {
    color: #F5F5F7;
}
.exp-panel {
    border: solid #27272A;
    margin: 0 1;
}
/* Experience Navigation Bar */
#exp-nav {
    width: 100%;
    height: 5;
    background: #111114;
    border-bottom: solid #27272A;
    align: center middle;
    padding: 0 1;
}
#exp-nav-title {
    width: auto;
    text-style: bold;
    color: #5E9EFF;
    padding: 0 2;
}
.exp-nav-btn {
    width: auto;
    height: 3;
    background: transparent;
    color: #63636E;
    border: none;
    margin: 0 1;
    min-width: 10;
}
.exp-nav-btn:hover {
    background: #1C1C20;
    color: #F5F5F7;
}
.exp-nav-btn:focus {
    background: #26262B;
    color: #5E9EFF;
}
#exp-nav-activity {
    width: auto;
    background: transparent;
    color: #5E9EFF;
    margin: 0 2;
}
/* Status bar */
#status-bar {
    background: #08080A;
    color: #63636E;
    height: 1;
    dock: bottom;
}
/* Experience Screen styles */
#exp-title, #arch-title, #cw-title, #inv-title, #imp-title,
#act-title, #fi-title, #collab-title, #mem-title,
#timeline-title, #repo-title, #kg-title, #ai-title,
#ce-title, #reports-title, #settings-title {
    text-style: bold;
    padding: 1 2;
    background: #141417;
    color: #F5F5F7;
    text-align: center;
    height: 3;
}
#exp-subtitle, #arch-subtitle, #cw-subtitle, #inv-subtitle, #imp-subtitle,
#act-subtitle, #fi-subtitle, #collab-subtitle, #mem-subtitle,
#timeline-subtitle, #repo-subtitle, #kg-subtitle, #ai-subtitle,
#ce-subtitle, #reports-subtitle, #settings-subtitle {
    color: #63636E;
    text-align: center;
    padding: 0 2;
    height: 1;
}
#exp-status, #arch-status, #cw-status, #inv-status, #imp-status, #act-status {
    height: 1;
    background: #08080A;
    color: #63636E;
    text-align: center;
}
.section-title {
    text-style: bold;
    padding: 0 1;
    background: #1C1C20;
    color: #A1A1AA;
    height: 1;
}
#exp-left, #exp-center, #exp-right { width: 33%; height: 100%; }
#arch-left { width: 45%; height: 100%; }
#arch-right { width: 55%; height: 100%; }
#cw-left { width: 50%; height: 100%; }
#cw-right { width: 50%; height: 100%; }
#inv-left { width: 45%; height: 100%; }
#inv-right { width: 55%; height: 100%; }
#imp-left { width: 50%; height: 100%; }
#imp-right { width: 50%; height: 100%; }
/* Activity Center */
#act-content { background: #08080A; border: solid #27272A; height: 100%; margin: 0 2; }
/* Home */
#home-left { width: 35%; height: 100%; }
#home-center { width: 35%; height: 100%; }
#home-right { width: 30%; height: 100%; }
#home-attention { height: auto; max-height: 20; }
#home-activity { background: #08080A; border: solid #27272A; height: 40%; }
#home-agents { background: #141417; border: solid #27272A; height: 100%; }
#home-tasks { height: 3; }
#home-events { background: #08080A; border: solid #27272A; height: 60%; }
#home-sessions { height: 8; }
/* Fabric Inspector */
#fi-traffic { width: 40%; height: 100%; }
#fi-detail { width: 60%; height: 100%; }
#fi-traffic-light { height: 3; }
#fi-activity { background: #08080A; border: solid #27272A; height: 80%; }
#fi-event-stream { background: #08080A; border: solid #27272A; height: 100%; }
/* Agent Collaboration */
#collab-left { width: 45%; height: 100%; }
#collab-right { width: 55%; height: 100%; }
#collab-graph { height: auto; max-height: 20; }
#collab-list { background: #141417; border: solid #27272A; height: 70%; }
#collab-detail { background: #08080A; border: solid #27272A; height: 100%; }
/* Memory Explorer */
#mem-filter { background: #141417; border: solid #27272A; padding: 1; margin: 0 2; height: 3; }
#mem-nav { width: 40%; height: 100%; }
#mem-content { width: 60%; height: 100%; }
#mem-nav-list { background: #141417; border: solid #27272A; height: 100%; }
#mem-detail { background: #08080A; border: solid #27272A; height: 100%; }
/* Timeline */
#timeline-filter { background: #141417; border: solid #27272A; padding: 1; margin: 0 2; height: 3; }
#timeline-content { background: #08080A; border: solid #27272A; height: 100%; }
/* Repository */
#repo-file-tree-panel { width: 40%; height: 100%; }
#repo-info-panel { width: 60%; height: 100%; }
#file-tree { background: #141417; border: solid #27272A; height: 100%; }
#repo-content { background: #08080A; border: solid #27272A; height: 100%; }
/* Knowledge Graph */
#kg-search { background: #141417; border: solid #27272A; padding: 1; margin: 0 2; height: 3; }
#kg-panel-left { width: 40%; height: 100%; }
#kg-panel-right { width: 60%; height: 100%; }
#kg-entity-list { background: #141417; border: solid #27272A; height: 100%; }
#kg-inspect { background: #08080A; border: solid #27272A; height: 100%; }
/* AI Command Center */
#ai-provider-list { width: 40%; height: 100%; }
#ai-provider-detail { width: 60%; height: 100%; }
#ai-detail-content, #ai-providers-list { background: #141417; border: solid #27272A; height: 100%; }
#ai-detail-content { background: #08080A; }
/* CE */
#ce-watchers { width: 40%; height: 100%; }
#ce-events { width: 60%; height: 100%; }
#ce-watcher-log { background: #141417; border: solid #27272A; height: 100%; }
#ce-event-log { background: #08080A; border: solid #27272A; height: 100%; }
/* Reports */
#reports-cycle-list { width: 30%; height: 100%; }
#reports-content { width: 70%; height: 100%; }
#reports-list { background: #141417; border: solid #27272A; height: 100%; }
#reports-content-log { background: #08080A; border: solid #27272A; height: 100%; }
/* Common */
#agent-list { background: #141417; border: solid #27272A; height: 60%; }
#task-summary { background: #141417; border: solid #27272A; height: 3; padding: 0 1; }
ListView { background: #141417; }
ListItem { padding: 0 1; }
ListItem:hover { background: #2E2E34; }
ListView:focus Within { border: none; }
Button { background: #26262B; color: #F5F5F7; }
Button:hover { background: #5E9EFF; }
.hint { color: #63636E; text-align: center; height: 1; padding: 0 1; }
/* Palette & Search */
#palette-container { width: 60%; height: 60%; margin: 5 20; background: #1C1C20; border: solid #5E9EFF; }
#palette-input { background: #141417; border: none; padding: 1; }
#palette-list { background: #1C1C20; height: 100%; }
#palette-footer { background: #141417; color: #63636E; text-align: center; height: 1; }
#search-container { width: 70%; height: 70%; margin: 3 15; background: #1C1C20; border: solid #5E9EFF; }
#search-input { background: #141417; border: none; padding: 1; }
#search-sources { height: 3; background: #111114; padding: 0 1; }
.source-btn { width: 10; height: 1; background: #26262B; color: #A1A1AA; border: none; margin: 0 1; }
.source-btn:hover { background: #5E9EFF; color: #F5F5F7; }
#search-results { background: #1C1C20; height: 100%; }
#search-footer { background: #141417; color: #63636E; text-align: center; height: 1; }
"""


class ExperienceNavBar(Static):
    """Top navigation bar with experience-first buttons."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="exp-nav"):
            yield Static("[bold]Genesis[/]", id="exp-nav-title")
            yield Button("Understand", id="nav-understand", classes="exp-nav-btn")
            yield Button("Architecture", id="nav-architecture", classes="exp-nav-btn")
            yield Button("Continue Work", id="nav-continue", classes="exp-nav-btn")
            yield Button("Investigate", id="nav-investigate", classes="exp-nav-btn")
            yield Button("Improve", id="nav-improve", classes="exp-nav-btn")
            yield Static("|", id="exp-nav-sep")
            yield Button("Activity", id="nav-activity", classes="exp-nav-btn")
            yield Button("Home", id="nav-home", classes="exp-nav-btn")

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id or ""
        action = btn_id.replace("nav-", "")
        app = self.app
        if hasattr(app, action):
            getattr(app, action)()


class GenesisDesktop(App):
    """Genesis Desktop — M157 Experience-First Workspace."""

    TITLE = "Genesis"
    SUB_TITLE = "Engineering Operating System"
    CSS = WORKSPACE_CSS

    SCREENS = {
        "home": GenesisHome,
        "understand": UnderstandProject,
        "architecture": ReviewArchitecture,
        "continue": ContinueWork,
        "investigate": InvestigateProblem,
        "improve": ImproveRepository,
        "inspector": FabricInspectorScreen,
        "agents": AgentCollaborationScreen,
        "memory": EngineeringMemoryExplorer,
        "repository": RepositoryScreen,
        "timeline": EngineeringTimelineScreen,
        "graph": KnowledgeGraphScreen,
        "ai": AIOrchestrationCenter,
        "ce": ContinuousEngineeringScreen,
        "reports": ReportsScreen,
        "settings": SettingsScreen,
    }

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+k", "command_palette", "Palette"),
        Binding("ctrl+p", "search_everywhere", "Search"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("h", "home", "Home"),
        Binding("u", "understand", "Understand"),
        Binding("a", "architecture", "Architecture"),
        Binding("w", "continue_work", "Work"),
        Binding("i", "investigate", "Investigate"),
        Binding("m", "improve", "Improve"),
        Binding("n", "activity", "Activity Center"),
        Binding("f", "go_inspector", "Inspector"),
        Binding("g", "go_agents", "Agents"),
        Binding("t", "go_timeline", "Timeline"),
        Binding("r", "go_repository", "Repo"),
        Binding("p", "go_ai", "AI"),
        Binding("c", "go_ce", "CE"),
    ]

    def __init__(self):
        super().__init__()
        self._workspace_memory = WorkspaceMemory.instance()
        self._activity_center = ActivityCenter.instance()
        self._screen_cache: dict[str, tuple[Screen, str | None]] = {}

    def on_mount(self):
        kernel = FabricKernel.instance()
        kernel.boot()
        self._workspace_memory.boot(persist_path=".genesis/workspace_memory.json")

        last_screen = self._workspace_memory.get("last_screen", "understand")
        if last_screen in self.SCREENS:
            self.push_screen(last_screen)
        else:
            self.push_screen("understand")

        unread = self._activity_center.unread_count()
        self.notify(
            f"Genesis M157 ready. [U]nderstand [A]rchitecture [W]ork [I]nvestigate [M]prove  "
            f"Activity: {unread} unread",
            severity="information",
            timeout=5,
        )

    def navigate_to(self, target: str, source: str | None = None):
        if target not in self.SCREENS:
            return
        if target == "home" and len(self.screen_stack) <= 1:
            return
        source_id = None
        if self.screen and hasattr(self.screen, 'screen_id'):
            source_id = self.screen.screen_id
        self._workspace_memory.record_navigation(target)
        self._screen_cache[target] = (self.SCREENS[target](), source or source_id)
        self.push_screen(self._screen_cache[target][0])

    def action_back(self):
        if len(self.screen_stack) > 1:
            self.pop_screen()
        elif self.screen is not self.screen_stack[0]:
            self.switch_screen(self.screen_stack[0])

    def action_command_palette(self):
        self._workspace_memory.record_command("command_palette")
        self.push_screen(CommandPalette())

    def action_search_everywhere(self):
        self.push_screen(SearchEverywhere())

    def home(self):
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self._workspace_memory.record_navigation("home")

    def understand(self):
        self.navigate_to("understand")

    def architecture(self):
        self.navigate_to("architecture")

    def continue_work(self):
        self.navigate_to("continue")

    def investigate(self):
        self.navigate_to("investigate")

    def improve(self):
        self.navigate_to("improve")

    def activity(self):
        from genesis.desktop.activity_screen import ActivityCenterScreen
        self.push_screen(ActivityCenterScreen())

    def go_inspector(self):
        self.navigate_to("inspector")

    def go_agents(self):
        self.navigate_to("agents")

    def go_timeline(self):
        self.navigate_to("timeline")

    def go_repository(self):
        self.navigate_to("repository")

    def go_ai(self):
        self.navigate_to("ai")

    def go_ce(self):
        self.navigate_to("ce")

    def action_refresh(self):
        if self.screen is not None and hasattr(self.screen, 'action_refresh'):
            self.screen.action_refresh()
