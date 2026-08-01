"""
Engineering Terminal (Mission 182) — Genesis-aware command shell.

Commands operate on Genesis concepts: projects, objects, knowledge,
timeline, reports, apps, AI, providers, workflows.

Not a generic shell — understands Genesis natively.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TerminalCommand:
    name: str
    description: str = ""
    usage: str = ""
    handler: str = ""
    args: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TerminalResult:
    text: str = ""
    data: Any = None
    error: str = ""
    format: str = "text"  # text | table | json | tree


BUILTIN_COMMANDS: list[TerminalCommand] = [
    TerminalCommand("help", "Show available commands", "help [command]"),
    TerminalCommand("status", "Show platform status", "status [--json]"),
    TerminalCommand("events", "Query events", "events [--type TYPE] [--limit N]"),
    TerminalCommand("agents", "List agents", "agents [--status STATUS]"),
    TerminalCommand("apps", "List applications", "apps [--running]"),
    TerminalCommand("providers", "List AI providers", "providers [--healthy]"),
    TerminalCommand("knowledge", "Search knowledge", "knowledge <query>"),
    TerminalCommand("search", "Search everything", "search <query> [--source SRC]"),
    TerminalCommand("memory", "Query memory", "memory <type> [--limit N]"),
    TerminalCommand("timeline", "View timeline", "timeline [--days N]"),
    TerminalCommand("services", "List services", "services"),
    TerminalCommand("health", "System health check", "health [--detail]"),
    TerminalCommand("resources", "Resource usage", "resources"),
    TerminalCommand("lifecycle", "Platform lifecycle", "lifecycle [pause|resume|status]"),
    TerminalCommand("karpathy", "Run Karpathy goal-driven execution", "karpathy <goal> [verify_cmd]"),
    TerminalCommand("apply-rules", "Inject Karpathy guidelines", "apply-rules [path]"),
]


class EngineeringTerminal:
    """REPL for Genesis-aware commands."""

    def __init__(self, kernel: Any = None, lifecycle: Any = None,
                 query_engine: Any = None, resource_monitor: Any = None,
                 app_runtime: Any = None):
        self._kernel = kernel
        self._lifecycle = lifecycle
        self._query_engine = query_engine
        self._resource_monitor = resource_monitor
        self._app_runtime = app_runtime
        self._commands: dict[str, TerminalCommand] = {
            c.name: c for c in BUILTIN_COMMANDS
        }

    def register(self, cmd: TerminalCommand):
        self._commands[cmd.name] = cmd

    @property
    def commands(self) -> dict[str, TerminalCommand]:
        return dict(self._commands)

    def execute(self, line: str) -> TerminalResult:
        try:
            parts = shlex.split(line)
        except ValueError as e:
            return TerminalResult(error=f"Parse error: {e}")
        if not parts:
            return TerminalResult(error="Empty command")

        cmd_name = parts[0].lower()
        args = parts[1:]

        handler_name = f"_cmd_{cmd_name}"
        handler = getattr(self, handler_name, None)
        if not handler:
            return TerminalResult(error=f"Unknown command: {cmd_name}. Type 'help'.")

        try:
            return handler(args)
        except Exception as e:
            return TerminalResult(error=f"Error: {e}")

    def _cmd_help(self, args: list[str]) -> TerminalResult:
        if args:
            cmd = self._commands.get(args[0])
            if cmd:
                return TerminalResult(
                    text=f"{cmd.name}: {cmd.description}\nUsage: {cmd.usage}",
                )
            return TerminalResult(error=f"Unknown command: {args[0]}")
        lines = ["Available commands:"]
        for name, cmd in sorted(self._commands.items()):
            lines.append(f"  {name:20s} {cmd.description}")
        return TerminalResult(text="\n".join(lines))

    def _cmd_status(self, args: list[str]) -> TerminalResult:
        info: dict[str, Any] = {"platform": "Genesis"}
        if self._kernel:
            try:
                h = self._kernel.health()
                info["state"] = h.status
                info["uptime"] = f"{h.uptime_seconds:.0f}s"
                info["services"] = h.services_count
                info["sessions"] = h.active_sessions
                info["threads"] = h.threads
            except Exception:
                pass
        if self._lifecycle:
            info["lifecycle"] = self._lifecycle._state.value
        if "--json" in args:
            return TerminalResult(data=info, format="json")
        lines = [f"{k}: {v}" for k, v in info.items()]
        return TerminalResult(text="\n".join(lines))

    def _cmd_events(self, args: list[str]) -> TerminalResult:
        if not self._kernel:
            return TerminalResult(error="No kernel connected")
        limit = 20
        event_type = None
        for i, a in enumerate(args):
            if a == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])
            elif a == "--type" and i + 1 < len(args):
                event_type = args[i + 1]
        try:
            events = self._kernel.query_events(limit=limit)
            if event_type:
                events = [e for e in events if e.type == event_type]
            lines = [f"{e.timestamp:.2f} [{e.severity.value:8s}] {e.type:30s} {e.origin}" for e in events]
            return TerminalResult(text="\n".join(lines) if lines else "No events found")
        except Exception as e:
            return TerminalResult(error=str(e))

    def _cmd_agents(self, args: list[str]) -> TerminalResult:
        if not self._kernel or not self._kernel.agent_runtime:
            return TerminalResult(error="No agent runtime")
        try:
            agents = self._kernel.agent_runtime.list_agents()
            status_filter = None
            for i, a in enumerate(args):
                if a == "--status" and i + 1 < len(args):
                    status_filter = args[i + 1]
            if status_filter:
                agents = [a for a in agents if a.get("status") == status_filter]
            lines = [f"{a.get('name', '?'):20s} {a.get('role', '?'):20s} {a.get('status', '?')}" for a in agents]
            return TerminalResult(text="\n".join(lines) if lines else "No agents")
        except Exception as e:
            return TerminalResult(error=str(e))

    def _cmd_apps(self, args: list[str]) -> TerminalResult:
        if not self._app_runtime:
            return TerminalResult(error="No app runtime")
        apps = self._app_runtime.list()
        if "--running" in args:
            apps = [a for a in apps if a["status"] == "running"]
        lines = [f"{a['name']:20s} v{a['version']:8s} {a['status']:10s}" for a in apps]
        return TerminalResult(text="\n".join(lines) if lines else "No apps")

    def _cmd_providers(self, args: list[str]) -> TerminalResult:
        if not self._kernel or not self._kernel.ai:
            return TerminalResult(error="No AI engine")
        try:
            providers = self._kernel.ai.list_providers()
        except Exception:
            providers = []
        if "--healthy" in args:
            providers = [p for p in providers if p.get("health", {}).get("healthy")]
        lines = [f"{p['id']:30s} {p.get('status', '?'):10s}" for p in providers]
        return TerminalResult(text="\n".join(lines) if lines else "No providers")

    def _cmd_search(self, args: list[str]) -> TerminalResult:
        if not args or args[0].startswith("--"):
            return TerminalResult(error="Usage: search <query> [--source SRC]")
        query = args[0]
        sources = None
        for i, a in enumerate(args):
            if a == "--source" and i + 1 < len(args):
                sources = [args[i + 1]]
        if self._query_engine:
            results = self._query_engine.search(query, sources=sources)
            lines = [f"[{r.relevance:.1f}] {r.label}" for r in results]
        elif self._kernel:
            results = self._kernel.search(query)
            lines = [f"[{r.get('relevance', 0):.1f}] {r.get('label', '?')}" for r in results]
        else:
            return TerminalResult(error="No search engine")
        return TerminalResult(text="\n".join(lines) if lines else "No results")

    def _cmd_knowledge(self, args: list[str]) -> TerminalResult:
        if not args:
            return TerminalResult(error="Usage: knowledge <query>")
        query = " ".join(args)
        if self._query_engine:
            results = self._query_engine.search(query, sources=["knowledge"])
        elif self._kernel:
            results = self._kernel.search(query)
        else:
            return TerminalResult(error="No knowledge engine")
        lines = [f"[{r.relevance:.1f}] {r.label[:100]}" for r in results]
        return TerminalResult(text="\n".join(lines) if lines else "No results")

    def _cmd_memory(self, args: list[str]) -> TerminalResult:
        if not args:
            return TerminalResult(error="Usage: memory <type> [--limit N]")
        return TerminalResult(text=f"Memory query: {args[0]} (stub)")

    def _cmd_timeline(self, args: list[str]) -> TerminalResult:
        if not self._kernel or not self._kernel.timeline:
            return TerminalResult(error="No timeline engine")
        try:
            entries = self._kernel.timeline.query(limit=20)
            lines = [str(e)[:100] for e in entries]
            return TerminalResult(text="\n".join(lines) if lines else "No timeline entries")
        except Exception as e:
            return TerminalResult(error=str(e))

    def _cmd_services(self, args: list[str]) -> TerminalResult:
        if not self._kernel or not self._kernel.registry:
            return TerminalResult(error="No service registry")
        try:
            services = self._kernel.registry.list()
        except Exception:
            services = []
        lines = [f"{s.get('name', '?'):20s} {s.get('version', '?'):8s} {s.get('status', '?'):10s}" for s in services]
        return TerminalResult(text="\n".join(lines) if lines else "No services")

    def _cmd_health(self, args: list[str]) -> TerminalResult:
        if not self._kernel:
            return TerminalResult(error="No kernel")
        try:
            h = self._kernel.health()
            lines = [
                f"State:     {h.status}",
                f"Uptime:    {h.uptime_seconds:.0f}s",
                f"Services:  {h.services_count}",
                f"Sessions:  {h.active_sessions}",
                f"Threads:   {h.threads}",
            ]
            if "--detail" in args:
                try:
                    lines.append(f"Messages:  {self._kernel.bus.message_count()}")
                    lines.append(f"Events:    {self._kernel.event_store.count() if self._kernel.event_store else 0}")
                except Exception:
                    pass
            return TerminalResult(text="\n".join(lines))
        except Exception as e:
            return TerminalResult(error=str(e))

    def _cmd_resources(self, args: list[str]) -> TerminalResult:
        if not self._resource_monitor:
            return TerminalResult(error="No resource monitor")
        s = self._resource_monitor.summary()
        return TerminalResult(data=s, format="json")

    def _cmd_lifecycle(self, args: list[str]) -> TerminalResult:
        if not self._lifecycle:
            return TerminalResult(error="No lifecycle manager")
        if not args:
            return TerminalResult(data=self._lifecycle.summary, format="json")
        action = args[0]
        if action == "pause":
            self._lifecycle.pause()
            return TerminalResult(text="Platform paused")
        elif action == "resume":
            self._lifecycle.resume()
            return TerminalResult(text="Platform resumed")
        elif action == "status":
            return TerminalResult(data=self._lifecycle.summary, format="json")
        else:
            return TerminalResult(error=f"Unknown lifecycle action: {action}")

    def _cmd_karpathy(self, args: list[str]) -> TerminalResult:
        if not args:
            return TerminalResult(error="Usage: karpathy <goal description> [verify_command]")
        goal = args[0]
        verify_cmd = args[1] if len(args) > 1 else "pytest"
        from genesis.agentos.karpathy import KarpathyExecutionEngine
        engine = KarpathyExecutionEngine(".")
        res = engine.execute_goal(goal, verify_cmd)
        lines = [
            f"Goal: {res.goal_description}",
            f"Success: {res.success}",
            f"Iterations: {res.iterations}",
            f"Assumptions: {res.thought.assumptions if res.thought else []}",
            f"Output:\n{res.final_verification_output[:300]}",
        ]
        return TerminalResult(text="\n".join(lines))

    def _cmd_apply_rules(self, args: list[str]) -> TerminalResult:
        path = args[0] if args else "."
        from genesis.karpathy_provisioning import provision_karpathy_rules
        res = provision_karpathy_rules(path)
        lines = [f"Provisioned rules at {path}:"] + [f"  {k}: {v}" for k, v in res.items()]
        return TerminalResult(text="\n".join(lines))
