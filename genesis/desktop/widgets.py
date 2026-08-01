"""Cycle 014 — Shared widgets, color maps, event-driven subscription helpers."""

from __future__ import annotations

import json
import time
from typing import Any

try:
    from textual import on, work
    from textual.app import ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import (
        Button, Input, Label, ListItem, ListView, RichLog, Static,
    )
    from textual.widget import Widget
except ImportError:
    raise ImportError("Textual is required. Install with: pip install textual")

from genesis.fabric.events import EngineeringEvent
from genesis.fabric.kernel import FabricKernel

# ── Shared Color Maps ──────────────────────────────────────────────────────

AGENT_STATUS_COLOR: dict[str, str] = {
    "idle": "green", "running": "cyan", "error": "red",
    "terminated": "dim", "waiting": "yellow", "blocked": "red",
}

AGENT_STATUS_MARK: dict[str, str] = {
    "idle": "●", "running": "▶", "error": "✗",
    "terminated": "○", "waiting": "◐", "blocked": "◉",
}

EVENT_SEVERITY_COLOR: dict[str, str] = {
    "info": "green", "warning": "yellow", "error": "red",
    "critical": "bold red", "debug": "dim", "trace": "dim",
}

TASK_STATUS_COLOR: dict[str, str] = {
    "pending": "dim", "ready": "yellow", "running": "cyan",
    "completed": "green", "failed": "red", "blocked": "red",
    "skipped": "dim",
}

CONNECTION_STATUS_COLOR: dict[str, str] = {
    "connected": "green", "disconnected": "red", "error": "red",
}


def _subscribe_events(widget, refresh_method, event_type="*"):
    """Subscribe widget to EventRouter events. Returns handler for unsubscribe."""
    kernel = FabricKernel.instance()
    handler = lambda e: widget.call_from_thread(refresh_method)
    kernel.on_event(event_type, handler)
    return handler


def _unsubscribe_events(handler):
    """Unsubscribe a handler from the EventRouter."""
    try:
        FabricKernel.instance().events.unsubscribe(handler)
    except Exception:
        pass


_DRIVEN_INTERVAL = 9999
"""Polling interval fallback (seconds). Widgets primarily use event-driven push."""


class StatusBar(Static):
    """Bottom status bar — kernel state, events, uptime, executor, connections."""

    def on_mount(self):
        self._handler = _subscribe_events(self, self.refresh_state)
        self.set_interval(_DRIVEN_INTERVAL, self.refresh_state)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def refresh_state(self):
        kernel = FabricKernel.instance()
        try:
            stats = kernel.stats()
            executor_info = ""
            if stats.executor_running:
                executor_info = f"  │  Executor: {stats.executor_executions}ok/{stats.executor_failed}fail"
            storage_status = "DB" if kernel.storage and kernel.storage.connected else "NoDB"
            self.update(
                f"  [bold white]Genesis[/]  │  "
                f"State: [{self._state_color(stats.state)}]{stats.state}[/]  │  "
                f"Events: {stats.events_delivered}  │  "
                f"Services: {stats.services}  │  "
                f"Uptime: {stats.uptime_seconds:.0f}s  │  "
                f"Threads: {stats.threads}"
                f"{executor_info}  │  "
                f"[dim]{storage_status}[/]  │  "
                f"[dim]Ctrl+K Palette  Ctrl+P Search[/]"
            )
        except Exception:
            self.update("[dim]Genesis — connecting...[/]")

    def _state_color(self, state: str) -> str:
        return {"running": "green", "booting": "yellow", "degraded": "red", "shutdown": "dim"}.get(state, "white")


class EventLog(RichLog):
    """Live event stream — filtered, color-coded Fabric events."""

    def on_mount(self):
        self._handler = _subscribe_events(self, self.poll_events)
        self.set_interval(_DRIVEN_INTERVAL, self.poll_events)
        self._last_count = 0

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def poll_events(self):
        try:
            kernel = FabricKernel.instance()
            count = kernel.event_store.count()
            if count > self._last_count:
                events = kernel.query_events(limit=10)
                for ev in reversed(events):
                    age = time.time() - ev.timestamp
                    if age < 120:
                        color = EVENT_SEVERITY_COLOR.get(ev.severity.value, "white")
                        self.write(f"[{color}][{ev.type}][/] {ev.origin}: {json.dumps(ev.payload)[:100]}")
                self._last_count = count
        except Exception:
            pass


