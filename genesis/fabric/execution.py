"""
Agent Execution Engine (Mission 74) — wires AgentRuntime to AI providers.

Agents no longer simulate work. When assigned a task, the execution engine
finds the best available AI provider, constructs the proper system prompt
based on agent role, executes the task, and returns the result.

Flow:
  AgentInstance.assign_task(objective)
    → AgentExecutionEngine.execute(agent, task)
      → AIRouter.best_provider(capability)
        → AIProvider.chat(system_prompt + objective)
          → result returned to agent
            → agent.complete_task(task, result)
"""

from __future__ import annotations

import threading
import time
from typing import Any

from genesis.ai import Message, MessageRole
from genesis.fabric.agents import AgentInstance, AgentRole, AgentRuntime, AgentTask
from genesis.fabric.kernel import FabricKernel


ROLE_PROMPTS: dict[AgentRole, str] = {
    AgentRole.CHIEF_ENGINEER: (
        "You are the Chief Engineer of an autonomous engineering platform. "
        "You oversee all engineering operations, make architectural decisions, "
        "prioritize work, and ensure quality standards. Provide concise, "
        "authoritative engineering guidance."
    ),
    AgentRole.PRINCIPAL_ARCHITECT: (
        "You are a Principal Architect responsible for system design. "
        "You analyze architecture, identify technical debt, propose migrations, "
        "and ensure long-term architectural integrity. Be precise and thorough."
    ),
    AgentRole.REPOSITORY_SCIENTIST: (
        "You are a Repository Scientist. You analyze repositories to understand "
        "their structure, dependencies, patterns, and health. You produce "
        "structured engineering reports about repository state."
    ),
    AgentRole.ENGINEERING_RESEARCHER: (
        "You are an Engineering Researcher. You investigate problems, explore "
        "solutions, evaluate technologies, and produce evidence-backed "
        "recommendations. Always cite your sources and reasoning."
    ),
    AgentRole.PLANNER: (
        "You are a Planner. You decompose high-level goals into actionable "
        "engineering tasks with dependencies, estimated effort, and clear "
        "acceptance criteria. Be specific and practical."
    ),
    AgentRole.PRODUCT_MANAGER: (
        "You are a Product Manager. You define requirements, prioritize "
        "features, manage stakeholder expectations, and ensure the product "
        "delivers value. Balance business needs with engineering reality."
    ),
    AgentRole.ECONOMICS_ANALYST: (
        "You are an Economics Analyst. You analyze engineering economics, "
        "compute ROI, evaluate cost-benefit trade-offs, and optimize resource "
        "allocation. Base all analysis on quantitative evidence."
    ),
    AgentRole.BACKEND_ENGINEER: (
        "You are a Backend Engineer. You write Python code, design APIs, "
        "implement business logic, and optimize performance. Write clean, "
        "well-structured, production-quality code. Prefer simplicity."
    ),
    AgentRole.FRONTEND_ENGINEER: (
        "You are a Frontend Engineer. You build user interfaces that are "
        "beautiful, responsive, and accessible. You write clean TypeScript and "
        "CSS. Prioritize user experience and visual polish."
    ),
    AgentRole.KNOWLEDGE_ENGINEER: (
        "You are a Knowledge Engineer. You structure information into graphs, "
        "ontologies, and knowledge bases. You identify relationships, extract "
        "entities, and build representations that enable reasoning."
    ),
    AgentRole.DOCUMENTATION_ENGINEER: (
        "You are a Documentation Engineer. You write clear, comprehensive "
        "engineering documentation, API references, architecture guides, and "
        "user manuals. Be precise, organized, and readable."
    ),
    AgentRole.SECURITY_ENGINEER: (
        "You are a Security Engineer. You audit code for vulnerabilities, "
        "review security architecture, propose mitigations, and ensure "
        "compliance with security best practices. Be thorough and cautious."
    ),
    AgentRole.PERFORMANCE_ENGINEER: (
        "You are a Performance Engineer. You profile systems, identify "
        "bottlenecks, propose optimizations, and benchmark improvements. "
        "Base all recommendations on data and measurement."
    ),
    AgentRole.QUALITY_ENGINEER: (
        "You are a Quality Engineer. You review code quality, enforce "
        "standards, ensure test coverage, and prevent technical debt. "
        "Be constructive but rigorous in your reviews."
    ),
    AgentRole.TESTING_ENGINEER: (
        "You are a Testing Engineer. You write tests, design test "
        "strategies, implement test infrastructure, and ensure reliability. "
        "Cover edge cases, error paths, and integration scenarios."
    ),
    AgentRole.GOVERNANCE_AUDITOR: (
        "You are a Governance Auditor. You ensure compliance with "
        "architecture specifications, coding standards, and engineering "
        "policies. Identify violations and recommend corrective actions."
    ),
    AgentRole.MIGRATION_SPECIALIST: (
        "You are a Migration Specialist. You plan and execute code "
        "migrations, refactoring, and upgrades. Ensure backward compatibility "
        "and minimize disruption during transitions."
    ),
    AgentRole.SIMULATION_SCIENTIST: (
        "You are a Simulation Scientist. You build models, run simulations, "
        "and analyze system behavior under various conditions. Provide "
        "predictive insights backed by quantitative analysis."
    ),
    AgentRole.REVIEWER: (
        "You are a Code Reviewer. You review pull requests, provide "
        "actionable feedback, and enforce quality gates. Be thorough, "
        "specific, and constructive in all reviews."
    ),
    AgentRole.RELEASE_ENGINEER: (
        "You are a Release Engineer. You manage versioning, build pipelines, "
        "deployment processes, and release coordination. Ensure smooth, "
        "reliable releases with proper rollback plans."
    ),
}

