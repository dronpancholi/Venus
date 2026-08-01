# M141 — AI Orchestration Engine

## File
`genesis/ai/engine.py`

## Purpose
Makes AI a first-class kernel subsystem. Auto-discovers and registers AI providers on boot, wires `routing_decision()` into production, fixes `summarize()` to include "available" key.

## Key Components

### AIOrchestrationEngine
- `boot()` — auto-discovers providers from `genesis.ai.providers` via `pkgutil`
- `chat()`, `stream_chat()`, `embeddings()`, `tool_call()` — delegates to AIRouter
- `routing_decision()` — returns best provider with fallback chain
- `list_providers()` — detailed provider info (models, health, capabilities, latency)
- `summarize()` — includes `available` key
- `health()` — overall AI subsystem health

### Auto-Discovery
Scans `genesis.ai.providers` for classes extending `AIProvider`. Registers 3 providers:
- `nvidia_nim` — Nvidia NIM (1 model)
- `ollama` — Ollama (1 model)
- `openai_compat` — OpenAI-compatible (2 models)

Each provider is registered as an EngineeringObject with type `AI_PROVIDER`.

## Integration
- **FabricKernel.ai** — lazy-loaded property, auto-booted in `kernel.boot()`
- **EngineeringRegistry** — all providers registered as AI_PROVIDER objects
- **Events** — emits `ai.provider.registered` for each provider
- **AgentExecutionEngine** — uses `kernel.ai` instead of raw `ProviderRegistry`
- **AIOrchestrationCenter screen** — uses `kernel.ai` methods

## Critical Gaps Addressed
- ✅ AI providers now auto-register on boot
- ✅ `summarize()` includes `available` key
- ✅ `routing_decision()` called in production flow
- ✅ AI layer is a first-class kernel subsystem