class AgentListView(ListView):
    """Agent list with status markers, task counts, role badges."""

    def on_mount(self):
        self.refresh_agents()
        self._handler = _subscribe_events(self, self.refresh_agents)
        self.set_interval(_DRIVEN_INTERVAL, self.refresh_agents)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def refresh_agents(self):
        try:
            kernel = FabricKernel.instance()
            if kernel.agent_runtime:
                agents = kernel.agent_runtime.list_agents()
                self.clear()
                for a in agents:
                    d = a.to_dict()
                    status_mark = AGENT_STATUS_MARK.get(d["status"], "?")
                    status_color = AGENT_STATUS_COLOR.get(d["status"], "white")
                    self.append(ListItem(Label(
                        f" [{status_color}]{status_mark}[/] [bold]{d['name']}[/]  "
                        f"[dim]{d['role']}[/]  "
                        f"tasks: {d['task_count']}/{d['completed_count']}/{d['failed_count']}"
                    )))
        except Exception:
            pass


class TaskSummary(Static):
    """Task graph summary — total nodes, status breakdown, critical path."""

    def on_mount(self):
        self._update_display()
        self._handler = _subscribe_events(self, self._update_display)
        self.set_interval(_DRIVEN_INTERVAL, self._update_display)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _update_display(self):
        try:
            kernel = FabricKernel.instance()
            if kernel.task_graph:
                s = kernel.task_graph.summary()
                text = f"Total: {s['total_nodes']}  |  "
                for status, count in s.get("by_status", {}).items():
                    text += f"{status}: {count}  |  "
                text += f"Critical path: {s['critical_path_length']} steps"
                self.update(f"[bold]Task Graph[/]  {text}")
            else:
                self.update("[dim]Task Graph: not initialized[/]")
        except Exception:
            self.update("[dim]Task Graph: not available[/]")


class ActivityBar(Widget):
    """Left sidebar with icon-based navigation."""

    ACTIONS = [
        ("home", "🏠", "Home"),
        ("inspector", "🔍", "Fabric Inspector"),
        ("agents", "🤖", "Agent Collaboration"),
        ("memory", "🧠", "Memory Explorer"),
        ("repository", "📁", "Repository"),
        ("timeline", "⏱", "Timeline"),
        ("graph", "🔬", "Knowledge Graph"),
        ("ai", "⚡", "AI Command Center"),
        ("ce", "🔄", "Continuous Engineering"),
        ("reports", "📊", "Reports"),
        ("settings", "⚙", "Settings"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="activity-bar"):
            for action_id, icon, label in self.ACTIONS:
                yield Button(icon, id=f"ab-{action_id}", tooltip=label, classes="activity-btn")

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id and btn_id.startswith("ab-"):
            action = btn_id[3:]
            app = self.app
            if hasattr(app, 'navigate_to'):
                app.navigate_to(action)


class ContextSidebar(Widget):
    """Right sidebar — context-sensitive info for the active screen."""

    def compose(self) -> ComposeResult:
        with Vertical(id="context-sidebar"):
            yield Static("[bold]Context[/]", id="sidebar-title", classes="sidebar-header")
            yield RichLog(id="sidebar-content", max_lines=50, highlight=True)

    def set_content(self, title: str, lines: list[str]):
        log = self.query_one("#sidebar-content", RichLog)
        log.clear()
        self.query_one("#sidebar-title", Static).update(f"[bold]{title}[/]")
        for line in lines:
            log.write(line)


class SectionTitle(Static):
    """Section title with consistent styling."""

    def __init__(self, text: str):
        super().__init__(f"[bold]{text}[/]", classes="section-title")


class DataPanel(Widget):
    """A reusable panel with title and RichLog content."""

    def __init__(self, title: str, max_lines: int = 20):
        super().__init__()
        self._panel_title = title
        self._max_lines = max_lines

    def compose(self) -> ComposeResult:
        with Vertical():
            yield SectionTitle(self._panel_title)
            yield RichLog(id=f"dp-{id(self)}", max_lines=self._max_lines, highlight=True)

    @property
    def log(self) -> RichLog:
        return self.query_one(f"#dp-{id(self)}", RichLog)

    def write(self, text: str):
        self.log.write(text)

    def clear(self):
        self.log.clear()


class AttentionWidget(Widget):
    """M78 — Shows items requiring immediate attention."""

    def compose(self) -> ComposeResult:
        yield SectionTitle("Requires Attention")
        yield RichLog(id="attention-log", max_lines=10, highlight=True)

    def on_mount(self):
        self._refresh_content()
        self._handler = _subscribe_events(self, self._refresh_content)
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_content)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_content(self):
        log = self.query_one("#attention-log", RichLog)
        log.clear()
        kernel = FabricKernel.instance()
        count = 0

        try:
            if kernel.agent_runtime:
                for a in kernel.agent_runtime.list_agents():
                    d = a.to_dict()
                    if d["status"] in ("error", "blocked"):
                        log.write(f"  [red]✗[/] Agent [bold]{d['name']}[/] is [red]{d['status']}[/]")
                        count += 1
                    elif d["failed_count"] > 0:
                        log.write(f"  [yellow]⚠[/] Agent [bold]{d['name']}[/] has {d['failed_count']} failures")
                        count += 1
        except Exception:
            pass

        try:
            if kernel.task_graph:
                s = kernel.task_graph.summary()
                for status in ("failed", "blocked"):
                    c = s.get("by_status", {}).get(status, 0)
                    if c > 0:
                        log.write(f"  [red]●[/] {c} task(s) {status}")
                        count += 1
                ready = s.get("ready_count", 0)
                if ready > 0:
                    log.write(f"  [yellow]◐[/] {ready} task(s) ready for execution")
                    count += 1
        except Exception:
            pass

        try:
            events = kernel.query_events(limit=10, event_type="error")
            for ev in events:
                age = time.time() - ev.timestamp
                if age < 60:
                    log.write(f"  [red]![/] {ev.type} — {ev.origin} ({age:.0f}s ago)")
                    count += 1
        except Exception:
            pass

        if count == 0:
            log.write("  [green]✓[/] All systems normal")