DEFAULT_ROLE_PROMPT = (
    "You are an autonomous engineering agent. Execute the assigned task "
    "carefully and produce high-quality output."
)


class AgentExecutionEngine:
    """Executes agent tasks through AI providers.

    Usage:
        engine = AgentExecutionEngine(kernel, router)
        result = engine.execute(agent, task)
    """

    def __init__(self, kernel: FabricKernel | None = None,
                 router=None):
        self._kernel = kernel or FabricKernel.instance()
        self._router = router or self._kernel.ai
        self._execution_count = 0
        self._total_duration_ms = 0.0

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "execution_count": self._execution_count,
            "total_duration_ms": self._total_duration_ms,
            "avg_duration_ms": (
                self._total_duration_ms / self._execution_count
                if self._execution_count > 0 else 0.0
            ),
        }

    def execute(self, agent: AgentInstance, task: AgentTask,
                capability: str = "chat",
                provider_id: str | None = None,
                model: str | None = None) -> str:
        """Execute an agent task using the best available AI provider."""
        start = time.time()
        self._execution_count += 1

        system_prompt = self._build_system_prompt(agent, task)

        messages = [
            Message(role=MessageRole.SYSTEM, content=system_prompt),
            Message(role=MessageRole.USER, content=task.objective),
        ]

        if task.context:
            context_str = "\n".join(
                f"{k}: {v}" for k, v in task.context.items()
            )
            messages.append(
                Message(role=MessageRole.USER, content=f"Context:\n{context_str}")
            )

        try:
            response = self._router.chat(
                messages,
                provider=provider_id,
                model=model,
            )

            duration = (time.time() - start) * 1000
            self._total_duration_ms += duration

            result = response.content or ""

            self._kernel.emit("agent.execution.completed", {
                "agent_id": agent.agent_id,
                "task_id": task.task_id,
                "provider": response.provider,
                "model": response.model,
                "duration_ms": duration,
                "result_length": len(result),
                "usage": response.usage,
            }, origin="agent_execution_engine", tags=["agent", "execution"])

            return result

        except Exception as e:
            duration = (time.time() - start) * 1000
            self._kernel.emit("agent.execution.failed", {
                "agent_id": agent.agent_id,
                "task_id": task.task_id,
                "error": str(e),
                "duration_ms": duration,
            }, origin="agent_execution_engine", tags=["agent", "execution", "error"])
            raise

    def execute_sync(self, agent: AgentInstance, task: AgentTask) -> str:
        """Execute synchronously with automatic completion/failure handling."""
        try:
            result = self.execute(agent, task)
            agent.complete_task(task, result)
            return result
        except Exception as e:
            agent.fail_task(task, str(e))
            raise

    def _build_system_prompt(self, agent: AgentInstance,
                              task: AgentTask) -> str:
        """Build the system prompt for this agent role + task context."""
        role_prompt = ROLE_PROMPTS.get(
            agent.spec.role, DEFAULT_ROLE_PROMPT
        )

        parts = [role_prompt]
        if agent.spec.system_prompt:
            parts.append(agent.spec.system_prompt)

        parts.append(
            "You are part of the Genesis Engineering Operating System. "
            "All your work is tracked, audited, and persisted. "
            "Be concise, accurate, and actionable."
        )

        caps = task.context.get("required_capabilities") or \
                getattr(task, 'required_capabilities', None)
        if caps:
            parts.append(
                f"Required capabilities for this task: "
                f"{', '.join(caps)}"
            )

        return "\n\n".join(parts)

    def available_providers(self) -> list[dict[str, Any]]:
        """List available providers and their capabilities."""
        return self._router.list_providers()


