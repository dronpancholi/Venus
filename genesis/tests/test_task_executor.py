"""
Tests for TaskExecutor (Cycle 010) — background task execution loop.
"""

import time
from unittest.mock import MagicMock

from genesis.fabric.kernel import FabricKernel, KernelState
from genesis.fabric.tasks import TaskGraph, TaskNode, TaskNodeType, TaskStatus
from genesis.fabric.agents import AgentRuntime, AgentSpec, AgentRole, AgentTask, AgentStatus
from genesis.fabric.execution import AgentExecutionEngine, TaskExecutor


class TestTaskExecutorLifecycle:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance(enable_persistence=False)
        self.kernel.boot()
        self.graph = TaskGraph(kernel=self.kernel)
        self.runtime = AgentRuntime(kernel=self.kernel)

    def teardown_method(self):
        try:
            self.kernel.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None

    def test_start_stop(self):
        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=MagicMock(),
            poll_interval=0.1,
        )
        assert not executor.is_running
        executor.start()
        assert executor.is_running
        executor.stop()
        assert not executor.is_running

    def test_double_start(self):
        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=MagicMock(),
            poll_interval=0.1,
        )
        executor.start()
        executor.start()
        assert executor.is_running
        executor.stop()

    def test_stats(self):
        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=MagicMock(),
            poll_interval=1.0,
        )
        stats = executor.stats
        assert stats["running"] is False
        assert stats["execution_count"] == 0
        assert stats["failed_count"] == 0
        assert stats["poll_interval"] == 1.0

        executor.start()
        time.sleep(0.05)
        stats = executor.stats
        assert stats["running"] is True
        executor.stop()