class LiveActivityFeed(RichLog):
    """M78 — Live event-driven activity feed for the Command Center."""

    def on_mount(self):
        self._last_count = 0
        self._handler = _subscribe_events(self, self.poll)
        self.set_interval(_DRIVEN_INTERVAL, self.poll)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def poll(self):
        try:
            kernel = FabricKernel.instance()
            count = kernel.event_store.count()
            if count > self._last_count:
                events = kernel.query_events(limit=5)
                for ev in events:
                    if ev.timestamp > time.time() - 30:
                        color = EVENT_SEVERITY_COLOR.get(ev.severity.value, "white")
                        self.write(f" [{color}]⊡[/] [{color}]{ev.type}[/] [dim]{ev.origin}[/]")
                self._last_count = count
        except Exception:
            pass


class FabricTrafficLight(Static):
    """M78 — Live fabric traffic indicator: shows event throughput as color bar."""

    def on_mount(self):
        self._samples: list[float] = []
        self._last_count = 0
        self._handler = _subscribe_events(self, self._tick)
        self.set_interval(1, self._tick)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _tick(self):
        try:
            kernel = FabricKernel.instance()
            count = kernel.event_store.count()
            delta = count - self._last_count
            self._samples.append(delta)
            if len(self._samples) > 10:
                self._samples.pop(0)
            self._last_count = count

            avg = sum(self._samples) / max(len(self._samples), 1)
            if avg > 5:
                color = "green"
            elif avg > 1:
                color = "yellow"
            else:
                color = "dim"
            self.update(f"[{color}]Event Traffic: {delta}/s (avg {avg:.1f}/s)[/]")
        except Exception:
            pass


