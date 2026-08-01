from __future__ import annotations

import threading
from typing import Any

from genesis.ai import AIProvider, BenchmarkResult, ProviderCapabilities, ProviderHealth


class ProviderRegistry:
    _providers: dict[str, AIProvider] = {}
    _lock = threading.RLock()
    _benchmarks: dict[str, BenchmarkResult] = {}
    _capabilities: dict[str, ProviderCapabilities] = {}
    _health_cache: dict[str, ProviderHealth] = {}

    @classmethod
    def register(cls, provider: AIProvider):
        with cls._lock:
            cls._providers[provider.provider_id] = provider

    @classmethod
    def unregister(cls, provider_id: str):
        with cls._lock:
            cls._providers.pop(provider_id, None)
            cls._benchmarks.pop(provider_id, None)
            cls._capabilities.pop(provider_id, None)
            cls._health_cache.pop(provider_id, None)

    @classmethod
    def get(cls, provider_id: str) -> AIProvider | None:
        return cls._providers.get(provider_id)

    @classmethod
    def list_providers(cls) -> list[AIProvider]:
        return list(cls._providers.values())

    @classmethod
    def list_provider_ids(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    def get_benchmark(cls, provider_id: str) -> BenchmarkResult | None:
        return cls._benchmarks.get(provider_id)

    @classmethod
    def set_benchmark(cls, provider_id: str, benchmark: BenchmarkResult):
        with cls._lock:
            cls._benchmarks[provider_id] = benchmark

    @classmethod
    def get_capabilities(cls, provider_id: str) -> ProviderCapabilities | None:
        return cls._capabilities.get(provider_id)

    @classmethod
    def set_capabilities(cls, provider_id: str, caps: ProviderCapabilities):
        with cls._lock:
            cls._capabilities[provider_id] = caps

    @classmethod
    def get_health(cls, provider_id: str) -> ProviderHealth | None:
        return cls._health_cache.get(provider_id)

    @classmethod
    def set_health(cls, provider_id: str, health: ProviderHealth):
        with cls._lock:
            cls._health_cache[provider_id] = health

    @classmethod
    def healthy_providers(cls) -> list[AIProvider]:
        return [
            p for pid, p in cls._providers.items()
            if cls._health_cache.get(pid, ProviderHealth()).healthy
        ]

    @classmethod
    def summarize(cls) -> dict[str, Any]:
        return {
            "total": len(cls._providers),
            "healthy": len(cls.healthy_providers()),
            "providers": [
                {
                    "id": pid,
                    "models": [m.id for m in p.models],
                    "healthy": cls._health_cache.get(pid, ProviderHealth()).healthy,
                }
                for pid, p in cls._providers.items()
            ],
        }
