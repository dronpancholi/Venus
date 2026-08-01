from __future__ import annotations

import importlib
import pkgutil
import threading
import time
from typing import Any, Iterator

from genesis.ai import (
    AIProvider, ChatResponse, Chunk, EmbeddingResponse, Message, ProviderCapability, ToolSpec,
)
from genesis.ai.registry import ProviderRegistry
from genesis.ai.router import AIRouter, ConsensusResult, RoutingDecision
from genesis.config.settings import config as platform_config
from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


class AIOrchestrationEngine:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._router = AIRouter()
        self._registry = ProviderRegistry
        self._engineering = get_registry()
        self._lock = threading.RLock()
        self._provider_objects: dict[str, str] = {}

    @property
    def router(self) -> AIRouter:
        return self._router

    @property
    def registry(self) -> type[ProviderRegistry]:
        return self._registry

    def boot(self):
        self._auto_discover_providers()

    def _auto_discover_providers(self):
        try:
            pkg = importlib.import_module("genesis.ai.providers")
            for _, name, is_pkg in pkgutil.iter_modules(pkg.__path__, prefix="genesis.ai.providers."):
                if is_pkg:
                    continue
                try:
                    mod = importlib.import_module(name)
                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if isinstance(attr, type) and issubclass(attr, AIProvider) and attr is not AIProvider:
                            try:
                                provider = attr(
                                    api_key=platform_config.ai_api_key or "",
                                    base_url=platform_config.ai_base_url or "",
                                )
                            except Exception:
                                provider = attr()
                            self._register_provider(provider)
                except Exception:
                    pass
        except Exception:
            pass

    def _register_provider(self, provider: AIProvider):
        with self._lock:
            self._registry.register(provider)
            try:
                caps = provider.check_capabilities()
                self._registry.set_capabilities(provider.provider_id, caps)
            except Exception:
                pass
            try:
                health = provider.health()
                self._registry.set_health(provider.provider_id, health)
            except Exception:
                pass
            obj = EngineeringObject(
                object_type=EngineeringObjectType.PROVIDER,
                name=provider.provider_id,
                description=f"AI Provider: {provider.provider_id} — {len(provider.models)} models",
                tags=["ai_provider", "ai"],
                metadata={
                    "provider_id": provider.provider_id,
                    "models": [m.id for m in provider.models],
                    "default_model": provider.get_default_model(),
                },
            )
            self._engineering.register(obj)
            self._provider_objects[provider.provider_id] = obj.id
            if self._kernel:
                self._kernel.emit("ai.provider.registered", {
                    "provider_id": provider.provider_id,
                    "models": [m.id for m in provider.models],
                }, origin="ai", tags=["ai"])

    def chat(
        self,
        messages: list[Message],
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> ChatResponse:
        return self._router.chat(messages, provider=provider, model=model, **kwargs)

    def stream_chat(
        self,
        messages: list[Message],
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> Iterator[Chunk]:
        return self._router.stream_chat(messages, provider=provider, model=model, **kwargs)

    def embeddings(
        self,
        texts: list[str],
        provider: str | None = None,
        model: str | None = None,
    ) -> EmbeddingResponse:
        return self._router.embeddings(texts, provider=provider, model=model)

    def tool_call(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> ChatResponse:
        return self._router.tool_call(messages, tools, provider=provider, model=model, **kwargs)

    def parallel_chat(
        self,
        messages: list[Message],
        providers: list[str] | None = None,
        model: str | None = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> list[tuple[str, ChatResponse | None, str | None]]:
        return self._router.parallel_chat(messages, providers=providers, model=model, timeout=timeout, **kwargs)

    def consensus_chat(
        self,
        messages: list[Message],
        min_providers: int = 2,
        model: str | None = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> ConsensusResult:
        return self._router.consensus_chat(messages, min_providers=min_providers, model=model, timeout=timeout, **kwargs)

    def best_of_n(
        self,
        messages: list[Message],
        n: int = 3,
        model: str | None = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> ChatResponse:
        return self._router.best_of_n(messages, n=n, model=model, timeout=timeout, **kwargs)

    def routing_decision(self, capability: str = "chat") -> RoutingDecision:
        return self._router.routing_decision(capability)

    def best_provider(self, capability: str = "chat") -> AIProvider:
        return self._router.best_provider(capability)

    def list_providers(self) -> list[dict[str, Any]]:
        results = []
        for pid in self._registry.list_provider_ids():
            prov = self._registry.get(pid)
            health = self._registry.get_health(pid)
            caps = self._registry.get_capabilities(pid)
            bench = self._registry.get_benchmark(pid)
            results.append({
                "id": pid,
                "models": [m.id for m in prov.models] if prov else [],
                "healthy": health.healthy if health else False,
                "capabilities": [c.name for c in caps.capabilities] if caps else [],
                "latency_ms": health.latency_ms if health else 0.0,
                "benchmark_score": bench.success_rate if bench else None,
            })
        return results

    def summarize(self) -> dict[str, Any]:
        raw = self._registry.summarize()
        raw["available"] = self._registry.list_provider_ids()
        return raw

    def health(self) -> dict[str, Any]:
        try:
            prov = self.best_provider()
            return {
                "healthy": True,
                "providers": len(self._registry.list_providers()),
                "available": self._registry.list_provider_ids(),
                "best_provider": prov.provider_id if prov else None,
            }
        except RuntimeError:
            return {
                "healthy": False,
                "providers": 0,
                "available": [],
                "best_provider": None,
            }
