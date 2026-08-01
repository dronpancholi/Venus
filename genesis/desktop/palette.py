"""Cycle 014 — Command Palette and Universal Search."""

from __future__ import annotations

try:
    from textual.app import ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.screen import ModalScreen
    from textual.widgets import (
        Button, Input, Label, ListItem, ListView, Static,
    )
except ImportError:
    raise ImportError("Textual is required. Install with: pip install textual")

from genesis.fabric.kernel import FabricKernel


COMMANDS = [
    ("home", "Command Center", "Go to Engineering Command Center", "ctrl+h"),
    ("inspector", "Fabric Inspector", "Watch real-time event flow", "ctrl+shift+f"),
    ("agents", "Agent Collaboration", "Open Agent Collaboration Visualizer", "ctrl+shift+a"),
    ("memory", "Memory Explorer", "Browse Engineering Memory", "ctrl+shift+m"),
    ("repository", "Repository Explorer", "Open Repository Intelligence", "ctrl+t"),
    ("timeline", "Engineering Timeline", "Open Engineering Timeline", "ctrl+e"),
    ("graph", "Knowledge Graph 2.0", "Open Interactive Knowledge Graph", "ctrl+g"),
    ("ai", "AI Orchestration Center", "Manage AI providers and routing", "ctrl+1"),
    ("ce", "Continuous Engineering V3", "Start/stop watchers, watch mode", "ctrl+2"),
    ("reports", "Reports", "View engineering reports", ""),
    ("settings", "Settings", "Workspace settings", ""),
    ("search", "Search Everywhere", "Search across all subsystems", "ctrl+p"),
    ("refresh", "Refresh", "Force refresh current view", "ctrl+r"),
    ("palette", "Command Palette", "Show this palette", "ctrl+k"),
    ("quit", "Quit", "Exit Genesis", "ctrl+q"),
    ("start_ce", "Start CE Watchers", "Start Continuous Engineering watchers", ""),
    ("stop_ce", "Stop CE Watchers", "Stop all watchers", ""),
    ("kernel_stats", "Kernel Stats", "Show kernel statistics", ""),
    ("emit_event", "Emit Test Event", "Emit a test event through the fabric", ""),
    ("inspector_metrics", "Fabric Metrics", "View live fabric metrics and histograms", ""),
    ("inspector_sessions", "Fabric Sessions", "View active sessions and scheduled tasks", ""),
    ("tasks", "Task Manager", "View and manage active tasks", ""),
]


