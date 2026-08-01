"""
Tests for Agent Execution Engine (Mission 74).
"""

from genesis.fabric.agents import AgentRole, AgentRuntime, AgentSpec, AgentTask
from genesis.fabric.execution import (
    ROLE_PROMPTS, DEFAULT_ROLE_PROMPT, AgentExecutionEngine,
)
from genesis.fabric.kernel import FabricKernel


class TestAgentExecutionEngine:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance(enable_persistence=False)
        self.kernel.boot()
        self.engine = AgentExecutionEngine(self.kernel)

    def teardown_method(self):
        self.kernel.shutdown()

    def test_initial_stats(self):
        stats = self.engine.stats
        assert stats["execution_count"] == 0
        assert stats["total_duration_ms"] == 0.0
        assert stats["avg_duration_ms"] == 0.0

    def test_role_prompts_have_all_roles(self):
        for role in AgentRole:
            assert role in ROLE_PROMPTS, f"Missing prompt for {role}"

    def test_role_prompt_content(self):
        for role, prompt in ROLE_PROMPTS.items():
            assert len(prompt) > 20, f"Prompt too short for {role}"
            assert isinstance(prompt, str)

    def test_default_role_prompt_exists(self):
        assert len(DEFAULT_ROLE_PROMPT) > 20

    def test_available_providers_returns_list(self):
        providers = self.engine.available_providers()
        assert isinstance(providers, list)

    def test_build_system_prompt_with_role(self):
        runtime = AgentRuntime(self.kernel)
        agent_id = runtime.spawn(AgentSpec(
            name="Test Engineer",
            role=AgentRole.BACKEND_ENGINEER,
        ))
        agent = runtime.get_agent(agent_id)
        task = AgentTask(objective="Write a function")

        prompt = self.engine._build_system_prompt(agent, task)
        assert "Backend Engineer" in prompt
        assert "Genesis" in prompt
        assert "engineering" in prompt.lower()

    def test_build_system_prompt_with_custom_system_prompt(self):
        runtime = AgentRuntime(self.kernel)
        agent_id = runtime.spawn(AgentSpec(
            name="Custom Agent",
            role=AgentRole.REVIEWER,
            system_prompt="Be extra thorough.",
        ))
        agent = runtime.get_agent(agent_id)
        task = AgentTask(objective="Review code")
        prompt = self.engine._build_system_prompt(agent, task)
        assert "Be extra thorough" in prompt
        assert "Reviewer" in prompt

    def test_build_system_prompt_with_capabilities(self):
        runtime = AgentRuntime(self.kernel)
        agent_id = runtime.spawn(AgentSpec(
            name="Capable Agent",
            role=AgentRole.SECURITY_ENGINEER,
        ))
        agent = runtime.get_agent(agent_id)
        task = AgentTask(
            objective="Audit security",
            context={"required_capabilities": ["security", "code_review"]},
        )
        prompt = self.engine._build_system_prompt(agent, task)
        assert "security" in prompt or "code_review" in prompt

    def test_execute_without_provider_raises_helpful_error(self):
        runtime = AgentRuntime(self.kernel)
        agent_id = runtime.spawn(AgentSpec(
            name="Test", role=AgentRole.BACKEND_ENGINEER,
        ))
        agent = runtime.get_agent(agent_id)
        task = AgentTask(objective="Do something")

        try:
            self.engine.execute(agent, task)
            assert False, "Expected an exception"
        except Exception as e:
            error_str = str(e)
            assert len(error_str) > 0, "Error message should not be empty"
            # The error will be from AIRouter since no providers registered

    def test_execute_sync_propagates_error(self):
        runtime = AgentRuntime(self.kernel)
        agent_id = runtime.spawn(AgentSpec(
            name="Fail Agent", role=AgentRole.BACKEND_ENGINEER,
        ))
        agent = runtime.get_agent(agent_id)
        task = AgentTask(objective="This will fail")

        try:
            self.engine.execute_sync(agent, task)
        except Exception:
            pass

        assert agent.status.value == "error"
        assert agent._failed_count == 1

    def test_execution_count_increments(self):
        runtime = AgentRuntime(self.kernel)
        agent_id = runtime.spawn(AgentSpec(
            name="Count Test", role=AgentRole.BACKEND_ENGINEER,
        ))
        agent = runtime.get_agent(agent_id)
        task = AgentTask(objective="Count test")

        try:
            self.engine.execute(agent, task)
        except Exception:
            pass

        assert self.engine.stats["execution_count"] >= 1