class TestTaskExecutorFindAgent:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance(enable_persistence=False)
        self.kernel.boot()
        self.graph = TaskGraph(kernel=self.kernel)
        self.runtime = AgentRuntime(kernel=self.kernel)
        self.engine = MagicMock()

    def teardown_method(self):
        try:
            self.kernel.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None

    def test_find_agent_prefers_matching_role(self):
        engineer_id = self.runtime.spawn(AgentSpec(
            name="Engineer", role=AgentRole.BACKEND_ENGINEER,
        ))
        self.runtime.spawn(AgentSpec(
            name="Architect", role=AgentRole.PRINCIPAL_ARCHITECT,
        ))

        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=self.engine,
        )

        node = TaskNode(
            title="Fix bug", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
            required_agent_roles=["backend_engineer"],
        )
        agent = executor._find_agent(node)
        assert agent is not None
        assert agent.agent_id == engineer_id
        assert agent.spec.role == AgentRole.BACKEND_ENGINEER

    def test_find_agent_returns_none_if_no_idle_agents(self):
        self.runtime.spawn(AgentSpec(
            name="Busy", role=AgentRole.BACKEND_ENGINEER,
        ))

        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=self.engine,
        )

        agent = self.runtime.get_agent(
            self.runtime.list_agents()[0].agent_id
        )
        agent.status = AgentStatus.RUNNING

        node = TaskNode(
            title="Task", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
            required_agent_roles=["backend_engineer"],
        )
        result = executor._find_agent(node)
        assert result is None

    def test_find_agent_returns_any_idle_agent_without_role_req(self):
        agent_id = self.runtime.spawn(AgentSpec(
            name="Any", role=AgentRole.BACKEND_ENGINEER,
        ))

        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=self.engine,
        )

        node = TaskNode(
            title="Task", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        agent = executor._find_agent(node)
        assert agent is not None
        assert agent.agent_id == agent_id


class TestTaskExecutorPropagation:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance(enable_persistence=False)
        self.kernel.boot()
        self.graph = TaskGraph(kernel=self.kernel)
        self.runtime = AgentRuntime(kernel=self.kernel)
        self.engine = MagicMock()

    def teardown_method(self):
        try:
            self.kernel.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None

    def test_propagate_completion_unblocks_dependent(self):
        parent = TaskNode(
            title="Parent", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        child = TaskNode(
            title="Child", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.BLOCKED,
            dependencies=[parent.id],
        )
        self.graph.add_node(parent)
        self.graph.add_node(child)
        self.graph.add_dependency(child.id, parent.id)

        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=self.engine,
        )

        parent.status = TaskStatus.COMPLETED
        executor._propagate_completion(parent)

        child_node = self.graph.get_node(child.id)
        assert child_node is not None
        assert child_node.status == TaskStatus.READY

    def test_propagate_completion_skips_non_blocked(self):
        parent = TaskNode(
            title="Parent", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        child = TaskNode(
            title="Child", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
            dependencies=[parent.id],
        )
        self.graph.add_node(parent)
        self.graph.add_node(child)
        self.graph.add_dependency(child.id, parent.id)

        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=self.engine,
        )

        parent.status = TaskStatus.COMPLETED
        executor._propagate_completion(parent)

        child_node = self.graph.get_node(child.id)
        assert child_node is not None
        assert child_node.status == TaskStatus.READY

    def test_propagate_completion_waits_for_all_deps(self):
        parent_a = TaskNode(
            title="Parent A", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        parent_b = TaskNode(
            title="Parent B", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.PENDING,
        )
        child = TaskNode(
            title="Child", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.BLOCKED,
            dependencies=[parent_a.id, parent_b.id],
        )
        self.graph.add_node(parent_a)
        self.graph.add_node(parent_b)
        self.graph.add_node(child)
        self.graph.add_dependency(child.id, parent_a.id)
        self.graph.add_dependency(child.id, parent_b.id)

        executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=self.engine,
        )

        parent_a.status = TaskStatus.COMPLETED
        executor._propagate_completion(parent_a)

        child_node = self.graph.get_node(child.id)
        assert child_node is not None
        assert child_node.status == TaskStatus.BLOCKED

        parent_b.status = TaskStatus.COMPLETED
        executor._propagate_completion(parent_b)

        child_node = self.graph.get_node(child.id)
        assert child_node is not None
        assert child_node.status == TaskStatus.READY


class TestTaskExecutorTick:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance(enable_persistence=False)
        self.kernel.boot()
        self.graph = TaskGraph(kernel=self.kernel)
        self.runtime = AgentRuntime(kernel=self.kernel)
        self.engine = MagicMock()
        self.engine.execute.return_value = "Task result"

        self.executor = TaskExecutor(
            kernel=self.kernel, graph=self.graph,
            runtime=self.runtime, engine=self.engine,
            poll_interval=0.1,
        )

    def teardown_method(self):
        try:
            self.executor.stop()
        except Exception:
            pass
        try:
            self.kernel.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None

    def test_tick_executes_ready_task(self):
        agent_id = self.runtime.spawn(AgentSpec(
            name="Worker", role=AgentRole.BACKEND_ENGINEER,
        ))
        node = TaskNode(
            title="Do work", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        self.graph.add_node(node)

        self.executor._tick()

        agent = self.runtime.get_agent(agent_id)
        assert agent is not None
        assert agent.status == AgentStatus.IDLE
        assert agent._completed_count == 1

        node_updated = self.graph.get_node(node.id)
        assert node_updated is not None
        assert node_updated.status == TaskStatus.COMPLETED

    def test_tick_skips_without_agents(self):
        node = TaskNode(
            title="No agents", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        self.graph.add_node(node)

        self.executor._tick()

        node_updated = self.graph.get_node(node.id)
        assert node_updated is not None
        assert node_updated.status == TaskStatus.READY

    def test_tick_handles_execution_failure(self):
        self.runtime.spawn(AgentSpec(
            name="Worker", role=AgentRole.BACKEND_ENGINEER,
        ))
        self.engine.execute.side_effect = RuntimeError("Execution failed")

        node = TaskNode(
            title="Will fail", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        self.graph.add_node(node)

        self.executor._tick()

        node_updated = self.graph.get_node(node.id)
        assert node_updated is not None
        assert node_updated.status == TaskStatus.FAILED
        assert self.executor.stats["failed_count"] == 1

    def test_tick_propagates_to_dependents(self):
        self.runtime.spawn(AgentSpec(
            name="Worker", role=AgentRole.BACKEND_ENGINEER,
        ))

        parent = TaskNode(
            title="Parent", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        child = TaskNode(
            title="Child", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.BLOCKED,
            dependencies=[parent.id],
        )
        self.graph.add_node(parent)
        self.graph.add_node(child)
        self.graph.add_dependency(child.id, parent.id)

        self.executor._tick()

        parent_updated = self.graph.get_node(parent.id)
        assert parent_updated is not None
        assert parent_updated.status == TaskStatus.COMPLETED

        child_updated = self.graph.get_node(child.id)
        assert child_updated is not None
        assert child_updated.status == TaskStatus.READY

    def test_multiple_ticks_process_chain(self):
        self.runtime.spawn(AgentSpec(
            name="Worker", role=AgentRole.BACKEND_ENGINEER,
        ))

        node1 = TaskNode(
            title="Step 1", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.READY,
        )
        node2 = TaskNode(
            title="Step 2", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.BLOCKED,
            dependencies=[node1.id],
        )
        node3 = TaskNode(
            title="Step 3", node_type=TaskNodeType.ENGINEERING_TASK,
            status=TaskStatus.BLOCKED,
            dependencies=[node2.id],
        )
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        self.graph.add_node(node3)
        self.graph.add_dependency(node2.id, node1.id)
        self.graph.add_dependency(node3.id, node2.id)

        self.executor._tick()

        assert self.graph.get_node(node1.id).status == TaskStatus.COMPLETED
        assert self.graph.get_node(node2.id).status == TaskStatus.READY

        self.executor._tick()

        assert self.graph.get_node(node2.id).status == TaskStatus.COMPLETED
        assert self.graph.get_node(node3.id).status == TaskStatus.READY

        self.executor._tick()

        assert self.graph.get_node(node3.id).status == TaskStatus.COMPLETED

        assert self.executor.stats["execution_count"] == 3
        assert self.executor.stats["failed_count"] == 0


class TestTaskExecutorKernelIntegration:
    def setup_method(self):
        FabricKernel._instance = None

    def teardown_method(self):
        try:
            kernel = FabricKernel.instance()
            kernel.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None

    def test_boot_creates_executor(self):
        kernel = FabricKernel.instance(enable_persistence=False)
        kernel.boot()

        assert kernel.task_executor is not None
        assert kernel.task_executor.is_running

    def test_shutdown_stops_executor(self):
        kernel = FabricKernel.instance(enable_persistence=False)
        kernel.boot()

        assert kernel.task_executor.is_running

        kernel.shutdown()
        assert not kernel.task_executor.is_running

    def test_stats_includes_executor(self):
        kernel = FabricKernel.instance(enable_persistence=False)
        kernel.boot()

        stats = kernel.stats()
        assert stats.executor_running is True

        kernel.shutdown()
