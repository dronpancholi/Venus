"""
Tests for AI Provider Platform (Mission 32).
"""

import pytest
from genesis.ai import (
    AIProvider, ChatResponse, Chunk, EmbeddingResponse, Message,
    MessageRole, ModelSpec, ProviderCapabilities, ProviderCapability,
    ProviderHealth, ToolSpec, ToolParameter,
)
from genesis.ai.registry import ProviderRegistry
from genesis.ai.router import AIRouter


class FakeProvider(AIProvider):
    provider_id = "test_provider"

    def __init__(self, healthy: bool = True):
        self.models = [ModelSpec(id="test-model", name="Test Model", is_default=True)]
        self._healthy = healthy
        self.chat_calls = 0
        self.stream_calls = 0
        self.embed_calls = 0
        self.tool_calls = 0

    def chat(self, messages, model=None, **kwargs):
        self.chat_calls += 1
        return ChatResponse(content="test response", model="test-model", provider=self.provider_id)

    def stream_chat(self, messages, model=None, **kwargs):
        self.stream_calls += 1
        yield Chunk(content="test ")
        yield Chunk(content="stream")
        yield Chunk(content="", done=True)

    def embeddings(self, texts, model=None):
        self.embed_calls += 1
        return EmbeddingResponse(vectors=[[0.1, 0.2, 0.3]] * len(texts), model="test-model", provider=self.provider_id)

    def tool_call(self, messages, tools, model=None, **kwargs):
        self.tool_calls += 1
        return ChatResponse(content="tool result", model="test-model", provider=self.provider_id,
                            tool_calls=[{"function": {"name": "test"}}])

    def check_capabilities(self):
        return ProviderCapabilities(
            capabilities={ProviderCapability.CHAT, ProviderCapability.STREAMING,
                         ProviderCapability.EMBEDDINGS, ProviderCapability.TOOL_CALLING,
                         ProviderCapability.CODE_GENERATION},
        )

    def health(self):
        return ProviderHealth(healthy=self._healthy)


class StreamingOnlyProvider(AIProvider):
    provider_id = "stream_only"

    def __init__(self):
        self.models = [ModelSpec(id="stream-model", name="Stream Model", is_default=True,
                                 supports_embeddings=False, supports_tools=False)]

    def chat(self, messages, model=None, **kwargs):
        raise NotImplementedError("No chat, only streaming")

    def stream_chat(self, messages, model=None, **kwargs):
        yield Chunk(content="stream only")
        yield Chunk(content="", done=True)

    def embeddings(self, texts, model=None):
        raise NotImplementedError("No embeddings")

    def tool_call(self, messages, tools, model=None, **kwargs):
        raise NotImplementedError("No tool calling")

    def check_capabilities(self):
        return ProviderCapabilities(capabilities={ProviderCapability.CHAT, ProviderCapability.STREAMING})

    def health(self):
        return ProviderHealth(healthy=True)


# ── ProviderRegistry ────────────────────────────────────────────────────

class TestProviderRegistry:
    def setup_method(self):
        ProviderRegistry._providers.clear()
        ProviderRegistry._benchmarks.clear()
        ProviderRegistry._capabilities.clear()
        ProviderRegistry._health_cache.clear()

    def test_register_and_get(self):
        p = FakeProvider()
        ProviderRegistry.register(p)
        assert ProviderRegistry.get("test_provider") is p

    def test_register_overwrites(self):
        p1 = FakeProvider()
        p2 = FakeProvider()
        ProviderRegistry.register(p1)
        ProviderRegistry.register(p2)
        assert ProviderRegistry.get("test_provider") is p2

    def test_unregister(self):
        ProviderRegistry.register(FakeProvider())
        ProviderRegistry.unregister("test_provider")
        assert ProviderRegistry.get("test_provider") is None

    def test_list_providers(self):
        ProviderRegistry.register(FakeProvider())
        ProviderRegistry.register(StreamingOnlyProvider())
        assert len(ProviderRegistry.list_providers()) == 2

    def test_healthy_providers(self):
        ProviderRegistry.register(FakeProvider(healthy=True))
        ProviderRegistry.register(FakeProvider(healthy=False))
        ProviderRegistry.set_health("test_provider", ProviderHealth(healthy=True))
        ProviderRegistry.set_health("test_provider", ProviderHealth(healthy=False, message="down"))
        # Need distinct IDs for healthy vs unhealthy
        ProviderRegistry._providers.clear()
        hp = FakeProvider(healthy=True)
        hp.provider_id = "healthy_prov"
        up = FakeProvider(healthy=False)
        up.provider_id = "unhealthy_prov"
        ProviderRegistry.register(hp)
        ProviderRegistry.register(up)
        ProviderRegistry.set_health("healthy_prov", ProviderHealth(healthy=True))
        ProviderRegistry.set_health("unhealthy_prov", ProviderHealth(healthy=False))
        healthy = ProviderRegistry.healthy_providers()
        assert len(healthy) == 1
        assert healthy[0].provider_id == "healthy_prov"

    def test_capabilities(self):
        ProviderRegistry.register(FakeProvider())
        caps = ProviderCapabilities(capabilities={ProviderCapability.CHAT})
        ProviderRegistry.set_capabilities("test_provider", caps)
        assert ProviderRegistry.get_capabilities("test_provider") is caps

    def test_summary(self):
        p = FakeProvider()
        p.provider_id = "p1"
        ProviderRegistry.register(p)
        ProviderRegistry.set_health("p1", ProviderHealth(healthy=True))
        s = ProviderRegistry.summarize()
        assert s["total"] == 1
        assert s["healthy"] == 1

    def test_benchmark(self):
        from genesis.ai import BenchmarkResult
        b = BenchmarkResult(provider_id="test", model="m")
        ProviderRegistry.set_benchmark("test", b)
        assert ProviderRegistry.get_benchmark("test") is b


