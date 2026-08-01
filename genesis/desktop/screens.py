"""Cycle 012 — All Genesis Desktop screens. Real-time, collaborative, explorable, alive."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

try:
    from textual.app import ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical, ScrollableContainer
    from textual.screen import Screen
    from textual.widgets import (
        Input, Label, ListItem, ListView,
        RichLog, Static, Tree,
    )
except ImportError:
    raise ImportError("Textual is required. Install with: pip install textual")

from genesis.fabric.kernel import FabricKernel
from genesis.desktop.widgets import (
    _DRIVEN_INTERVAL, _subscribe_events, _unsubscribe_events,
    AgentCollaborationGraph, AgentListView, AttentionWidget,
    CopilotSuggestions, DataPanel, EventLog, FabricTrafficLight,
    LiveActivityFeed, MetricsTimeline, SectionTitle, SessionTimeline,
    StatusBar, TaskSummary,
    AGENT_STATUS_COLOR, AGENT_STATUS_MARK, CONNECTION_STATUS_COLOR,
    EVENT_SEVERITY_COLOR, TASK_STATUS_COLOR,
)


# ══════════════════════════════════════════════════════════════════════════════
# M78 — Fabric Inspector
# ══════════════════════════════════════════════════════════════════════════════

class FabricInspectorScreen(Screen):
    """M78 — Watch events move through Genesis in real time."""
    screen_id = "inspector"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("e", "show_events", "Events"),
        Binding("m", "show_metrics", "Metrics"),
        Binding("s", "show_sessions", "Sessions"),
    ]

    VIEWS = ["events", "metrics", "sessions"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Fabric Inspector[/]", id="fi-title")
            yield Static("[dim]Real-time event flow | Latency | Throughput | [E]vents [M]etrics [S]essions",
                         id="fi-subtitle")
            with Horizontal():
                with Vertical(id="fi-traffic"):
                    yield SectionTitle("Traffic")
                    yield FabricTrafficLight(id="fi-traffic-light")
                    yield LiveActivityFeed(id="fi-activity", max_lines=15, highlight=True)
                with Vertical(id="fi-detail"):
                    yield SectionTitle("Event Stream")
                    yield RichLog(id="fi-event-stream", max_lines=30, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._view = "events"
        self._last_count = 0
        self._handler = _subscribe_events(self, self._refresh)
        self._refresh()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh(self):
        log = self.query_one("#fi-event-stream", RichLog)
        if self._view != "events":
            return
        try:
            kernel = FabricKernel.instance()
            count = kernel.event_store.count()
            if count > self._last_count:
                events = kernel.query_events(limit=15)
                log.clear()
                log.write("[bold]Event Flow[/]")
                ev_types = kernel.event_store.count_by_type()
                log.write(f"  Types: {', '.join(f'{t}({c})' for t, c in sorted(ev_types.items(), key=lambda x: -x[1])[:8])}")
                log.write("")
                for ev in reversed(events):
                    color = EVENT_SEVERITY_COLOR.get(ev.severity.value, "white")
                    age = time.time() - ev.timestamp
                    log.write(f"  [{color}]→[/] [{color}]{ev.type:<30}[/] [dim]{ev.origin:<15} {age:.1f}s ago corr={ev.correlation_id[:12]}[/]")
                self._last_count = count
        except Exception:
            log.write("  [dim]No events available[/]")

    def action_show_events(self):
        self._view = "events"
        self._last_count = 0

    def action_show_metrics(self):
        self._view = "metrics"
        log = self.query_one("#fi-event-stream", RichLog)
        log.clear()
        try:
            kernel = FabricKernel.instance()
            s = kernel.stats()
            m = kernel.metrics.snapshot()
            log.write("[bold]Fabric Metrics[/]")
            log.write(f"  State: {s.state}")
            log.write(f"  Uptime: {s.uptime_seconds:.0f}s")
            log.write(f"  Events delivered: {s.events_delivered}")
            log.write(f"  Events stored: {s.event_store_count}")
            log.write(f"  Services: {s.services}")
            log.write(f"  Sessions: {s.active_sessions}")
            log.write(f"  Threads: {s.threads}")
            log.write(f"  Executor: {'running' if s.executor_running else 'stopped'}")
            log.write(f"  Executor OK: {s.executor_executions}")
            log.write(f"  Executor Fail: {s.executor_failed}")
            log.write("")
            log.write("[bold]Histogram Details[/]")
            for name in m.get("histogram_names", []):
                h = kernel.metrics.histogram(name)
                if h:
                    log.write(f"  {name}: min={h['min']:.2f} avg={h['avg']:.2f} max={h['max']:.2f} p95={h['p95']:.2f}")
        except Exception:
            pass

    def action_show_sessions(self):
        self._view = "sessions"
        log = self.query_one("#fi-event-stream", RichLog)
        log.clear()
        try:
            kernel = FabricKernel.instance()
            log.write("[bold]Active Sessions[/]")
            for sid, ctx in kernel._contexts.items():
                st = ctx.get("session_type", "?")
                started = ctx.get("started_at", 0)
                age = time.time() - started
                log.write(f"  [dim]{sid}[/] {st} [dim]({age:.0f}s old)[/]")
            if not kernel._contexts:
                log.write("  [dim]No active sessions[/]")
            log.write("")
            log.write("[bold]Scheduled Tasks[/]")
            tasks = kernel.scheduler.list_tasks()
            for t in tasks:
                log.write(f"  {t.name}: interval={t.interval_secs}s runs={t.run_count} errors={t.error_count}")
            if not tasks:
                log.write("  [dim]No scheduled tasks[/]")
        except Exception:
            pass

    def action_refresh(self):
        self._refresh()


# ══════════════════════════════════════════════════════════════════════════════
# M110 — Genesis Home: What should I work on next?
# ══════════════════════════════════════════════════════════════════════════════

class GenesisHome(Screen):
    """M110 — Engineering Home. Immediately answers: What should I work on next?"""
    screen_id = "home"

    BINDINGS = [
        Binding("ctrl+k", "command_palette", "Palette"),
        Binding("ctrl+p", "search_everywhere", "Search"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(id="home-title")
            yield Static(id="home-subtitle")
            with Horizontal():
                with Vertical(id="home-left"):
                    yield SectionTitle("Requires Attention")
                    yield AttentionWidget(id="home-attention")
                    yield SectionTitle("Activity")
                    yield LiveActivityFeed(id="home-activity", max_lines=10, highlight=True)
                with Vertical(id="home-center"):
                    yield SectionTitle("Active Agents")
                    yield AgentListView(id="home-agents")
                    yield SectionTitle("Tasks")
                    yield TaskSummary(id="home-tasks")
                with Vertical(id="home-right"):
                    yield SectionTitle("Live Events")
                    yield EventLog(id="home-events", max_lines=14, highlight=True)
                    yield SectionTitle("Sessions")
                    yield SessionTimeline(id="home-sessions")
                    yield CopilotSuggestions(id="home-copilot")
            yield StatusBar()

    def on_mount(self):
        self._greeting()
        self._handler = _subscribe_events(self, self._refresh_home)
        self._refresh_home()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_home)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _greeting(self):
        kernel = FabricKernel.instance()
        h = kernel.health()
        uptime = h.uptime_seconds if h else 0
        title = self.query_one("#home-title", Static)
        subtitle = self.query_one("#home-subtitle", Static)
        hours = int(uptime // 3600)
        mins = int((uptime % 3600) // 60)
        title.update(f"[bold white]Genesis Home[/]")
        subtitle.update(f"[dim]Uptime: {hours}h {mins}m  |  Ctrl+K: Commands  Ctrl+P: Search  Ctrl+R: Refresh[/]")

    def _refresh_home(self):
        try:
            self.query_one("#home-attention", AttentionWidget)._refresh_content()
        except Exception:
            pass
        try:
            self.query_one("#home-agents", AgentListView).refresh_agents()
        except Exception:
            pass
        try:
            self.query_one("#home-events", EventLog).poll_events()
        except Exception:
            pass
        try:
            self.query_one("#home-activity", LiveActivityFeed).poll()
        except Exception:
            pass
        try:
            self.query_one("#home-tasks", TaskSummary)._update_display()
        except Exception:
            pass
        try:
            self.query_one("#home-sessions", SessionTimeline)._refresh_content()
        except Exception:
            pass

    def action_command_palette(self):
        self.app.push_screen(CommandPalette())

    def action_search_everywhere(self):
        self.app.push_screen(SearchEverywhere())

    def action_refresh(self):
        self._refresh_home()


# ══════════════════════════════════════════════════════════════════════════════
# M80 — Agent Collaboration Visualizer
# ══════════════════════════════════════════════════════════════════════════════

class AgentCollaborationScreen(Screen):
    """M80 — See AI agents working together. Hierarchy, delegation, reasoning, metrics."""
    screen_id = "agents"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("p", "pause_selected", "Pause"),
        Binding("s", "resume_selected", "Resume"),
        Binding("t", "terminate_selected", "Terminate"),
        Binding("d", "show_delegation", "Delegation"),
        Binding("c", "show_conversations", "Conversations"),
    ]

    VIEWS = ["agents", "delegation", "conversations"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Agent Collaboration[/]", id="collab-title")
            yield Static("[dim]Hierarchy | Delegation | Conversations | Metrics | [P]ause [S]resume [T]erminate",
                         id="collab-subtitle")
            yield Static("[dim][D]elegation  [C]onversations  Click agent for detail  [R]efresh",
                         id="collab-legend")
            with Horizontal():
                with Vertical(id="collab-left"):
                    yield AgentCollaborationGraph(id="collab-graph")
                    yield SectionTitle("Agent List")
                    yield ListView(id="collab-list")
                with Vertical(id="collab-right"):
                    yield SectionTitle("Agent Detail")
                    yield RichLog(id="collab-detail", max_lines=40, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._selected_agent: Any = None
        self._view = "agents"
        self._handler = _subscribe_events(self, self._refresh_agents)
        self._refresh_agents()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_agents)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_agents(self):
        try:
            kernel = FabricKernel.instance()
            lv = self.query_one("#collab-list", ListView)
            lv.clear()
            if kernel.agent_runtime:
                agents = kernel.agent_runtime.list_agents()
                detail = self.query_one("#collab-detail", RichLog)
                for a in agents:
                    d = a.to_dict()
                    status_mark = AGENT_STATUS_MARK.get(d["status"], "?")
                    status_color = AGENT_STATUS_COLOR.get(d["status"], "white")
                    lv.append(ListItem(
                        Label(f" [{status_color}]{status_mark}[/] [bold]{d['name']}[/] [dim]{d['role']}[/] "
                              f"tasks:{d['task_count']} ✓{d['completed_count']} ✗{d['failed_count']}"),
                        id=f"collab-agent-{d['agent_id']}",
                    ))
                if agents:
                    detail.write("[bold]Agent Ecosystem[/]")
                    detail.write(f"  {len(agents)} agents active")
                    by_status = defaultdict(int)
                    for a in agents:
                        by_status[a.to_dict()["status"]] += 1
                    for status, count in by_status.items():
                        detail.write(f"  {status}: {count}")
                    detail.write("")
                    detail.write("[bold]Collaboration[/]")
                    detail.write("  Agents communicate via the Fabric MessageBus")
                    detail.write("  Task delegation through TaskGraph dependencies")
                    detail.write("  Conversations through ConversationEngine")
                    detail.write("")
                    detail.write("[bold]Keys:[/] [P]ause [S]resume [T]erminate [D]elegation [C]onversations")
            if not lv.children:
                lv.append(ListItem(Label("[dim]No agents registered[/]")))
        except Exception:
            pass

    def on_list_view_selected(self, event: ListView.Selected):
        item_id = event.item.id or ""
        if item_id.startswith("collab-agent-"):
            agent_id = item_id[14:]
            kernel = FabricKernel.instance()
            detail = self.query_one("#collab-detail", RichLog)
            detail.clear()
            try:
                agent = kernel.agent_runtime.get_agent(agent_id)
                if agent:
                    d = agent.to_dict()
                    detail.write(f"[bold]Agent:[/] {d['name']}")
                    detail.write(f"[bold]ID:[/] {d['agent_id']}")
                    detail.write(f"[bold]Role:[/] {d['role']}")
                    detail.write(f"[bold]Status:[/] [{self._sc(d['status'])}]{d['status']}[/]")
                    detail.write(f"[bold]Model:[/] {d.get('model', 'default')}")
                    detail.write(f"[bold]Provider:[/] {d.get('provider', 'default')}")
                    detail.write(f"[bold]Tasks:[/] {d['task_count']} total, {d['completed_count']} done, {d['failed_count']} fail")
                    detail.write("")
                    if d.get("current_task"):
                        detail.write(f"[bold]Current Task:[/] {d['current_task']['objective']}")
                        detail.write(f"  Status: {d['current_task']['status']}")
                    detail.write("")
                    detail.write("[bold]Performance[/]")
                    detail.write(f"  Completion rate: {d['completed_count']/max(d['task_count'],1)*100:.0f}%")
                    detail.write(f"  Failure rate: {d['failed_count']/max(d['task_count'],1)*100:.0f}%")
                    detail.write("")
                    detail.write("[dim]Keys: [P]ause [S]resume [T]erminate[/]")
                    self._selected_agent = agent
                else:
                    detail.write(f"[dim]Agent {agent_id} not found[/]")
            except Exception as e:
                detail.write(f"[red]Error: {e}[/]")

    def action_pause_selected(self):
        if self._selected_agent:
            try:
                self._selected_agent.pause()
                self.app.notify("Agent paused", severity="information")
            except Exception as e:
                self.app.notify(f"Pause failed: {e}", severity="error")

    def action_resume_selected(self):
        if self._selected_agent:
            try:
                self._selected_agent.resume()
                self.app.notify("Agent resumed", severity="information")
            except Exception as e:
                self.app.notify(f"Resume failed: {e}", severity="error")

    def action_terminate_selected(self):
        if self._selected_agent:
            try:
                self._selected_agent.terminate()
                self.app.notify("Agent terminated", severity="warning")
                self._selected_agent = None
            except Exception as e:
                self.app.notify(f"Terminate failed: {e}", severity="error")

    def action_show_delegation(self):
        self._view = "delegation"
        detail = self.query_one("#collab-detail", RichLog)
        detail.clear()
        detail.write("[bold]Delegation Graph[/]")
        detail.write("  Agents delegate tasks through the TaskGraph")
        detail.write("  Ready tasks: waiting for execution")
        detail.write("  Blocked tasks: waiting for dependencies")
        detail.write("  Running tasks: currently executing")
        try:
            kernel = FabricKernel.instance()
            if kernel.task_graph:
                s = kernel.task_graph.summary()
                detail.write("")
                detail.write(f"[bold]Task Graph Summary[/]")
                detail.write(f"  Total: {s['total_nodes']}")
                for status, count in s.get("by_status", {}).items():
                    detail.write(f"  {status}: {count}")
                detail.write(f"  Critical path: {s['critical_path_length']} steps")
        except Exception:
            pass

    def action_show_conversations(self):
        self._view = "conversations"
        detail = self.query_one("#collab-detail", RichLog)
        detail.clear()
        detail.write("[bold]Agent Conversations[/]")
        try:
            kernel = FabricKernel.instance()
            if kernel._conversation_engine:
                cs = kernel._conversation_engine.summary()
                detail.write(f"  Total conversations: {cs['total_conversations']}")
                detail.write(f"  Total messages: {cs['total_messages']}")
                detail.write("")
                convs = kernel._conversation_engine.search(limit=10)
                for c in convs:
                    age = time.time() - c.updated_at
                    detail.write(f"  [bold]{c.title}[/] [dim]({c.message_count} msgs, "
                                 f"{len(c.participants)} participants, {age:.0f}s ago)[/]")
            else:
                detail.write("  [dim]Conversation engine not initialized[/]")
        except Exception:
            detail.write("  [dim]Conversations not available[/]")

    def action_refresh(self):
        self._refresh_agents()

    def _sc(self, status: str) -> str:
        return AGENT_STATUS_COLOR.get(status, "white")


# ══════════════════════════════════════════════════════════════════════════════
# M81 — Engineering Memory Explorer
# ══════════════════════════════════════════════════════════════════════════════

class EngineeringMemoryExplorer(Screen):
    """M81 — Browse reports, decisions, experiments, architecture history. Everything navigable."""
    screen_id = "memory"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("e", "show_events", "Events"),
        Binding("a", "show_audit", "Audit"),
        Binding("c", "show_conversations", "Conversations"),
        Binding("t", "show_tasks", "Tasks"),
        Binding("p", "show_reports", "Reports"),
        Binding("d", "show_decisions", "Decisions"),
        Binding("slash", "filter", "Filter"),
    ]

    VIEWS = ["events", "audit", "conversations", "tasks", "reports", "decisions"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Engineering Memory Explorer[/]", id="mem-title")
            yield Static("[dim][E]vents [A]udit [C]onversations [T]asks [R]eports [D]ecisions [/] Press [/] filter",
                         id="mem-subtitle")
            yield Input(placeholder="Filter memory...", id="mem-filter")
            with Horizontal():
                with Vertical(id="mem-nav"):
                    yield SectionTitle("Browse")
                    yield ListView(id="mem-nav-list")
                with Vertical(id="mem-content"):
                    yield SectionTitle("Memory Detail")
                    yield RichLog(id="mem-detail", max_lines=45, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._view = "events"
        self._filter_text = ""
        self._handler = _subscribe_events(self, self._refresh_memory)
        self._refresh_memory()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_memory)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_memory(self):
        kernel = FabricKernel.instance()
        nav = self.query_one("#mem-nav-list", ListView)
        detail = self.query_one("#mem-detail", RichLog)
        nav.clear()
        detail.clear()
        q = self._filter_text.lower()

        detail.write(f"[bold]{self._view.title()}[/]")
        detail.write("")

        if self._view == "events":
            try:
                events = kernel.query_events(limit=50)
                for ev in reversed(events):
                    color = EVENT_SEVERITY_COLOR.get(ev.severity.value, "white")
                    age = time.time() - ev.timestamp
                    age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                    line = f"  [{color}]•[/] [{color}]{ev.type:<35}[/] [dim]{ev.origin:<20} {age_str:>8}[/]"
                    if not q or q in line.lower():
                        detail.write(line)
                        nav.append(ListItem(Label(f"[{color}]{ev.type}[/] [dim]{age_str}[/]")))
            except Exception:
                detail.write("  [dim]No events available[/]")

        elif self._view == "audit":
            try:
                entries = kernel.audit.query(limit=50)
                for e in entries:
                    age = time.time() - e.timestamp
                    age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                    sev_color = EVENT_SEVERITY_COLOR.get(e.severity, "white")
                    line = f"  [dim]{age_str:>8}[/] [{sev_color}]{e.action:<35}[/] [dim]{e.actor}[/]"
                    if not q or q in line.lower():
                        detail.write(line)
                        nav.append(ListItem(Label(f"[{sev_color}]{e.action}[/] [dim]{age_str}[/]")))
            except Exception:
                detail.write("  [dim]No audit entries[/]")

        elif self._view == "conversations":
            try:
                if kernel._conversation_engine:
                    convs = kernel._conversation_engine.search(limit=20)
                    for c in convs:
                        age = time.time() - c.updated_at
                        age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                        line = f"  [bold]{c.title:<30}[/] [dim]{c.message_count} msgs, {len(c.participants)} participants, {age_str}[/]"
                        if not q or q in line.lower():
                            detail.write(line)
                            nav.append(ListItem(Label(f"{c.title} [dim]({c.message_count} msgs)[/]")))
                else:
                    detail.write("  [dim]Conversation engine not initialized[/]")
            except Exception:
                detail.write("  [dim]Conversations not available[/]")

        elif self._view == "tasks":
            try:
                if kernel.task_graph:
                    s = kernel.task_graph.summary()
                    detail.write(f"Total: {s['total_nodes']}")
                    nav.append(ListItem(Label(f"Total: {s['total_nodes']}")))
                    for status, count in s.get("by_status", {}).items():
                        detail.write(f"  {status}: {count}")
                        nav.append(ListItem(Label(f"{status}: {count}")))
                    detail.write(f"Critical path: {s['critical_path_length']} steps")
                    detail.write("")
                    nodes = kernel.task_graph.list_nodes()
                    for n in nodes[:30]:
                        d = n.to_dict()
                        age = time.time() - d.get("created_at", time.time())
                        age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                        status_color = TASK_STATUS_COLOR.get(d["status"], "white")
                        line = f"  [{status_color}]{d['label']:<30}[/] [dim]{d['status']:<10} {age_str}[/]"
                        if not q or q in line.lower():
                            detail.write(line)
                else:
                    detail.write("  [dim]Task graph not initialized[/]")
            except Exception:
                detail.write("  [dim]Tasks not available[/]")

        elif self._view == "reports":
            detail.write("[bold]Engineering Reports[/]")
            reports_dir = Path.cwd() / "Reports"
            if reports_dir.exists():
                for cycle_dir in sorted(reports_dir.iterdir(), reverse=True):
                    if cycle_dir.is_dir() and cycle_dir.name.startswith("Cycle_"):
                        files = list(cycle_dir.glob("*.md"))
                        nav.append(ListItem(Label(f"[bold]{cycle_dir.name}[/] ({len(files)} reports)")))
                        detail.write(f"  [bold]{cycle_dir.name}[/]")
                        for fname in sorted(f.name for f in files):
                            line = f"    📄 {fname}"
                            if not q or q in line.lower():
                                detail.write(line)
            else:
                detail.write("  [dim]No reports directory[/]")

        elif self._view == "decisions":
            detail.write("[bold]Engineering Decisions[/]")
            detail.write("  (Extracted from audit log and reports)")
            try:
                entries = kernel.audit.query(limit=30)
                for e in entries:
                    if any(kw in e.action.lower() for kw in ["decision", "approved", "rejected", "policy"]):
                        line = f"  [bold]{e.action}[/] by {e.actor} — {e.detail}"
                        if not q or q in line.lower():
                            detail.write(line)
            except Exception:
                detail.write("  [dim]No decisions found[/]")

        if not nav.children:
            nav.append(ListItem(Label("[dim]No results[/]")))

    def action_show_events(self):
        self._view = "events"
        self._refresh_memory()

    def action_show_audit(self):
        self._view = "audit"
        self._refresh_memory()

    def action_show_conversations(self):
        self._view = "conversations"
        self._refresh_memory()

    def action_show_tasks(self):
        self._view = "tasks"
        self._refresh_memory()

    def action_show_reports(self):
        self._view = "reports"
        self._refresh_memory()

    def action_show_decisions(self):
        self._view = "decisions"
        self._refresh_memory()

    def action_filter(self):
        self.query_one("#mem-filter", Input).focus()

    def on_input_submitted(self, event: Input.Submitted):
        self._filter_text = event.value
        self._refresh_memory()

    def action_refresh(self):
        self._refresh_memory()


# ══════════════════════════════════════════════════════════════════════════════
# M69 — Repository Intelligence (enhanced)
# ══════════════════════════════════════════════════════════════════════════════

class RepositoryScreen(Screen):
    """M69 — Repository cockpit with file tree, architecture, health, dependencies."""
    screen_id = "repository"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "toggle_file_tree", "File Tree"),
        Binding("a", "toggle_architecture", "Architecture"),
        Binding("h", "toggle_health", "Health"),
    ]

    VIEWS = ["files", "architecture", "health"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Repository Intelligence[/]", id="repo-title")
            yield Static("[dim][F]ile Tree [A]rchitecture [H]ealth [R]efresh Esc back",
                         id="repo-subtitle")
            with Horizontal():
                with Vertical(id="repo-file-tree-panel"):
                    yield SectionTitle("Files")
                    yield Tree("Repository", id="file-tree")
                with Vertical(id="repo-info-panel"):
                    yield SectionTitle("Knowledge")
                    yield RichLog(id="repo-content", max_lines=40, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._mode = "files"
        self._refresh_repo()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_repo)

    def _refresh_repo(self):
        kernel = FabricKernel.instance()
        info = self.query_one("#repo-content", RichLog)
        tree = self.query_one("#file-tree", Tree)
        tree.clear()
        info.clear()
        repo_root = Path.cwd()

        if self._mode == "files":
            tree.root.label = repo_root.name
            try:
                for child in sorted(repo_root.iterdir()):
                    if child.name.startswith(".") or child.name.startswith("__pycache__"):
                        continue
                    if child.is_dir():
                        subtree = tree.root.add(f"📁 {child.name}", expanded=False)
                        try:
                            for sub in sorted(child.iterdir()):
                                if not sub.name.startswith(".") and not sub.name.startswith("__pycache__"):
                                    subtree.add_leaf(f"📄 {sub.name}" if not sub.is_dir() else f"📁 {sub.name}")
                        except PermissionError:
                            subtree.add_leaf("[dim]restricted[/]")
                    else:
                        tree.root.add_leaf(f"📄 {child.name}")
            except Exception:
                tree.root.add("[dim]Could not scan files[/]")

            info.write("[bold]Repository Health[/]")
            info.write(f"  Watchers: tracking {repo_root.name}")
            try:
                from genesis.watch import ContinuousEngineering
                if hasattr(kernel, '_continuous_engineering') and kernel._continuous_engineering:
                    ce = kernel._continuous_engineering
                    states = ce.states()
                    for name, state in states.items():
                        info.write(f"  {name}: scans={state.scan_count} changes={state.change_count}")
                else:
                    info.write("  [dim]No watchers active (Ctrl+K → Start CE)[/]")
            except Exception:
                info.write("  [dim]Watchers not available[/]")

        elif self._mode == "architecture":
            info.write("[bold]Architecture Overview[/]")
            info.write("")
            info.write("[dim]Fabric Layers:[/]")
            info.write("   Fabric Kernel    — genesis/fabric/")
            info.write("   Message Bus      — genesis/fabric/bus.py")
            info.write("   Event Router     — genesis/fabric/events.py")
            info.write("   Agent Runtime    — genesis/fabric/agents.py")
            info.write("   Task Graph       — genesis/fabric/tasks.py")
            info.write("   Storage          — genesis/fabric/storage.py")
            info.write("")
            info.write("[bold]Service Count:[/]")
            info.write(f"  {kernel.registry.count()} registered services")

        elif self._mode == "health":
            info.write("[bold]System Health[/]")
            h = kernel.health()
            info.write(f"  Kernel: {h.status}")
            info.write(f"  Uptime: {h.uptime_seconds:.0f}s")
            info.write(f"  Services: {h.services_count}")
            info.write(f"  Messages: {h.messages_sent}")
            info.write(f"  Sessions: {h.active_sessions}")
            info.write(f"  Threads: {h.threads}")
            s = kernel.stats()
            info.write(f"  Events: {s.events_delivered}")
            info.write(f"  Executor: {'running' if s.executor_running else 'stopped'}")

    def action_toggle_file_tree(self):
        self._mode = "files"
        self._refresh_repo()

    def action_toggle_architecture(self):
        self._mode = "architecture"
        self._refresh_repo()

    def action_toggle_health(self):
        self._mode = "health"
        self._refresh_repo()

    def action_refresh(self):
        self._refresh_repo()

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        info = self.query_one("#repo-content", RichLog)
        info.clear()
        info.write(f"[bold]Selected:[/] {event.node.label}")
        info.write(f"[dim]Depth: {event.node._depth}[/]")
        if event.node.children:
            info.write(f"[dim]Children: {len(event.node.children)}[/]")


# ══════════════════════════════════════════════════════════════════════════════
# M71 — Engineering Timeline (enhanced)
# ══════════════════════════════════════════════════════════════════════════════

class EngineeringTimelineScreen(Screen):
    """M71 — Canonical engineering history with filtering, replay, and inspection."""
    screen_id = "timeline"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("e", "show_events", "Events"),
        Binding("a", "show_audit", "Audit"),
        Binding("c", "show_conversations", "Conversations"),
        Binding("t", "show_tasks", "Tasks"),
        Binding("r", "refresh", "Refresh"),
        Binding("slash", "filter", "Filter"),
    ]

    VIEWS = ["events", "audit", "conversations", "tasks"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Engineering Timeline[/]", id="timeline-title")
            yield Static("[dim][E]vents [A]udit [C]onversations [T]asks [/] [/]filter Esc back",
                         id="timeline-subtitle")
            yield Input(placeholder="Filter timeline...", id="timeline-filter")
            yield RichLog(id="timeline-content", max_lines=50, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._current_view = "events"
        self._filter_text = ""
        self._handler = _subscribe_events(self, self._refresh_timeline)
        self._refresh_timeline()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_timeline)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_timeline(self):
        kernel = FabricKernel.instance()
        log = self.query_one("#timeline-content", RichLog)
        log.clear()
        q = self._filter_text.lower()

        if self._current_view == "events":
            log.write("[bold]Engineering Timeline • Events[/]")
            try:
                tl = kernel.timeline
                if hasattr(tl, 'query'):
                    entries = tl.query(limit=40)
                    for entry in entries:
                        color = EVENT_SEVERITY_COLOR.get(entry.get("severity", "info"), "white")
                        ts = entry.get("timestamp", 0)
                        age = time.time() - ts
                        age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                        ev_type = entry.get("type", entry.get("event_type", "?"))
                        origin = entry.get("origin", entry.get("source", "?"))
                        line = f"  [{color}]•[/] [{color}]{ev_type:<35}[/] [dim]{origin:<20} {age_str:>8}[/]"
                        if not q or q in line.lower():
                            log.write(line)
                else:
                    events = kernel.query_events(limit=40)
                    for ev in reversed(events):
                        color = EVENT_SEVERITY_COLOR.get(ev.severity.value, "white")
                        age = time.time() - ev.timestamp
                        age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                        line = f"  [{color}]•[/] [{color}]{ev.type:<35}[/] [dim]{ev.origin:<20} {age_str:>8}[/]"
                        if not q or q in line.lower():
                            log.write(line)
            except Exception:
                log.write("  [dim]No events available[/]")

        elif self._current_view == "audit":
            log.write("[bold]Audit Trail[/]")
            try:
                entries = kernel.audit.query(limit=40)
                for e in entries:
                    age = time.time() - e.timestamp
                    age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                    sev_color = EVENT_SEVERITY_COLOR.get(e.severity, "white")
                    line = f"  [dim]{age_str:>8}[/] [{sev_color}]{e.action:<35}[/] [dim]{e.actor}[/]"
                    if not q or q in line.lower():
                        log.write(line)
            except Exception:
                log.write("  [dim]No audit entries available[/]")

        elif self._current_view == "conversations":
            log.write("[bold]Conversations[/]")
            try:
                if kernel._conversation_engine:
                    convs = kernel._conversation_engine.search(limit=20)
                    for c in convs:
                        age = time.time() - c.updated_at
                        age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                        line = f"  [bold]{c.title:<30}[/] [dim]{c.message_count} msgs, {len(c.participants)} participants, {age_str}[/]"
                        if not q or q in line.lower():
                            log.write(line)
                else:
                    log.write("  [dim]Conversation engine not initialized[/]")
            except Exception:
                log.write("  [dim]Conversations not available[/]")

        elif self._current_view == "tasks":
            log.write("[bold]Task History[/]")
            try:
                if kernel.task_graph:
                    s = kernel.task_graph.summary()
                    log.write(f"  Total: {s['total_nodes']}  Critical path: {s['critical_path_length']}")
                    nodes = kernel.task_graph.list_nodes()
                    for n in nodes[:30]:
                        d = n.to_dict()
                        age = time.time() - d.get("created_at", time.time())
                        age_str = f"{age:.0f}s ago" if age < 3600 else f"{age/60:.0f}m ago"
                        sc = TASK_STATUS_COLOR.get(d["status"], "white")
                        line = f"  [{sc}]{d['label']:<30}[/] [dim]{d['status']:<10} {age_str}[/]"
                        if not q or q in line.lower():
                            log.write(line)
                else:
                    log.write("  [dim]Task graph not initialized[/]")
            except Exception:
                log.write("  [dim]Tasks not available[/]")

    def action_show_events(self):
        self._current_view = "events"
        self._refresh_timeline()

    def action_show_audit(self):
        self._current_view = "audit"
        self._refresh_timeline()

    def action_show_conversations(self):
        self._current_view = "conversations"
        self._refresh_timeline()

    def action_show_tasks(self):
        self._current_view = "tasks"
        self._refresh_timeline()

    def action_filter(self):
        self.query_one("#timeline-filter", Input).focus()

    def on_input_submitted(self, event: Input.Submitted):
        self._filter_text = event.value
        self._refresh_timeline()

    def action_refresh(self):
        self._refresh_timeline()


# ══════════════════════════════════════════════════════════════════════════════
# M82 — Knowledge Graph 2.0
# ══════════════════════════════════════════════════════════════════════════════

class KnowledgeGraphScreen(Screen):
    """M113 — Entity relationship browser: services, agents, tasks, and their connections."""
    screen_id = "graph"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("s", "show_services", "Services"),
        Binding("a", "show_agents", "Agents"),
        Binding("t", "show_tasks", "Tasks"),
        Binding("c", "show_conversations", "Conversations"),
        Binding("d", "show_dependencies", "Dependencies"),
        Binding("slash", "filter", "Filter"),
    ]

    VIEWS = ["services", "agents", "tasks", "conversations", "dependencies"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Entity Explorer[/]", id="kg-title")
            yield Static("[dim][S]ervices [A]gents [T]asks [C]onversations [D]ependencies [/]filter",
                         id="kg-subtitle")
            yield Input(placeholder="Filter entities...", id="kg-search")
            with Horizontal():
                with Vertical(id="kg-panel-left"):
                    yield Tree("Entities", id="kg-entity-tree")
                with Vertical(id="kg-panel-right"):
                    yield SectionTitle("Details")
                    yield RichLog(id="kg-inspect", max_lines=40, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._view = "services"
        self._filter_text = ""
        self._handler = _subscribe_events(self, self._refresh_graph)
        self._refresh_graph()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_graph)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_graph(self):
        kernel = FabricKernel.instance()
        tree = self.query_one("#kg-entity-tree", Tree)
        inspect = self.query_one("#kg-inspect", RichLog)
        tree.clear()
        inspect.clear()
        q = self._filter_text.lower()

        inspect.write(f"[bold]Entities — {self._view.title()}[/]")
        inspect.write("")

        root = tree.root

        if self._view == "services":
            root.label = "Services"
            for s in kernel.registry.list():
                if q in s.name.lower():
                    node = root.add(f"[magenta]●[/] {s.name} v{s.version}")
                    node.add(f"[dim]ID: {s.instance_id}[/]")
                    node.add(f"[dim]Status: {s.status}[/]")
                    for cap in getattr(s, 'capabilities', []):
                        node.add(f"[dim]Capability: {cap}[/]")

        elif self._view == "agents":
            root.label = "Agents"
            if kernel.agent_runtime:
                agents = kernel.agent_runtime.list_agents()
                for a in agents:
                    d = a.to_dict()
                    if q and q not in d["name"].lower() and q not in d["role"].lower():
                        continue
                    color = AGENT_STATUS_COLOR.get(d["status"], "white")
                    mark = AGENT_STATUS_MARK.get(d["status"], "?")
                    node = root.add(f"[{color}]{mark}[/] {d['name']} [dim]({d['role']})[/]")
                    node.add(f"[dim]Status: [{color}]{d['status']}[/][/]")
                    node.add(f"[dim]Model: {d.get('model', '?')}[/]")
                    node.add(f"[dim]Provider: {d.get('provider', '?')}[/]")
                    node.add(f"[dim]Tasks: {d['task_count']} ({d['completed_count']} done, {d['failed_count']} fail)[/]")
                    if d.get("task_count", 0) > 0:
                        task_n = node.add("[dim]Recent Tasks[/]")
                        for t in d.get("recent_tasks", [])[:5]:
                            task_n.add(f"[dim]{t}[/]")
            else:
                root.add("[dim]No agents registered[/]")

        elif self._view == "tasks":
            root.label = "Tasks"
            if kernel.task_graph:
                nodes = kernel.task_graph.list_nodes()
                for n in nodes[:30]:
                    d = n.to_dict()
                    if q and q not in d["label"].lower() and q not in d["status"].lower():
                        continue
                    color = TASK_STATUS_COLOR.get(d["status"], "white")
                    node = root.add(f"[{color}]◉[/] {d['label']} [dim]({d['status']})[/]")
                    node.add(f"[dim]Type: {d.get('node_type', '?')}[/]")
                    deps = d.get("dependencies", [])
                    if deps:
                        dep_node = node.add(f"[dim]Depends on ({len(deps)})[/]")
                        for dep in deps[:5]:
                            dep_node.add(f"[dim]→ {dep}[/]")
            else:
                root.add("[dim]Task graph not initialized[/]")

        elif self._view == "conversations":
            root.label = "Conversations"
            try:
                if hasattr(kernel, '_conversation_engine') and kernel._conversation_engine:
                    convs = kernel._conversation_engine.search(limit=20)
                    for c in convs:
                        if q and q not in c.title.lower():
                            continue
                        node = root.add(f"[blue]💬[/] {c.title} [dim]({c.message_count} msgs)[/]")
                        node.add(f"[dim]ID: {c.id}[/]")
                        for p in getattr(c, 'participants', [])[:5]:
                            node.add(f"[dim]Participant: {p}[/]")
            except Exception:
                root.add("[dim]Conversation engine not available[/]")

        elif self._view == "dependencies":
            root.label = "Dependency Graph"
            if kernel.task_graph:
                s = kernel.task_graph.summary()
                root.add(f"[bold]Total Nodes:[/] {s['total_nodes']}")
                root.add(f"[bold]Critical Path:[/] {s['critical_path_length']} steps")
                for status, count in s.get("by_status", {}).items():
                    color = TASK_STATUS_COLOR.get(status, "white")
                    root.add(f"[{color}]●[/] {status}: {count}")
                root.add("")
                dep_root = root.add("[bold]Task Dependencies[/]")
                nodes = kernel.task_graph.list_nodes()
                for n in nodes[:15]:
                    d = n.to_dict()
                    color = TASK_STATUS_COLOR.get(d["status"], "white")
                    task_node = dep_root.add(f"[{color}]◉[/] {d['label']}")
                    for dep_id in d.get("dependencies", [])[:5]:
                        task_node.add(f"[dim]→ {dep_id}[/]")
            else:
                root.add("[dim]Task graph not initialized[/]")

        tree.refresh()

    def action_show_services(self):
        self._view = "services"
        self._refresh_graph()

    def action_show_agents(self):
        self._view = "agents"
        self._refresh_graph()

    def action_show_tasks(self):
        self._view = "tasks"
        self._refresh_graph()

    def action_show_conversations(self):
        self._view = "conversations"
        self._refresh_graph()

    def action_show_dependencies(self):
        self._view = "dependencies"
        self._refresh_graph()

    def action_filter(self):
        self.query_one("#kg-search", Input).focus()

    def on_input_submitted(self, event: Input.Submitted):
        self._filter_text = event.value
        self._refresh_graph()

    def action_refresh(self):
        self._refresh_graph()


# ══════════════════════════════════════════════════════════════════════════════
# M83 — AI Orchestration Center
# ══════════════════════════════════════════════════════════════════════════════

class AIOrchestrationCenter(Screen):
    """M83 — Visual provider management with capabilities, routing, benchmarks, health."""
    screen_id = "ai"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]AI Orchestration Center[/]", id="ai-title")
            yield Static("[dim]Providers | Models | Capabilities | Routing | Benchmarks | Health",
                         id="ai-subtitle")
            with Horizontal():
                with Vertical(id="ai-provider-list"):
                    yield SectionTitle("Providers")
                    yield ListView(id="ai-providers-list")
                with Vertical(id="ai-provider-detail"):
                    yield SectionTitle("Provider Detail")
                    yield RichLog(id="ai-detail-content", max_lines=40, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._handler = _subscribe_events(self, self._refresh_providers)
        self._refresh_providers()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_providers)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_providers(self):
        kernel = FabricKernel.instance()
        lv = self.query_one("#ai-providers-list", ListView)
        detail = self.query_one("#ai-detail-content", RichLog)
        lv.clear()
        detail.clear()

        detail.write("[bold]AI Provider Ecosystem[/]")
        detail.write("")

        try:
            ai = kernel.ai
            summary = ai.summarize() if hasattr(ai, 'summarize') else {}
            providers = summary.get("providers", [])
            available = summary.get("available", [])

            if available:
                detail.write(f"[bold]Available Providers:[/] {len(available)}")
                for p_id in available:
                    detail.write(f"  [green]●[/] {p_id}")
            if providers:
                detail.write(f"[bold]Registered Providers:[/] {len(providers)}")
                for p in providers:
                    name = p.get("id", "?")
                    healthy = p.get("healthy", False)
                    status_color = "green" if healthy else "red"
                    models = p.get("models", [])
                    label = f"[{status_color}]●[/] {name} [{status_color}]{'healthy' if healthy else 'unhealthy'}[/]"
                    lv.append(ListItem(Label(label)))
                    detail.write(f"  [{status_color}]●[/] {name} [{status_color}]{'healthy' if healthy else 'unhealthy'}[/]")
                    if models:
                        detail.write(f"     Models: {', '.join(models[:5])}")
            else:
                detail.write("  [dim]No registered providers[/]")
                lv.append(ListItem(Label("[dim]No providers registered[/]")))
        except ImportError:
            detail.write("  [dim]AI Orchestration Engine not available[/]")
        except Exception as e:
            detail.write(f"  [dim]Error: {e}[/]")

        detail.write("")
        detail.write("[bold]Routing & Fallback[/]")
        try:
            if hasattr(ai, 'routing_decision'):
                decision = ai.routing_decision('chat')
                detail.write(f"  Router: active")
                detail.write(f"  Best provider: {decision.provider_id or 'none'}")
                detail.write(f"  Confidence: {decision.confidence:.2f}")
                detail.write(f"  Fallback chain: {', '.join(decision.fallback_chain) or 'none'}")
        except Exception:
            detail.write("  Router: active (default)")

        detail.write("")
        detail.write("[bold]System Integration[/]")
        s = kernel.health()
        detail.write(f"  Services: {s.services_count}")
        detail.write(f"  Messages: {s.messages_sent}")
        detail.write(f"  Sessions: {s.active_sessions}")

    def action_refresh(self):
        self._refresh_providers()


# ══════════════════════════════════════════════════════════════════════════════
# M73 — Continuous Engineering V3
# ══════════════════════════════════════════════════════════════════════════════

class ContinuousEngineeringScreen(Screen):
    """M73/M88 — Enhanced watcher ecosystem with auto-detection, recommendations, notifications."""
    screen_id = "ce"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("s", "start_watchers", "Start"),
        Binding("x", "stop_watchers", "Stop"),
        Binding("w", "toggle_watch", "Watch Mode"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Continuous Engineering V3[/]", id="ce-title")
            yield Static("[dim]Watchers | Auto-detection | Recommendations | [S]tart [X]stop [W]atch [R]efresh",
                         id="ce-subtitle")
            with Horizontal():
                with Vertical(id="ce-watchers"):
                    yield SectionTitle("Watchers")
                    yield RichLog(id="ce-watcher-log", max_lines=30, highlight=True)
                with Vertical(id="ce-events"):
                    yield SectionTitle("Event Stream")
                    yield EventLog(id="ce-event-log", max_lines=25, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._watch_mode = False
        self._handler = _subscribe_events(self, self._refresh_watchers)
        self._refresh_watchers()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_watchers)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_watchers(self):
        kernel = FabricKernel.instance()
        log = self.query_one("#ce-watcher-log", RichLog)
        log.clear()

        log.write("[bold]Watcher Status[/]")
        try:
            from genesis.watch import ContinuousEngineering
            if hasattr(kernel, '_continuous_engineering') and kernel._continuous_engineering:
                ce = kernel._continuous_engineering
                states = ce.states()
                for name, state in states.items():
                    status_icon = "[green]●[/]" if state.active else "[dim]○[/]"
                    log.write(f"  {status_icon} [bold]{name}[/]")
                    log.write(f"     Active: {state.active}")
                    log.write(f"     Scans: {state.scan_count}")
                    log.write(f"     Changes: {state.change_count}")
                    log.write(f"     Errors: {state.error_count}")
                    log.write(f"     Last scan: {state.last_scan:.0f}")
                    log.write("")
                if not states:
                    log.write("  [dim]No watchers running[/]")
                    log.write("  Press [bold]S[/] to start watchers")
                if self._watch_mode:
                    log.write("[bold green]Watch Mode ACTIVE[/] — auto-detecting changes")
            else:
                log.write("  [dim]Continuous Engineering not initialized[/]")
                log.write("  Press [bold]S[/] to start watchers")
        except Exception as e:
            log.write(f"  [dim]Error: {e}[/]")

    def action_start_watchers(self):
        try:
            from genesis.watch import ContinuousEngineering
            kernel = FabricKernel.instance()
            if not hasattr(kernel, '_continuous_engineering') or not kernel._continuous_engineering:
                ce = ContinuousEngineering(kernel)
                ce.setup_defaults(".")
                ce.start_all()
                kernel._continuous_engineering = ce
            else:
                kernel._continuous_engineering.start_all()
            self.app.notify("Continuous Engineering started", severity="information")
            self._refresh_watchers()
        except Exception as e:
            self.app.notify(f"Failed: {e}", severity="error")

    def action_stop_watchers(self):
        try:
            kernel = FabricKernel.instance()
            if hasattr(kernel, '_continuous_engineering') and kernel._continuous_engineering:
                kernel._continuous_engineering.stop_all()
                self.app.notify("Continuous Engineering stopped", severity="information")
                self._refresh_watchers()
        except Exception as e:
            self.app.notify(f"Failed: {e}", severity="error")

    def action_toggle_watch(self):
        self._watch_mode = not self._watch_mode
        self.app.notify(f"Watch mode: {'ON' if self._watch_mode else 'OFF'}", severity="information")
        self._refresh_watchers()

    def action_refresh(self):
        self._refresh_watchers()


# ══════════════════════════════════════════════════════════════════════════════
# Reports Screen (enhanced for Memory Explorer integration)
# ══════════════════════════════════════════════════════════════════════════════

class ReportsScreen(Screen):
    """Engineering Reports — browse cycle reports with full content reading."""
    screen_id = "reports"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Engineering Reports[/]", id="reports-title")
            yield Static("[dim]Browse cycle reports | Institutional knowledge | Esc back",
                         id="reports-subtitle")
            with Horizontal():
                with Vertical(id="reports-cycle-list"):
                    yield SectionTitle("Cycles")
                    yield ListView(id="reports-list")
                with Vertical(id="reports-content"):
                    yield SectionTitle("Report")
                    yield RichLog(id="reports-content-log", max_lines=40, highlight=True)
            yield StatusBar()

    def on_mount(self):
        self._refresh_reports()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_reports)

    def _refresh_reports(self):
        lv = self.query_one("#reports-list", ListView)
        lv.clear()
        reports_dir = Path.cwd() / "Reports"
        if reports_dir.exists():
            cycles = sorted(reports_dir.iterdir(), reverse=True)
            for cycle_dir in cycles:
                if cycle_dir.is_dir() and cycle_dir.name.startswith("Cycle_"):
                    files = list(cycle_dir.glob("*.md"))
                    lv.append(ListItem(
                        Label(f"[bold]{cycle_dir.name}[/] ({len(files)} reports)"),
                        id=f"cycle-{cycle_dir.name}",
                    ))
        if not lv.children:
            lv.append(ListItem(Label("[dim]No reports found[/]")))

    def on_list_view_selected(self, event: ListView.Selected):
        item_id = event.item.id or ""
        if item_id.startswith("cycle-"):
            cycle_name = item_id[6:]
            log = self.query_one("#reports-content-log", RichLog)
            log.clear()
            reports_dir = Path.cwd() / "Reports" / cycle_name
            if reports_dir.exists():
                log.write(f"[bold]{cycle_name}[/]")
                log.write("")
                for report_file in sorted(reports_dir.glob("*.md")):
                    try:
                        content = report_file.read_text()
                        lines = content.split("\n")
                        log.write(f"[bold]{report_file.name}[/]")
                        for line in lines[:5]:
                            if line.strip():
                                log.write(f"  {line[:120]}")
                        log.write("  ...")
                        log.write("")
                    except Exception:
                        pass

    def action_refresh(self):
        self._refresh_reports()


# ══════════════════════════════════════════════════════════════════════════════
# Settings Screen
# ══════════════════════════════════════════════════════════════════════════════

class SettingsScreen(Screen):
    """Workspace settings — kernel, persistence, provider configuration."""
    screen_id = "settings"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Settings[/]", id="settings-title")
            yield Static("[dim]Workspace | Kernel | Persistence | AI Providers | Esc back",
                         id="settings-subtitle")
            with ScrollableContainer():
                yield DataPanel("General", max_lines=10)
                yield DataPanel("Kernel", max_lines=10)
                yield DataPanel("Persistence", max_lines=10)
                yield DataPanel("AI Providers", max_lines=10)
            yield StatusBar()

    def on_mount(self):
        self._load_settings()

    def _load_settings(self):
        kernel = FabricKernel.instance()
        panels = list(self.query(DataPanel))
        settings_data = [
            ("General", [
                "[bold]Workspace:[/] Genesis Desktop",
                f"[bold]Kernel:[/] {kernel.stats().state}",
                f"[bold]Uptime:[/] {kernel.health().uptime_seconds:.0f}s",
                f"[bold]Home:[/] {Path.cwd()}",
            ]),
            ("Kernel", [
                f"[bold]State:[/] {kernel.stats().state}",
                f"[bold]Services:[/] {kernel.registry.count()}",
                f"[bold]Executor:[/] {'running' if kernel.task_executor else 'not started'}",
                f"[bold]Threads:[/] {len(kernel._threads) if hasattr(kernel, '_threads') else 0}",
            ]),
            ("Persistence", [
                f"[bold]Storage:[/] {'connected' if kernel.storage and kernel.storage.connected else 'disconnected'}",
                f"[bold]Path:[/] {getattr(kernel.storage, '_path', 'N/A') if kernel.storage else 'N/A'}",
            ]),
            ("AI Providers", [
                "[bold]Router:[/] active",
                "[bold]Available:[/] check AI Command Center",
            ]),
        ]
        for i, (title, lines) in enumerate(settings_data):
            if i < len(panels):
                panels[i].clear()
                for line in lines:
                    panels[i].write(line)