class TaskExecutor:
    """Background loop that polls the task graph for ready tasks and executes them.

    Runs as a daemon thread inside FabricKernel. On each tick:
      1. Query TaskGraph for READY nodes whose dependencies are complete
      2. For each ready node, find an available agent with matching role
      3. Assign the task objective to the agent
      4. Execute through AgentExecutionEngine
      5. Mark the task node COMPLETED (or FAILED)
      6. Propagate to dependent nodes: check if any BLOCKED nodes become READY

    Usage:
        executor = TaskExecutor(kernel, graph, runtime, engine, poll_interval=2.0)
        executor.start()
        ...
        executor.stop()
    """

    def __init__(self, kernel: FabricKernel,
                 graph: TaskGraph,
                 runtime: AgentRuntime,
                 engine: AgentExecutionEngine,
                 poll_interval: float = 2.0):
        self._kernel = kernel
        self._graph = graph
        self._runtime = runtime
        self._engine = engine
        self._poll_interval = poll_interval
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._execution_count = 0
        self._failed_count = 0
        self._total_duration_ms = 0.0
        self._started_at = 0.0

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "running": self.is_running,
            "execution_count": self._execution_count,
            "failed_count": self._failed_count,
            "total_duration_ms": self._total_duration_ms,
            "avg_duration_ms": (
                self._total_duration_ms / self._execution_count
                if self._execution_count > 0 else 0.0
            ),
            "uptime_seconds": (time.time() - self._started_at) if self._started_at else 0.0,
            "poll_interval": self._poll_interval,
        }

    def start(self):
        if self.is_running:
            return
        self._stop_event.clear()
        self._started_at = time.time()
        self._thread = threading.Thread(target=self._run, daemon=True, name="task-executor")
        self._thread.start()
        try:
            self._kernel.emit("task_executor.started", {
                "poll_interval": self._poll_interval,
            }, origin="task_executor", tags=["executor"])
        except Exception:
            pass

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
        try:
            self._kernel.emit("task_executor.stopped", {
                "execution_count": self._execution_count,
                "uptime_seconds": (time.time() - self._started_at) if self._started_at else 0.0,
            }, origin="task_executor", tags=["executor"])
        except Exception:
            pass

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self._tick()
            except Exception:
                pass
            self._stop_event.wait(self._poll_interval)

    def _tick(self):
        ready = self._graph.get_ready_tasks()
        if not ready:
            return

        for node in ready:
            if self._stop_event.is_set():
                break

            agent = self._find_agent(node)
            if not agent:
                continue

            self._execute_node(node, agent)

    def _find_agent(self, node: TaskNode) -> AgentInstance | None:
        """Find an available agent matching the node's role requirements."""
        agents = self._runtime.list_agents()
        preferred_roles = node.required_agent_roles

        for agent in agents:
            if agent.status.value not in ("idle",):
                continue
            if preferred_roles:
                if agent.spec.role.value in preferred_roles:
                    return agent
            else:
                return agent

        return None

    def _execute_node(self, node, agent):
        tasks_mod = __import__("genesis.fabric.tasks", fromlist=["TaskStatus"])
        TaskStatus = tasks_mod.TaskStatus
        start = time.time()

        with self._lock:
            self._execution_count += 1

        self._graph.update_status(node.id, TaskStatus.RUNNING)

        try:
            task = agent.assign_task(
                objective=node.title,
                context={
                    "node_id": node.id,
                    "node_type": node.node_type.value,
                    "description": node.description,
                    "required_capabilities": node.required_capabilities,
                },
            )

            result = self._engine.execute(agent, task)

            agent.complete_task(task, result)

            node.progress = 1.0
            self._graph.update_status(node.id, TaskStatus.COMPLETED)

            duration = (time.time() - start) * 1000
            with self._lock:
                self._total_duration_ms += duration

            self._kernel.emit("task_executor.node.completed", {
                "node_id": node.id, "agent_id": agent.agent_id,
                "duration_ms": duration,
            }, origin="task_executor", tags=["executor"])

            self._propagate_completion(node)

        except Exception as e:
            with self._lock:
                self._failed_count += 1
                self._total_duration_ms += (time.time() - start) * 1000

            self._graph.update_status(node.id, TaskStatus.FAILED)

            try:
                agent.fail_task(task, str(e))
            except Exception:
                pass

            self._kernel.emit("task_executor.node.failed", {
                "node_id": node.id, "agent_id": agent.agent_id,
                "error": str(e),
            }, origin="task_executor", severity="error", tags=["executor"])

    def _propagate_completion(self, node):
        """After a node completes, check dependent nodes that may now be READY."""
        tasks_mod = __import__("genesis.fabric.tasks", fromlist=["TaskStatus"])
        TaskStatus = tasks_mod.TaskStatus
        for dep_id in node.blocking:
            dep = self._graph.get_node(dep_id)
            if not dep:
                continue
            if dep.status != TaskStatus.BLOCKED:
                continue
            all_deps_complete = all(
                (n := self._graph.get_node(d)) and n.is_complete
                for d in dep.dependencies
            )
            if all_deps_complete:
                self._graph.update_status(dep.id, TaskStatus.READY)
                self._kernel.emit("task_executor.node.unblocked", {
                    "node_id": dep.id,
                }, origin="task_executor", tags=["executor"])