# ── AIRouter ────────────────────────────────────────────────────────────

class TestAIRouter:
    def setup_method(self):
        ProviderRegistry._providers.clear()
        ProviderRegistry._benchmarks.clear()
        ProviderRegistry._capabilities.clear()
        ProviderRegistry._health_cache.clear()

    def test_chat_routing(self):
        p = FakeProvider()
        ProviderRegistry.register(p)
        ProviderRegistry.set_health(p.provider_id, ProviderHealth(healthy=True))
        ProviderRegistry.set_capabilities(p.provider_id, p.check_capabilities())
        router = AIRouter()
        resp = router.chat([Message(role=MessageRole.USER, content="hello")])
        assert resp.content == "test response"
        assert p.chat_calls == 1

    def test_stream_chat(self):
        p = FakeProvider()
        ProviderRegistry.register(p)
        ProviderRegistry.set_health(p.provider_id, ProviderHealth(healthy=True))
        ProviderRegistry.set_capabilities(p.provider_id, p.check_capabilities())
        router = AIRouter()
        chunks = list(router.stream_chat([Message(role=MessageRole.USER, content="hi")]))
        assert len(chunks) == 3
        assert p.stream_calls == 1

    def test_embeddings(self):
        p = FakeProvider()
        ProviderRegistry.register(p)
        ProviderRegistry.set_health(p.provider_id, ProviderHealth(healthy=True))
        ProviderRegistry.set_capabilities(p.provider_id, p.check_capabilities())
        router = AIRouter()
        resp = router.embeddings(["hello", "world"])
        assert len(resp.vectors) == 2
        assert p.embed_calls == 1

    def test_tool_call(self):
        p = FakeProvider()
        ProviderRegistry.register(p)
        ProviderRegistry.set_health(p.provider_id, ProviderHealth(healthy=True))
        ProviderRegistry.set_capabilities(p.provider_id, p.check_capabilities())
        router = AIRouter()
        resp = router.tool_call(
            [Message(role=MessageRole.USER, content="do something")],
            [ToolSpec(name="test", description="test", parameters=[ToolParameter(name="x", type="string", description="x")])],
        )
        assert resp.tool_calls is not None
        assert p.tool_calls == 1

    def test_specific_provider(self):
        p1 = FakeProvider()
        p1.provider_id = "p1"
        p2 = FakeProvider()
        p2.provider_id = "p2"
        ProviderRegistry.register(p1)
        ProviderRegistry.register(p2)
        ProviderRegistry.set_health("p1", ProviderHealth(healthy=True))
        ProviderRegistry.set_health("p2", ProviderHealth(healthy=True))
        router = AIRouter()
        resp = router.chat([Message(role=MessageRole.USER, content="h")], provider="p2")
        assert resp.provider == "p2"

    def test_no_healthy_providers_raises(self):
        router = AIRouter()
        with pytest.raises(RuntimeError, match="No healthy providers"):
            router.best_provider("chat")

    def test_routing_decision(self):
        p = FakeProvider()
        ProviderRegistry.register(p)
        ProviderRegistry.set_health(p.provider_id, ProviderHealth(healthy=True))
        ProviderRegistry.set_capabilities(p.provider_id, p.check_capabilities())
        router = AIRouter()
        decision = router.routing_decision("chat")
        assert decision.provider_id == "test_provider"
        assert decision.confidence > 0
        assert len(decision.reason) > 0

    def test_routing_decision_no_providers(self):
        router = AIRouter()
        decision = router.routing_decision("chat")
        assert decision.confidence == 0.0
        assert decision.provider_id == ""

    def test_unknown_provider_raises(self):
        router = AIRouter()
        with pytest.raises(ValueError, match="Provider not found"):
            router.chat([Message(role=MessageRole.USER, content="h")], provider="does_not_exist")


# ── ModelSpec ───────────────────────────────────────────────────────────

class TestModelSpec:
    def test_default_model_selection(self):
        p = FakeProvider()
        assert p.get_default_model() == "test-model"

    def test_no_default_falls_to_first(self):
        p = FakeProvider()
        p.models = [ModelSpec(id="m1", name="M1", is_default=False),
                    ModelSpec(id="m2", name="M2", is_default=True)]
        assert p.get_default_model() == "m2"

    def test_no_models_returns_empty(self):
        p = FakeProvider()
        p.models = []
        assert p.get_default_model() == ""


# ── ToolSpec ────────────────────────────────────────────────────────────

class TestToolSpec:
    def test_to_openai_format(self):
        t = ToolSpec("my_tool", "Does something", [
            ToolParameter("x", "string", "The X value", required=True),
            ToolParameter("y", "number", "The Y value", required=False),
        ])
        oa = t.to_openai_format()
        assert oa["function"]["name"] == "my_tool"
        assert "x" in oa["function"]["parameters"]["properties"]
        assert "y" in oa["function"]["parameters"]["properties"]
        assert oa["function"]["parameters"]["required"] == ["x"]

    def test_to_openai_format_no_params(self):
        t = ToolSpec("empty", "No params")
        oa = t.to_openai_format()
        assert oa["function"]["name"] == "empty"
        assert oa["function"]["parameters"]["required"] == []


# ── Message ─────────────────────────────────────────────────────────────

class TestMessage:
    def test_system_message(self):
        m = Message(role=MessageRole.SYSTEM, content="You are a bot")
        assert m.role == MessageRole.SYSTEM
        assert m.content == "You are a bot"

    def test_tool_message(self):
        m = Message(role=MessageRole.TOOL, content="result", tool_call_id="call_1")
        assert m.tool_call_id == "call_1"
