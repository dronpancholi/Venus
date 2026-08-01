from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry
from genesis.state import get_state


class PanelCapability(Enum):
    OBSERVE = "observe"
    REASON = "reason"
    RECOMMEND = "recommend"
    EXECUTE = "execute"
    MONITOR = "monitor"


@dataclass
class PanelAction:
    label: str
    handler: str
    params: dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = True


@dataclass
class DashboardPanel:
    title: str
    data_source: str = ""
    refresh_interval: float = 10.0
    last_data: dict[str, Any] = field(default_factory=dict)
    last_refresh: float = 0.0
    capabilities: list[PanelCapability] = field(default_factory=lambda: [PanelCapability.OBSERVE])
    actions: list[PanelAction] = field(default_factory=list)
    status: str = "idle"
    error: str | None = None
    recommendation: str = ""


@dataclass
class ProjectDashboard:
    project_name: str
    panels: dict[str, DashboardPanel] = field(default_factory=dict)
    layout: list[str] = field(default_factory=list)


class LiveCommandCenter:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._state = get_state()
        self._dashboards: dict[str, ProjectDashboard] = {}
        self._action_handlers: dict[str, Callable] = {}
        self._cc_obj: EngineeringObject | None = None

    def boot(self):
        self._cc_obj = EngineeringObject(
            object_type=EngineeringObjectType.WORKSPACE,
            name="LiveCommandCenter",
            description="Live project command center with real-time dashboards",
            tags=["command_center", "dashboard"],
        )
        self._registry.register(self._cc_obj)
        self._state.set("command_center", "dashboards", 0)
        self._register_default_handlers()
        self._build_default()

    def _register_default_handlers(self):
        self._action_handlers["refresh_architecture"] = lambda: self._fetch_data("architecture")
        self._action_handlers["refresh_health"] = lambda: self._fetch_data("health")
        self._action_handlers["run_health_check"] = lambda: (
            self._kernel.health_engine.snapshot().to_dict()
        )
        self._action_handlers["observe_boot"] = lambda: (
            self._kernel.boot_report.to_dict() if self._kernel.boot_report else {}
        )
        self._action_handlers["export_observability"] = lambda: (
            {"exported": self._kernel.observability.export_to_file("observability_export.json")}
            if hasattr(self._kernel.observability, 'export_to_file') else {}
        )

    def register_action_handler(self, name: str, handler: Callable) -> None:
        self._action_handlers[name] = handler

    def _build_default(self):
        dashboard = ProjectDashboard(project_name="default")

        dashboard.panels["health"] = DashboardPanel(
            title="System Health",
            data_source="health",
            capabilities=[PanelCapability.OBSERVE, PanelCapability.MONITOR],
            actions=[PanelAction("Run Check", "refresh_health", requires_approval=False)],
        )
        dashboard.panels["boot"] = DashboardPanel(
            title="Boot Sequence",
            data_source="boot",
            capabilities=[PanelCapability.OBSERVE, PanelCapability.REASON],
            actions=[PanelAction("View Boot Report", "observe_boot", requires_approval=False)],
        )
        dashboard.panels["observability"] = DashboardPanel(
            title="Observability",
            data_source="observability",
            capabilities=[PanelCapability.OBSERVE, PanelCapability.EXECUTE],
            actions=[PanelAction("Export Actions", "export_observability", requires_approval=True)],
        )
        dashboard.panels["architecture"] = DashboardPanel(
            title="Architecture",
            data_source="architecture",
            actions=[PanelAction("Scan", "refresh_architecture", requires_approval=True)],
        )
        dashboard.panels["knowledge"] = DashboardPanel(title="Knowledge", data_source="knowledge")
        dashboard.panels["timeline"] = DashboardPanel(title="Timeline", data_source="timeline")
        dashboard.panels["memory"] = DashboardPanel(title="Memory", data_source="memory_v2")
        dashboard.panels["risk"] = DashboardPanel(title="Risk", data_source="reasoning")
        dashboard.panels["velocity"] = DashboardPanel(title="Velocity", data_source="observatory")
        dashboard.panels["decisions"] = DashboardPanel(title="Decisions", data_source="decisions")
        dashboard.panels["insights"] = DashboardPanel(title="Insights", data_source="insight")
        dashboard.panels["plans"] = DashboardPanel(title="Plans", data_source="planner")
        dashboard.panels["workflows"] = DashboardPanel(title="Workflows", data_source="workflows")
        dashboard.panels["ai"] = DashboardPanel(title="AI Activity", data_source="ai")
        dashboard.panels["agents"] = DashboardPanel(title="Agents", data_source="agents")
        dashboard.panels["graph"] = DashboardPanel(
            title="Graph", data_source="graph",
            capabilities=[PanelCapability.OBSERVE],
        )
        dashboard.panels["reports"] = DashboardPanel(title="Reports", data_source="reports")
        dashboard.layout = [
            "health", "boot", "observability",
            "architecture", "knowledge", "timeline", "memory",
            "risk", "velocity", "decisions", "insights",
            "plans", "workflows", "ai", "agents", "graph", "reports",
        ]
        self._dashboards["default"] = dashboard
        self._state.set("command_center", "dashboards", len(self._dashboards))

    def get_dashboard(self, name: str = "default") -> ProjectDashboard | None:
        return self._dashboards.get(name)

    def refresh_panel(self, dashboard_name: str, panel_name: str,
                      record_observability: bool = True) -> dict[str, Any] | None:
        dashboard = self._dashboards.get(dashboard_name)
        if not dashboard:
            return None
        panel = dashboard.panels.get(panel_name)
        if not panel:
            return None
        try:
            data = self._fetch_data(panel.data_source)
            panel.last_data = data
            panel.last_refresh = time.time()
            panel.status = "ok"
            panel.error = None
            if record_observability and self._kernel.observability:
                self._kernel.observability.record(
                    type_=__import__('genesis.observability.engine', fromlist=['ActionType']).ActionType.DESKTOP_INTERACTION,
                    subsystem="command_center",
                    action=f"refresh_panel.{panel_name}",
                    detail=f"Refreshed {panel.title}",
                )
        except Exception as e:
            panel.status = "error"
            panel.error = str(e)
            data = {"error": str(e)}
        return data

    def refresh_all(self, dashboard_name: str = "default") -> dict[str, Any]:
        dashboard = self._dashboards.get(dashboard_name)
        if not dashboard:
            return {}
        results = {}
        for pname in dashboard.layout:
            results[pname] = self.refresh_panel(dashboard_name, pname, record_observability=False)
        return results

    def execute_action(self, dashboard_name: str, panel_name: str,
                       action_label: str) -> dict[str, Any]:
        dashboard = self._dashboards.get(dashboard_name)
        if not dashboard:
            return {"error": f"No dashboard '{dashboard_name}'"}
        panel = dashboard.panels.get(panel_name)
        if not panel:
            return {"error": f"No panel '{panel_name}'"}
        action = next((a for a in panel.actions if a.label == action_label), None)
        if not action:
            return {"error": f"No action '{action_label}' on panel '{panel_name}'"}
        handler = self._action_handlers.get(action.handler)
        if not handler:
            return {"error": f"No handler for '{action.handler}'"}
        try:
            result = handler()
            if self._kernel.observability:
                self._kernel.observability.record(
                    type_=__import__('genesis.observability.engine', fromlist=['ActionType']).ActionType.COMMAND,
                    subsystem="command_center",
                    action=f"execute.{action.handler}",
                    detail=f"Executed {action_label} on {panel.title}",
                    success=True,
                )
            return {"success": True, "data": result}
        except Exception as e:
            if self._kernel.observability:
                self._kernel.observability.record(
                    type_=__import__('genesis.observability.engine', fromlist=['ActionType']).ActionType.COMMAND,
                    subsystem="command_center",
                    action=f"execute.{action.handler}",
                    detail=f"Failed {action_label} on {panel.title}",
                    success=False, error=str(e),
                )
            return {"error": str(e)}

    def _fetch_data(self, source: str) -> dict[str, Any]:
        k = self._kernel
        if not k:
            return {"error": "no kernel"}
        try:
            if source == "architecture":
                la = k.live_architecture
                return la.summary() if hasattr(la, 'summary') else {}
            if source == "knowledge":
                ke = k.knowledge
                return ke.summary() if hasattr(ke, 'summary') else {}
            if source == "timeline":
                tl = k.timeline
                return {"entries": len(tl.query(limit=100))} if hasattr(tl, 'query') else {}
            if source == "memory_v2":
                mv = k.memory_v2
                return mv.stats() if hasattr(mv, 'stats') else {}
            if source == "reasoning":
                r = k.reasoning
                return r.summary() if hasattr(r, 'summary') else {}
            if source == "observatory":
                ob = k.observatory
                return ob.snapshot() if hasattr(ob, 'snapshot') else {}
            if source == "decisions":
                di = k.decision_intelligence
                return di.stats() if hasattr(di, 'stats') else {}
            if source == "insight":
                ie = k.insight_engine
                return ie.stats() if hasattr(ie, 'stats') else {}
            if source == "planner":
                pl = k.planner
                return {"plans": len(pl.list_plans())} if hasattr(pl, 'list_plans') else {}
            if source == "workflows":
                we = k.workflow_engine
                return we.stats() if hasattr(we, 'stats') else {}
            if source == "ai":
                ai = k.ai
                return ai.summarize() if hasattr(ai, 'summarize') else {}
            if source == "agents":
                ar = k.agent_runtime
                if ar and hasattr(ar, 'summary'):
                    return ar.summary()
                return {"agents": len(ar.list_agents())} if ar else {}
            if source == "health":
                he = k.health_engine
                score = he.score()
                return score.to_dict() if hasattr(score, 'to_dict') else {"score": 0}
            if source == "boot":
                be = k.boot_engine
                report = be.report() if be else None
                return report.to_dict() if report else {"booted": False}
            if source == "observability":
                obs = k.observability
                return obs.stats() if hasattr(obs, 'stats') else {}
            if source == "graph":
                gr = k.graph
                return gr.summary()
            if source == "reports":
                import pathlib
                reports_dir = pathlib.Path(k._started_at if hasattr(k, '_started_at') else ".").parent / "Reports"
                md_files = list(reports_dir.rglob("*.md")) if reports_dir.exists() else []
                return {"reports": len(md_files)}
        except Exception as e:
            return {"error": str(e)}
        return {}

    def snapshot(self) -> dict[str, Any]:
        panels_total = sum(len(d.panels) for d in self._dashboards.values())
        panels_ok = sum(
            1 for d in self._dashboards.values()
            for p in d.panels.values() if p.status == "ok"
        )
        return {
            "dashboards": len(self._dashboards),
            "panels": panels_total,
            "panels_ok": panels_ok,
            "handlers": len(self._action_handlers),
        }
