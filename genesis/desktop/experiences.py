from __future__ import annotations

import time
from typing import Any

try:
    from textual.app import ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical, ScrollableContainer
    from textual.screen import Screen
    from textual.widgets import (
        Button, Input, Label, ListItem, ListView,
        RichLog, Static, Tree,
    )
except ImportError:
    raise ImportError("Textual is required. Install with: pip install textual")

from genesis.fabric.kernel import FabricKernel
from genesis.fabric.events import EngineeringEvent
from genesis.desktop.widgets import (
    _DRIVEN_INTERVAL, _subscribe_events, _unsubscribe_events,
    CopilotSuggestions, DataPanel, SectionTitle,
    AGENT_STATUS_COLOR, AGENT_STATUS_MARK, EVENT_SEVERITY_COLOR,
    TASK_STATUS_COLOR,
)
from genesis.desktop.activity import ActivityCenter, NotificationSeverity


class ExperienceScreen(Screen):
    screen_id = "experience"

    def _kernel(self) -> FabricKernel:
        return FabricKernel.instance()

    def _color_for(self, val: float, high_is_bad: bool = True) -> str:
        if high_is_bad:
            return "red" if val > 0.7 else "yellow" if val > 0.3 else "green"
        return "green" if val > 0.7 else "yellow" if val > 0.3 else "red"


