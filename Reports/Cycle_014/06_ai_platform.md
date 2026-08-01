# Phase 0 Delta: AI Platform

**Files:** `genesis/ai/` — 5 files, 994 lines  
**Tests:** Via `test_kernel.py` (AI router tests)

## Architecture

```
AIRouter
  └── ProviderRegistry (class-level singleton)
        ├── NvidiaNIMProvider    — localhost:8000, 131K ctx, llama-3.1-nemotron
        ├── OllamaProvider       — localhost:11434, 8K ctx, llama3
        └── OpenAICompatibleProvider — api.openai.com, 128K ctx, gpt-4o
```

## Provider Interface (ABC)

| Method | Purpose |
|--------|---------|
| `chat()` | Synchronous chat completion |
| `stream_chat()` | Streaming (yields Chunk) |
| `embeddings()` | Text-to-vector |
| `tool_call()` | Function calling |
| `check_capabilities()` | Report capability set |
| `health()` | Health check |

**Capability enum:** CHAT, REASONING, STREAMING, EMBEDDINGS, TOOL_CALLING, STRUCTURED_OUTPUT, VISION, CODE_GENERATION, LONG_CONTEXT

## Routing Algorithm

`AIRouter._rank_providers(capability)`:
1. Get healthy providers from registry
2. Filter by required capability
3. Score: `success_rate * 50 + (1 - latency_p50/5000) * 30 + capability_bonuses`
4. Return sorted by score descending

**Fallback:** If no provider matches → `ProviderNotFoundError`

## Findings

1. **No provider caching** — `health()` is called on every `_rank_providers()` invocation
2. **Ollama `tool_call()` silently degrades** — falls back to plain `chat()`, caller gets no warning
3. **HTTP transport uses `urllib.request`** — no timeout configuration, no connection pooling, no retry
4. **No streaming in desktop** — screens use `chat()` not `stream_chat()`, all responses are synchronous
5. **No provider configuration UI** — base URLs and models are hardcoded at construction
6. **Benchmark data is never persisted** — `ProviderRegistry._benchmarks` is in-memory only, lost on restart

## Recommendations

1. Add TTL-based health caching (5s TTL) to avoid per-request health checks
2. Add `tool_call` capability check in `_rank_providers` so clients can detect degradation
3. Replace `urllib.request` with `httpx` for timeout/retry/pooling support
4. Create `ProviderSettingsScreen` for configuring base URLs and default models at runtime
5. Persist benchmark data to `StorageEngine` or JSON file
