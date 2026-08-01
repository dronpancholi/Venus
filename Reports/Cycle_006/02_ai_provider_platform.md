# Cycle 006 — AI Provider Platform

## Why a Provider Abstraction?

Every capability in Genesis depends on an AI model — analyzing code, generating patches,
running simulations, answering engineering questions, planning migrations, reviewing
governance compliance. Hardcoding a single provider creates:

- **Vendor lock-in** — changing providers requires code changes
- **No fallback** — a single provider outage stops all AI-dependent workflows
- **No benchmarking** — cannot compare providers objectively
- **No cost optimization** — cannot route cheap/simple queries to different models
- **Capability fragmentation** — each agent implements its own provider logic

## Design

The AI Provider Platform is a thin abstraction layer between the kernel and AI models.

```
┌─────────────────────────────────────────────────────┐
│                   Genesis Kernel                     │
│  Agents  │  Analyzer  │  Simulator  │  Governance    │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│              AI Provider Platform                    │
│  ProviderRegistry  │  Router  │  CapabilityChecker   │
│  Benchmarker       │  CostTracker  │  FallbackChain   │
└──────┬──────┬──────┬──────┬──────┬──────┬───────────┘
       │      │      │      │      │      │
  NVIDIA  Claude  OpenAI  Gemini  DeepSeek  Ollama ...
   NIM
```

## Provider Interface

Every provider implements:

```python
class AIProvider(ABC):
    provider_id: str
    models: list[ModelSpec]

    @abstractmethod
    def chat(self, messages: list[Message], model: str = None, **kwargs) -> ChatResponse: ...
    @abstractmethod
    def stream_chat(self, messages: list[Message], model: str = None, **kwargs) -> Iterator[Chunk]: ...
    @abstractmethod
    def embeddings(self, texts: list[str], model: str = None) -> list[list[float]]: ...
    @abstractmethod
    def tool_call(self, messages: list[Message], tools: list[Tool], model: str = None, **kwargs) -> ToolResponse: ...
    @abstractmethod
    def check_capabilities(self) -> ProviderCapabilities: ...
    @abstractmethod
    def health(self) -> ProviderHealth: ...
```

## Provider Registry

- Auto-discovery of installed provider packages (`genesis-provider-*`)
- Runtime registration via `ProviderRegistry.register(provider)`
- Default providers built-in: NVIDIA NIM, OpenAI-compatible, Ollama

## Smart Router

The router selects the optimal provider per request based on:

- **Capability match** — does the provider support the required capability (tool calling, vision, etc.)?
- **Cost** — cheapest adequate model for the task
- **Latency** — fastest adequate model for the task
- **Health** — only healthy providers
- **Rate limits** — avoid providers at capacity
- **Fallback chain** — if primary fails, try next

## Default Provider: NVIDIA NIM

NVIDIA NIM is the default because:
- Self-hosted on NVIDIA hardware
- No API key required for local deployment
- High throughput on enterprise hardware
- Strong code generation capabilities

## Capability Discovery

Each provider declares its capabilities:

```python
@dataclass
class ProviderCapabilities:
    chat: bool
    reasoning: bool
    streaming: bool
    embeddings: bool
    tool_calling: bool
    structured_output: bool
    vision: bool
    code_generation: bool
    long_context: int  # max context window
```

The platform benchmarks providers on startup and periodically:
- Latency (p50, p95, p99)
- Throughput (tokens/second)
- Cost per token
- Success rate
- Rate limit behavior

## Implementation Plan

1. `genesis/ai/__init__.py` — Provider base classes, types
2. `genesis/ai/registry.py` — ProviderRegistry
3. `genesis/ai/router.py` — Smart routing with fallback
4. `genesis/ai/providers/nvidia.py` — NVIDIA NIM provider
5. `genesis/ai/providers/openai_compat.py` — OpenAI API-compatible
6. `genesis/ai/providers/ollama.py` — Ollama provider
7. `genesis/tests/test_ai_platform.py` — 50+ tests

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Provider discovery | Entry point + registry | Standard Python pattern, no config file needed |
| Routing strategy | Capability-first, then cost | Ensures task requirements met before optimization |
| Default provider | NVIDIA NIM | Self-hosted, no API dependency |
| Streaming model | Iterator[Chunk] | Consistent across providers, easy to wrap |
| Error handling | Circuit breaker per provider | Prevents cascading failures |
| Benchmarking | Background periodic | Always has fresh data for routing |