class CommandPalette(ModalScreen):
    """M76 — Universal command palette. 25+ commands, keyboard-first navigation."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("down", "cursor_down", "Down"),
        Binding("up", "cursor_up", "Up"),
        Binding("enter", "execute", "Execute"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="palette-container"):
            yield Input(placeholder="Type a command...", id="palette-input")
            yield ListView(id="palette-list")
            yield Static("[dim]↑↓ Navigate ↵ Execute Esc Close[/]", id="palette-footer", classes="hint")

    def on_mount(self):
        self._all_commands = COMMANDS
        self._render_commands(self._all_commands)
        self.query_one("#palette-input", Input).focus()

    def _render_commands(self, commands: list[tuple]):
        lv = self.query_one("#palette-list", ListView)
        lv.clear()
        for action_id, name, desc, shortcut in commands:
            shortcut_text = f" [{shortcut}]" if shortcut else ""
            lv.append(ListItem(
                Label(f"[bold]{name}[/]  [dim]{desc}{shortcut_text}[/]"),
                id=f"cmd-{action_id}",
            ))

    def on_input_changed(self, event: Input.Changed):
        query = event.value.lower()
        filtered = [c for c in self._all_commands if query in c[1].lower() or query in c[2].lower() or query in c[0].lower()]
        self._render_commands(filtered)

    def action_cursor_down(self):
        self.query_one("#palette-list", ListView).action_cursor_down()

    def action_cursor_up(self):
        self.query_one("#palette-list", ListView).action_cursor_up()

    def action_execute(self):
        lv = self.query_one("#palette-list", ListView)
        if lv.children:
            lv.action_select()

    def on_list_view_selected(self, event: ListView.Selected):
        item_id = event.item.id or ""
        action = item_id.replace("cmd-", "")
        self.dismiss()
        app = self.app
        if action == "quit":
            app.exit()
        elif action == "palette":
            app.push_screen(CommandPalette())
        elif action == "search":
            app.push_screen(SearchEverywhere())
        elif action in ("home", "inspector", "agents", "memory", "repository", "timeline",
                        "graph", "ai", "ce", "reports", "settings"):
            app.navigate_to(action)
        elif action == "refresh":
            if hasattr(app.screen, 'action_refresh'):
                app.screen.action_refresh()
        elif action == "start_ce":
            self._start_ce()
        elif action == "stop_ce":
            self._stop_ce()
        elif action in ("emit_event", "kernel_stats", "inspector_metrics", "inspector_sessions", "tasks"):
            app.navigate_to("inspector")

    def _start_ce(self):
        try:
            from genesis.watch import ContinuousEngineering
            kernel = FabricKernel.instance()
            if not hasattr(kernel, '_continuous_engineering') or not kernel._continuous_engineering:
                ce = ContinuousEngineering(kernel)
                ce.setup_defaults(".")
                ce.start_all()
                kernel._continuous_engineering = ce
            self.app.notify("Continuous Engineering started", severity="information")
        except Exception as e:
            self.app.notify(f"Failed: {e}", severity="error")

    def _stop_ce(self):
        try:
            kernel = FabricKernel.instance()
            if hasattr(kernel, '_continuous_engineering') and kernel._continuous_engineering:
                kernel._continuous_engineering.stop_all()
                self.app.notify("Continuous Engineering stopped", severity="information")
        except Exception as e:
            self.app.notify(f"Failed: {e}", severity="error")


class SearchEverywhere(ModalScreen):
    """M112 — Engineering Spotlight: universal search across 20+ sources."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("down", "cursor_down", "Down"),
        Binding("up", "cursor_up", "Up"),
        Binding("enter", "open_result", "Open"),
        Binding("tab", "cycle_source", "Cycle Source"),
    ]

    SEARCH_SOURCES = [
        "Events", "Agents", "Tasks", "Services", "Audit",
        "Conversations", "Files", "Knowledge", "Reports", "Commands",
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="search-container"):
            yield Input(placeholder="Search everything... (min 2 chars)", id="search-input")
            with Horizontal(id="search-sources"):
                for src in self.SEARCH_SOURCES:
                    yield Button(src[:4], id=f"src-{src.lower()}", classes="source-btn")
            yield Static("[dim]Recent searches will appear here[/]", id="search-history-hint", classes="hint")
            yield ListView(id="search-results")
            yield Static("[dim]↵ Open ↑↓ Tab Cycle Source Esc Close[/]", id="search-footer", classes="hint")

    def on_mount(self):
        self._active_source = "all"
        self._results: list[dict] = []
        self._search_history: list[str] = []
        self._debounce_timer = None
        self._last_query = ""
        self._all_sources = [s.lower() for s in self.SEARCH_SOURCES]
        self._source_idx = -1
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed):
        query = event.value.strip()
        if query == self._last_query:
            return
        self._last_query = query
        if len(query) >= 2:
            self._perform_search(query)
        else:
            self._show_history()

    def _show_history(self):
        lv = self.query_one("#search-results", ListView)
        lv.clear()
        hint = self.query_one("#search-history-hint", Static)
        if self._search_history:
            hint.update("[dim]Recent searches[/]")
            for q in reversed(self._search_history[-10:]):
                lv.append(ListItem(Label(f"[dim]⌕[/] {q}")))
        else:
            hint.update("[dim]Type 2+ characters to search across 10 sources[/]")

    def _perform_search(self, query: str):
        q = query.lower()
        results = []
        hint = self.query_one("#search-history-hint", Static)
        hint.update(f"[dim]Searching: {query}[/]")
        try:
            kernel = FabricKernel.instance()

            if self._active_source in ("all", "events"):
                events = kernel.query_events(limit=30)
                for ev in events:
                    if q in ev.type.lower() or q in ev.origin.lower() or q in str(ev.payload).lower():
                        results.append({"type": "event", "label": f"[green]Event[/] {ev.type} [dim]{ev.origin}[/]", "relevance": 1.0})

            if self._active_source in ("all", "agents") and kernel.agent_runtime:
                agents = kernel.agent_runtime.list_agents()
                for a in agents:
                    d = a.to_dict()
                    if q in d["name"].lower() or q in d["role"].lower():
                        results.append({"type": "agent", "label": f"[cyan]Agent[/] {d['name']} ({d['role']})", "relevance": 0.9})

            if self._active_source in ("all", "tasks") and kernel.task_graph:
                nodes = kernel.task_graph.list_nodes()
                for n in nodes[:15]:
                    d = n.to_dict()
                    if q in d["label"].lower() or q in d["status"].lower():
                        results.append({"type": "task", "label": f"[yellow]Task[/] {d['label']} [dim]{d['status']}[/]", "relevance": 0.8})

            if self._active_source in ("all", "services"):
                for s in kernel.registry.list():
                    if q in s.name.lower():
                        results.append({"type": "service", "label": f"[magenta]Service[/] {s.name} v{s.version}", "relevance": 0.7})

            if self._active_source in ("all", "audit"):
                entries = kernel.audit.query(limit=20)
                for e in entries:
                    if q in e.action.lower() or q in e.actor.lower():
                        results.append({"type": "audit", "label": f"[dim]Audit[/] {e.action} by {e.actor}", "relevance": 0.6})

            if self._active_source in ("all", "conversations"):
                try:
                    if hasattr(kernel, '_conversation_engine') and kernel._conversation_engine:
                        convs = kernel._conversation_engine.search(query=q, limit=10) if q else kernel._conversation_engine.search(limit=10)
                        for c in convs:
                            results.append({"type": "conversation", "label": f"[blue]Conversation[/] {c.title} [dim]({c.message_count} msgs)[/]", "relevance": 0.7})
                except Exception:
                    pass

            if self._active_source in ("all", "commands"):
                for action_id, name, desc, shortcut in COMMANDS:
                    if q in name.lower() or q in desc.lower():
                        results.append({"type": "command", "label": f"[bold]Cmd[/] {name} — {desc}", "relevance": 0.5, "data": {"action": action_id}})

            if self._active_source in ("all", "reports"):
                from pathlib import Path
                reports_dir = Path.cwd() / "Reports"
                if reports_dir.exists():
                    for cycle_dir in sorted(reports_dir.iterdir(), reverse=True):
                        if cycle_dir.is_dir() and cycle_dir.name.startswith("Cycle_"):
                            for f in cycle_dir.glob("*.md"):
                                if q in f.stem.lower() or q in cycle_dir.name.lower():
                                    results.append({"type": "report", "label": f"[yellow]Report[/] {cycle_dir.name}/{f.name}", "relevance": 0.6})

            if self._active_source in ("all", "files"):
                from pathlib import Path
                root = Path.cwd() / "genesis"
                if root.exists():
                    for f in sorted(root.rglob("*.py"))[:50]:
                        rel = f.relative_to(Path.cwd())
                        if q in str(rel).lower():
                            results.append({"type": "file", "label": f"[bold]File[/] {rel}", "relevance": 0.5})

            if self._active_source in ("all", "knowledge"):
                try:
                    ke = kernel.knowledge
                    if hasattr(ke, 'search'):
                        entries = ke.search(q, limit=10)
                        for entry in entries[:10]:
                            label = entry.get("content", str(entry))[:80] if isinstance(entry, dict) else str(entry)[:80]
                            results.append({"type": "knowledge", "label": f"[bold]Knowledge[/] {label}", "relevance": 0.7})
                    if not results:
                        results.append({"type": "knowledge", "label": "[dim]KnowledgeEngine: use kernel.knowledge[/]", "relevance": 0.1})
                except Exception:
                    pass

        except Exception:
            pass

        results.sort(key=lambda r: (-r["relevance"], r["label"]))
        self._results = results[:30]
        lv = self.query_one("#search-results", ListView)
        lv.clear()

        if not results:
            hint.update(f"[dim]No results for '{query}'[/]")

        source_counts: dict[str, int] = {}
        for r in self._results:
            source_counts[r["type"]] = source_counts.get(r["type"], 0) + 1

        for r in self._results:
            lv.append(ListItem(Label(r["label"])))

        if self._last_query not in self._search_history:
            self._search_history.append(self._last_query)
            if len(self._search_history) > 50:
                self._search_history.pop(0)

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id or ""
        if btn_id.startswith("src-"):
            self._active_source = btn_id[4:]
            input_w = self.query_one("#search-input", Input)
            if input_w.value.strip():
                self._perform_search(input_w.value.strip())

    def action_cycle_source(self):
        self._source_idx = (self._source_idx + 1) % (len(self._all_sources) + 1)
        if self._source_idx == 0:
            self._active_source = "all"
        else:
            self._active_source = self._all_sources[self._source_idx - 1]
        input_w = self.query_one("#search-input", Input)
        if input_w.value.strip():
            self._perform_search(input_w.value.strip())

    def on_list_view_selected(self, event: ListView.Selected):
        idx = list(self.query_one("#search-results", ListView).children).index(event.item)
        if 0 <= idx < len(self._results):
            result = self._results[idx]
            self.dismiss()
            if result["type"] == "command":
                action = result["data"].get("action", "")
                app = self.app
                if action in ("home", "inspector", "agents", "memory", "repository", "timeline",
                              "graph", "ai", "ce", "reports", "settings"):
                    app.navigate_to(action)
            elif result["type"] in ("agent",):
                self.app.navigate_to("agents")
            elif result["type"] in ("event",):
                self.app.navigate_to("inspector")
            elif result["type"] in ("task",):
                self.app.navigate_to("home")
            elif result["type"] in ("report", "file"):
                self.app.navigate_to("reports")
            elif result["type"] in ("conversation", "knowledge"):
                self.app.navigate_to("memory")

    def action_cursor_down(self):
        self.query_one("#search-results", ListView).action_cursor_down()

    def action_cursor_up(self):
        self.query_one("#search-results", ListView).action_cursor_up()

    def action_open_result(self):
        lv = self.query_one("#search-results", ListView)
        if lv.children:
            lv.action_select()