class UnderstandProject(ExperienceScreen):
    screen_id = "understand"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("1", "switch_understand", "Overview"),
        Binding("2", "switch_knowledge", "Knowledge"),
        Binding("3", "switch_decisions", "Decisions"),
    ]

    VIEWS = ["overview", "knowledge", "decisions"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Understand Project[/]", id="exp-title")
            yield Static("[dim]Project overview | Knowledge base | Decisions | [1]Overview [2]Knowledge [3]Decisions",
                         id="exp-subtitle")
            with Horizontal():
                with Vertical(id="exp-left", classes="exp-panel"):
                    yield SectionTitle("Project Health")
                    yield RichLog(id="exp-health", max_lines=8, highlight=True)
                    yield SectionTitle("Recent Activity")
                    yield RichLog(id="exp-activity", max_lines=12, highlight=True)
                with Vertical(id="exp-center", classes="exp-panel"):
                    yield SectionTitle("Knowledge Overview")
                    yield RichLog(id="exp-knowledge", max_lines=10, highlight=True)
                    yield SectionTitle("Active Decisions")
                    yield RichLog(id="exp-decisions", max_lines=10, highlight=True)
                with Vertical(id="exp-right", classes="exp-panel"):
                    yield SectionTitle("Key Metrics")
                    yield RichLog(id="exp-metrics", max_lines=8, highlight=True)
                    yield CopilotSuggestions(id="exp-copilot")
            yield Static(id="exp-status")

    def on_mount(self):
        self._view = "overview"
        self._handler = _subscribe_events(self, self._refresh)
        self._refresh()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh(self):
        kernel = self._kernel()
        if self._view == "overview":
            self._show_overview(kernel)
        elif self._view == "knowledge":
            self._show_knowledge(kernel)
        elif self._view == "decisions":
            self._show_decisions(kernel)

    def _show_overview(self, kernel):
        try:
            health = self.query_one("#exp-health", RichLog)
            health.clear()
            s = kernel.stats()
            health.write(f"[bold]System[/]")
            health.write(f"  State: [{'green' if s.state == 'running' else 'yellow'}]{s.state}[/]")
            health.write(f"  Uptime: {s.uptime_seconds:.0f}s")
            health.write(f"  Events: {s.events_delivered} delivered")
            health.write(f"  Services: {s.services}")

            t = kernel.twin.summary() if hasattr(kernel.twin, 'summary') else {}
            if t:
                health.write(f"[bold]Repository[/]")
                health.write(f"  Modules: {t.get('total_modules', '?')}")
                health.write(f"  Classes: {t.get('total_classes', '?')}")
                health.write(f"  Functions: {t.get('total_functions', '?')}")

            activity = self.query_one("#exp-activity", RichLog)
            activity.clear()
            events = kernel.query_events(limit=8)
            if events:
                activity.write("[bold]Recent Events[/]")
                for ev in reversed(events[-5:]):
                    c = EVENT_SEVERITY_COLOR.get(ev.severity.value, "white")
                    activity.write(f"  [{c}]⊡[/] {ev.type} [dim]{ev.origin}[/]")
            else:
                activity.write("  [dim]No recent events[/]")
        except Exception:
            pass

    def _show_knowledge(self, kernel):
        klog = self.query_one("#exp-knowledge", RichLog)
        klog.clear()
        klog.write("[bold]Knowledge Base[/]")
        try:
            if hasattr(kernel, 'knowledge_organizer'):
                stats = kernel.knowledge_organizer.stats() if hasattr(kernel.knowledge_organizer, 'stats') else {}
                klog.write(f"  Clusters: {stats.get('clusters', 0)}")
                klog.write(f"  Concepts: {stats.get('concepts', 0)}")
                klog.write(f"  Items: {stats.get('total_items', 0)}")
                klog.write(f"  Top cluster: [bold]{stats.get('strongest_cluster', 'N/A')}[/]")
        except Exception:
            klog.write("  [dim]Knowledge organizer not available[/]")

        dlog = self.query_one("#exp-decisions", RichLog)
        dlog.clear()
        dlog.write("[bold]Decisions[/]")
        try:
            if hasattr(kernel, 'decision_intelligence'):
                stats = kernel.decision_intelligence.stats() if hasattr(kernel.decision_intelligence, 'stats') else {}
                dlog.write(f"  Total: {stats.get('total', 0)}")
                dlog.write(f"  Proposed: {stats.get('proposed', 0)}")
                dlog.write(f"  Decided: {stats.get('decided', 0)}")
        except Exception:
            dlog.write("  [dim]Decision intelligence not available[/]")

    def _show_decisions(self, kernel):
        dlog = self.query_one("#exp-decisions", RichLog)
        dlog.clear()
        dlog.write("[bold]All Decisions[/]")
        try:
            if hasattr(kernel, 'decision_intelligence'):
                di = kernel.decision_intelligence
                results = di.search("", "all") if hasattr(di, 'search') else []
                if results:
                    for r in results[:10]:
                        title = r.get('title', '?') if isinstance(r, dict) else getattr(r, 'title', '?')
                        status = r.get('status', '?') if isinstance(r, dict) else getattr(r, 'status', '?')
                        c = "green" if status == "decided" else "yellow"
                        dlog.write(f"  [{c}]●[/] {title} [dim]({status})[/]")
                else:
                    dlog.write("  [dim]No decisions recorded[/]")
        except Exception:
            dlog.write("  [dim]Decision engine not available[/]")

    def _show_metrics(self, kernel):
        mlog = self.query_one("#exp-metrics", RichLog)
        mlog.clear()
        mlog.write("[bold]Engineering Metrics[/]")
        try:
            reg = kernel.engineering
            stats = reg.stats() if hasattr(reg, 'stats') else {}
            mlog.write(f"  Registry objects: {stats.get('total', 0)}")
            mlog.write(f"  Types: {len(stats.get('by_type', {}))}")
        except Exception:
            mlog.write("  [dim]Registry not available[/]")

    def action_switch_understand(self):
        self._view = "overview"
        self._refresh()

    def action_switch_knowledge(self):
        self._view = "knowledge"
        self._refresh()

    def action_switch_decisions(self):
        self._view = "decisions"
        self._refresh()

    def action_refresh(self):
        self._refresh()


class ReviewArchitecture(ExperienceScreen):
    screen_id = "architecture"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "show_dependencies", "Dependencies"),
        Binding("q", "show_quality", "Quality"),
        Binding("c", "show_coupling", "Coupling"),
    ]

    VIEWS = ["dependencies", "quality", "coupling"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Review Architecture[/]", id="arch-title")
            yield Static("[dim]Dependencies | Quality | Coupling | [D]eps [Q]uality [C]oupling",
                         id="arch-subtitle")
            with Horizontal():
                with Vertical(id="arch-left", classes="exp-panel"):
                    yield SectionTitle("Architecture Summary")
                    yield RichLog(id="arch-summary", max_lines=15, highlight=True)
                with Vertical(id="arch-right", classes="exp-panel"):
                    yield SectionTitle("Analysis")
                    yield RichLog(id="arch-analysis", max_lines=25, highlight=True)
            yield Static(id="arch-status")

    def on_mount(self):
        self._view = "dependencies"
        self._handler = _subscribe_events(self, self._refresh)
        self._refresh()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh(self):
        kernel = self._kernel()
        summary = self.query_one("#arch-summary", RichLog)
        summary.clear()
        analysis = self.query_one("#arch-analysis", RichLog)
        analysis.clear()

        try:
            if hasattr(kernel, 'live_architecture'):
                arch = kernel.live_architecture
                s = arch.summary() if hasattr(arch, 'summary') else {}
                summary.write(f"[bold]Modules:[/] {s.get('total_modules', 'N/A')}")
                summary.write(f"[bold]Dependencies:[/] {s.get('total_dependencies', 'N/A')}")
                summary.write(f"[bold]Architecture Score:[/] {s.get('architecture_score', 'N/A')}")

            if hasattr(kernel, 'reasoning'):
                reasoning = kernel.reasoning
                if hasattr(reasoning, 'analyze_coupling'):
                    coup = reasoning.analyze_coupling()
                    if isinstance(coup, dict):
                        analysis.write("[bold]Coupling Analysis[/]")
                        for mod, score in list(coup.items())[:10]:
                            c = self._color_for(score)
                            analysis.write(f"  [{c}]●[/] {mod}: {score:.2f}")
        except Exception:
            analysis.write("  [dim]Architecture analysis pending[/]")

    def action_show_dependencies(self):
        self._view = "dependencies"
        self._refresh()

    def action_show_quality(self):
        self._view = "quality"
        self._refresh()

    def action_show_coupling(self):
        self._view = "coupling"
        self._refresh()

    def action_refresh(self):
        self._refresh()


class ContinueWork(ExperienceScreen):
    screen_id = "continue"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("w", "show_workflows", "Workflows"),
        Binding("p", "show_playbooks", "Playbooks"),
    ]

    VIEWS = ["workflows", "playbooks"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Continue Previous Work[/]", id="cw-title")
            yield Static("[dim]Active workflows | Pending playbooks | Recent sessions | [W]orkflows [P]laybooks",
                         id="cw-subtitle")
            with Horizontal():
                with Vertical(id="cw-left", classes="exp-panel"):
                    yield SectionTitle("Active Workflows")
                    yield RichLog(id="cw-workflows", max_lines=15, highlight=True)
                    yield SectionTitle("Recent Sessions")
                    yield RichLog(id="cw-sessions", max_lines=8, highlight=True)
                with Vertical(id="cw-right", classes="exp-panel"):
                    yield SectionTitle("Copilot Suggestions")
                    yield CopilotSuggestions(id="cw-copilot")
                    yield SectionTitle("Pending Decisions")
                    yield RichLog(id="cw-decisions", max_lines=8, highlight=True)
            yield Static(id="cw-status")

    def on_mount(self):
        self._view = "workflows"
        self._handler = _subscribe_events(self, self._refresh)
        self._refresh()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh(self):
        kernel = self._kernel()
        wf = self.query_one("#cw-workflows", RichLog)
        wf.clear()
        try:
            if hasattr(kernel, 'workflow_engine'):
                we = kernel.workflow_engine
                defs = we.list_defs() if hasattr(we, 'list_defs') else []
                execs = we.list_executions() if hasattr(we, 'list_executions') else []
                wf.write(f"[bold]Workflow Definitions:[/] {len(defs)}")
                wf.write(f"[bold]Active Executions:[/] {len(execs)}")
                for e in execs[:5]:
                    name = getattr(e, 'workflow_name', str(e)) if not isinstance(e, dict) else e.get('workflow_name', '?')
                    status = getattr(e, 'status', '?') if not isinstance(e, dict) else e.get('status', '?')
                    c = "green" if status == "completed" else "cyan" if status == "running" else "yellow"
                    wf.write(f"  [{c}]●[/] {name} [dim]({status})[/]")
        except Exception:
            wf.write("  [dim]Workflow engine not available[/]")

        sess = self.query_one("#cw-sessions", RichLog)
        sess.clear()
        try:
            ctx_count = len(kernel._contexts)
            sess.write(f"[bold]Active Sessions:[/] {ctx_count}")
            for sid, ctx in list(kernel._contexts.items())[:5]:
                st = ctx.get("session_type", "?")
                age = time.time() - ctx.get("started_at", time.time())
                sess.write(f"  {sid[:12]} [dim]{st} ({age:.0f}s ago)[/]")
        except Exception:
            sess.write("  [dim]No sessions[/]")

        dec = self.query_one("#cw-decisions", RichLog)
        dec.clear()
        try:
            if hasattr(kernel, 'decision_intelligence'):
                di = kernel.decision_intelligence
                stats = di.stats() if hasattr(di, 'stats') else {}
                dec.write(f"[bold]Open Decisions:[/] {stats.get('proposed', 0)}")
        except Exception:
            dec.write("  [dim]No pending decisions[/]")

    def action_show_workflows(self):
        self._view = "workflows"
        self._refresh()

    def action_show_playbooks(self):
        self._view = "playbooks"
        self._refresh()

    def action_refresh(self):
        self._refresh()


class InvestigateProblem(ExperienceScreen):
    screen_id = "investigate"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("e", "show_errors", "Errors"),
        Binding("i", "show_insights", "Insights"),
        Binding("w", "show_warnings", "Warnings"),
    ]

    VIEWS = ["errors", "warnings", "insights"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Investigate Problem[/]", id="inv-title")
            yield Static("[dim]Errors | Warnings | Insights | Root cause | [E]rrors [W]arnings [I]nsights",
                         id="inv-subtitle")
            with Horizontal():
                with Vertical(id="inv-left", classes="exp-panel"):
                    yield SectionTitle("Issues")
                    yield RichLog(id="inv-issues", max_lines=20, highlight=True)
                with Vertical(id="inv-right", classes="exp-panel"):
                    yield SectionTitle("Details")
                    yield RichLog(id="inv-details", max_lines=20, highlight=True)
            yield Static(id="inv-status")

    def on_mount(self):
        self._view = "errors"
        self._handler = _subscribe_events(self, self._refresh)
        self._refresh()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh(self):
        kernel = self._kernel()
        issues = self.query_one("#inv-issues", RichLog)
        issues.clear()
        details = self.query_one("#inv-details", RichLog)
        details.clear()

        if self._view == "errors":
            issues.write("[bold]Error Events[/]")
            err_events = kernel.query_events(limit=15)
            errors = [e for e in err_events if e.severity.value in ("error", "critical")]
            if errors:
                for ev in errors[:10]:
                    age = time.time() - ev.timestamp
                    issues.write(f"  [red]![/] {ev.type} [dim]({age:.0f}s ago)[/]")
                    details.write(f"[red]{ev.type}[/] from {ev.origin}")
                    details.write(f"  {str(ev.payload)[:200]}")
            else:
                issues.write("  [green]No recent errors[/]")
                details.write("  [green]All systems healthy[/]")

        elif self._view == "warnings":
            issues.write("[bold]Warnings[/]")
            w_events = kernel.query_events(limit=15)
            warnings = [e for e in w_events if e.severity.value == "warning"]
            if warnings:
                for ev in warnings[:10]:
                    issues.write(f"  [yellow]⚠[/] {ev.type}")
            else:
                issues.write("  [green]No warnings[/]")

        elif self._view == "insights":
            issues.write("[bold]Insights[/]")
            try:
                if hasattr(kernel, 'insight_engine'):
                    ie = kernel.insight_engine
                    insights = ie.list() if hasattr(ie, 'list') else []
                    if insights:
                        for ins in insights[:10]:
                            title = ins.get('title', '?') if isinstance(ins, dict) else getattr(ins, 'title', '?')
                            sev = ins.get('severity', '?') if isinstance(ins, dict) else getattr(ins, 'severity', '?')
                            c = "red" if sev == "high" else "yellow"
                            issues.write(f"  [{c}]●[/] {title} [dim]({sev})[/]")
                    else:
                        issues.write("  [dim]No insights recorded[/]")
            except Exception:
                issues.write("  [dim]Insight engine not available[/]")

    def action_show_errors(self):
        self._view = "errors"
        self._refresh()

    def action_show_warnings(self):
        self._view = "warnings"
        self._refresh()

    def action_show_insights(self):
        self._view = "insights"
        self._refresh()

    def action_refresh(self):
        self._refresh()


class ImproveRepository(ExperienceScreen):
    screen_id = "improve"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "show_debt", "Debt"),
        Binding("p", "show_playbooks", "Playbooks"),
        Binding("s", "show_suggestions", "Suggestions"),
    ]

    VIEWS = ["debt", "playbooks", "suggestions"]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Improve Repository[/]", id="imp-title")
            yield Static("[dim]Technical debt | Playbooks | Suggestions | [D]ebt [P]laybooks [S]uggestions",
                         id="imp-subtitle")
            with Horizontal():
                with Vertical(id="imp-left", classes="exp-panel"):
                    yield SectionTitle("Improvement Opportunities")
                    yield RichLog(id="imp-opportunities", max_lines=20, highlight=True)
                with Vertical(id="imp-right", classes="exp-panel"):
                    yield SectionTitle("Details")
                    yield RichLog(id="imp-details", max_lines=20, highlight=True)
            yield Static(id="imp-status")

    def on_mount(self):
        self._view = "debt"
        self._handler = _subscribe_events(self, self._refresh)
        self._refresh()
        self.set_interval(_DRIVEN_INTERVAL, self._refresh)

    def on_unmount(self):
        _unsubscribe_events(self._handler)

    def _refresh(self):
        kernel = self._kernel()
        opp = self.query_one("#imp-opportunities", RichLog)
        opp.clear()
        det = self.query_one("#imp-details", RichLog)
        det.clear()

        if self._view == "debt":
            opp.write("[bold]Technical Debt[/]")
            try:
                if hasattr(kernel, 'reasoning'):
                    r = kernel.reasoning
                    if hasattr(r, 'analyze_debt'):
                        debt = r.analyze_debt()
                        if isinstance(debt, dict):
                            for mod, score in list(debt.items())[:15]:
                                c = self._color_for(score)
                                opp.write(f"  [{c}]●[/] {mod}: {score:.2f}")
                    if hasattr(r, 'analyze_fragility'):
                        frag = r.analyze_fragility()
                        if isinstance(frag, dict):
                            det.write("[bold]Fragility[/]")
                            for mod, score in list(frag.items())[:10]:
                                c = self._color_for(score)
                                det.write(f"  [{c}]●[/] {mod}: {score:.2f}")
                else:
                    opp.write("  [dim]Reasoning engine not available[/]")
            except Exception:
                opp.write("  [dim]Debt analysis pending[/]")

        elif self._view == "playbooks":
            opp.write("[bold]Available Playbooks[/]")
            try:
                if hasattr(kernel, 'playbooks'):
                    pb = kernel.playbooks
                    playbooks = pb.list() if hasattr(pb, 'list') else []
                    if playbooks:
                        for p in playbooks:
                            name = p.get('name', str(p)) if isinstance(p, dict) else getattr(p, 'name', str(p))
                            desc = p.get('description', '') if isinstance(p, dict) else getattr(p, 'description', '')
                            opp.write(f"  [cyan]⊞[/] [bold]{name}[/]")
                            det.write(f"  {desc}")
                    else:
                        opp.write("  [dim]No playbooks registered[/]")
            except Exception:
                opp.write("  [dim]Playbooks not available[/]")

        elif self._view == "suggestions":
            opp.write("[bold]Proactive Suggestions[/]")
            try:
                if hasattr(kernel, 'proactive_copilot'):
                    pc = kernel.proactive_copilot
                    suggestions = pc.suggestions() if hasattr(pc, 'suggestions') else []
                    if suggestions:
                        for s in suggestions[:10]:
                            title = s.get('title', '?') if isinstance(s, dict) else getattr(s, 'title', '?')
                            urg = s.get('urgency', 'low') if isinstance(s, dict) else getattr(s, 'urgency', 'low')
                            c = "red" if urg == "high" else "yellow" if urg == "medium" else "green"
                            opp.write(f"  [{c}]●[/] {title} [dim]({urg})[/]")
                    else:
                        opp.write("  [dim]No suggestions yet[/]")
            except Exception:
                opp.write("  [dim]Proactive copilot not available[/]")

    def action_show_debt(self):
        self._view = "debt"
        self._refresh()

    def action_show_playbooks(self):
        self._view = "playbooks"
        self._refresh()

    def action_show_suggestions(self):
        self._view = "suggestions"
        self._refresh()

    def action_refresh(self):
        self._refresh()