class AgentCollaborationGraph(Widget):
    """M80 — Visual representation of agent collaboration and delegation."""

    def compose(self) -> ComposeResult:
        yield SectionTitle("Agent Collaboration")
        yield RichLog(id="collab-graph", max_lines=15, highlight=True)

    def on_mount(self):
        self.refresh()
        self._handler = _subscribe_events(self, self.refresh)
        self.set_interval(_DRIVEN_INTERVAL, self.refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def refresh(self, *, repaint=True, layout=False):
        log = self.query_one("#collab-graph", RichLog)
        log.clear()
        kernel = FabricKernel.instance()

        try:
            if not kernel.agent_runtime:
                log.write("  [dim]No agents registered[/]")
                return

            agents = kernel.agent_runtime.list_agents()
            if not agents:
                log.write("  [dim]No agents registered[/]")
                return

            log.write("[bold]Agent Hierarchy[/]")
            chiefs = [a for a in agents if getattr(a, '_spec', None) and hasattr(a._spec, 'role') and 'chief' in a._spec.role.lower()]
            others = [a for a in agents if a not in chiefs]

            for a in chiefs:
                d = a.to_dict()
                log.write(f"  [cyan]⊞[/] [bold]{d['name']}[/] ({d['role']})")
            for a in others[:5]:
                d = a.to_dict()
                log.write(f"  [dim]└──[/] [bold]{d['name']}[/] ({d['role']})")
            if len(others) > 5:
                log.write(f"  [dim]└── ... and {len(others)-5} more[/]")

            log.write("")
            log.write("[bold]Task Ownership[/]")
            for a in agents[:5]:
                d = a.to_dict()
                log.write(f"  {d['name']}: {d['task_count']} tasks ({d['completed_count']} done, {d['failed_count']} fail)")

            log.write("")
            log.write("[bold]Messaging Activity[/]")
            total_msgs = sum(len(getattr(a, '_outbox', [])) + len(getattr(a, '_inbox', [])) for a in agents)
            log.write(f"  {total_msgs} messages in flight")

        except Exception as e:
            log.write(f"  [dim]Error: {e}[/]")


class MetricsTimeline(Widget):
    """M84 — Key metrics over time, shown as a live timeline."""

    def compose(self) -> ComposeResult:
        yield SectionTitle("Metrics Timeline")
        yield RichLog(id="metrics-timeline", max_lines=8, highlight=True)

    def on_mount(self):
        self._samples: list[dict] = []
        self.refresh()
        self._handler = _subscribe_events(self, self.refresh)
        self.set_interval(_DRIVEN_INTERVAL, self.refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def refresh(self, *, repaint=True, layout=False):
        log = self.query_one("#metrics-timeline", RichLog)
        log.clear()
        kernel = FabricKernel.instance()

        try:
            s = kernel.stats()
            log.write(f"  Events/s: [bold]{s.events_delivered}[/]")
            log.write(f"  Uptime: [bold]{s.uptime_seconds:.0f}s[/]")
            log.write(f"  Services: [bold]{s.services}[/]")
            log.write(f"  Sessions: [bold]{s.active_sessions}[/]")
            if s.executor_running:
                log.write(f"  Executor runs: [bold]{s.executor_executions}[/] (failed: {s.executor_failed})")
            if kernel.storage and kernel.storage.connected:
                st = kernel.storage.stats()
                log.write(f"  DB writes: {st['write_count']}, reads: {st['read_count']}")
        except Exception:
            pass


class SessionTimeline(Widget):
    """M84 — Shows recent engineering sessions with their stage and status."""

    def compose(self) -> ComposeResult:
        yield SectionTitle("Recent Sessions")
        yield RichLog(id="session-timeline", max_lines=8, highlight=True)

    def on_mount(self):
        self._refresh_content()
        self._handler = _subscribe_events(self, self._refresh_content)
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_content)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_content(self):
        log = self.query_one("#session-timeline", RichLog)
        log.clear()
        kernel = FabricKernel.instance()

        try:
            ctx_count = len(kernel._contexts)
            if ctx_count > 0:
                for sid, ctx in list(kernel._contexts.items())[:5]:
                    st = ctx.get("session_type", "?")
                    age = time.time() - ctx.get("started_at", time.time())
                    log.write(f"  [dim]{sid[:12]}[/] {st} [dim]({age:.0f}s)[/]")
            else:
                log.write("  [dim]No active sessions[/]")
        except Exception:
            log.write("  [dim]Sessions not available[/]")


class CopilotSuggestions(Widget):
    """M124 — Copilot context-aware suggestions bar."""

    def compose(self) -> ComposeResult:
        yield SectionTitle("Copilot Suggestions")
        yield RichLog(id="copilot-suggestions", max_lines=5, highlight=True)

    def on_mount(self):
        self._refresh_content()
        self._handler = _subscribe_events(self, self._refresh_content)
        self.set_interval(_DRIVEN_INTERVAL, self._refresh_content)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh_content(self):
        log = self.query_one("#copilot-suggestions", RichLog)
        log.clear()
        kernel = FabricKernel.instance()
        try:
            copilot = kernel.copilot
            if hasattr(copilot, 'handle_intent'):
                findings = kernel.reasoning.analyze_all() if hasattr(kernel.reasoning, 'analyze_all') else {}
                risk_count = sum(1 for f in findings.values() if f.get("risk") and f["risk"] > 0.5) if findings else 0
                reg = kernel.engineering
                stats = reg.stats() if hasattr(reg, 'stats') else {}
                context = {
                    "screen": "home",
                    "engineering_objects": stats.get("total", "?"),
                    "high_risk_findings": risk_count,
                }
                resp = copilot.handle_intent("what_should_i_work_on", context)
                if isinstance(resp, dict) and resp.get("suggestion"):
                    log.write(f"  [bold cyan]▶[/] {resp['suggestion']}")
                elif isinstance(resp, str):
                    log.write(f"  [bold cyan]▶[/] {resp}")
                else:
                    log.write("  [dim]Copilot: all systems nominal[/]")
            else:
                log.write("  [dim]CopilotEngine loaded[/]")
        except Exception:
            log.write("  [dim]Copilot suggestions pending[/]")
