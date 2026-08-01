# Cycle 015 — Execution Platform V2 (M104)

## Current State

`AgentExecutionEngine` + `TaskExecutor` (single daemon thread, 2s poll)

**Limitations:**
- Single-threaded bottleneck — one task at a time
- No task timeout — stuck task blocks forever
- No retry logic — failed tasks stay failed
- No cancellation — running tasks cannot be stopped
- No pause/resume — execution state is binary
- No execution history — results stored in memory only
- No metrics — no per-task duration tracking
- No circuit breakers — provider failures cascade

## Target Architecture

```
TaskExecutor V2
  ├── WorkerPool (ThreadPoolExecutor)
  │     ├── Worker 1 → task execution
  │     ├── Worker 2 → task execution
  │     └── Worker N → task execution
  ├── ExecutionQueue (PriorityQueue)
  │     ├── Priority ordering
  │     ├── Retry queue (with backoff)
  │     └── Dead-letter queue (after max retries)
  ├── ExecutionHistory (persistent)
  │     ├── Per-task result, duration, provider
  │     └── Queryable by agent, type, time range
  ├── CircuitBreaker
  │     ├── Per-provider failure tracking
  │     └── Automatic disable after threshold
  └── MetricsCollector
        ├── Tasks/sec, avg duration, failure rate
        └── Per-provider latency p50/p95/p99
```

## Key Features

| Feature | Current | Target |
|---------|---------|--------|
| Concurrency | 1 thread | N-worker thread pool (configurable) |
| Timeout | None | Per-task timeout (default 300s) |
| Retry | None | Configurable: max_retries, backoff (linear/exponential) |
| Cancellation | None | `cancel_task(task_id)` — signal worker |
| Pause/Resume | None | `pause()` / `resume()` — drain queue |
| History | RAM only | SQLite via StorageEngine |
| Prioritization | None | Priority queue (CRITICAL > HIGH > NORMAL > LOW) |
| Circuit Breaker | None | Per-provider: 5 failures → 30s cooldown |
| Provider failover | Explicit only | Auto-failover on timeout/circuit break |

## Queue States

```
PENDING → QUEUED → RUNNING → COMPLETED
                         ↓ → FAILED → QUEUED (retry)
                                      ↓ → DEAD_LETTER (max retries)
                         ↓ → CANCELLED
```

## Implementation Plan

1. Add `ThreadPoolExecutor` to `TaskExecutor` with configurable `max_workers`
2. Add `timeout_seconds` to `TaskNode` and enforce in execution
3. Add `max_retries` / `retry_backoff` to `TaskNode` with exponential backoff
4. Add `cancel()` / `pause()` / `resume()` lifecycle methods
5. Persist execution results to StorageEngine
6. Add per-provider circuit breaker to AgentExecutionEngine
7. Add auto-failover: on timeout/circuit → try next healthy provider
