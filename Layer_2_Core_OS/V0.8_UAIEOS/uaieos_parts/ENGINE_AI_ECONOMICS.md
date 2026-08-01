# UAIEOS Engine Specification: AI Economics

This document specifies the token calculations, prefix cache management implementations, and budget controller middleware that drive the AI Economics Engine.

---

## 1. Engine Core Flow

The Economics Engine sits directly between the Client Orchestrator and the Model Providers, tracking consumption dynamically and rejecting invocations when budgets are exceeded.

```
       [Client Invocation request]
                    |
                    v
    +------------------------------+
    |   BudgetController Check     | -> (Rejects if current consumption >= limit)
    +------------------------------+
                    |
                    v
    +------------------------------+
    |  Prefix Cache Matcher Check  | -> (Queries cached prefix mappings)
    +------------------------------+
                    |
                    v
          [LLM Inference Run]
                    |
                    v
    +------------------------------+
    |   Cost Logger and Registry   | -> (Updates Token Bucket and saves stats)
    +------------------------------+
```

---

## 2. Budget Controller & Token Bucket Middleware (Python)

This module implements the rate-limiting and budget enforcement algorithms specified in [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md#L30-L55).

```python
import time
from typing import Dict, Optional

class BudgetExceededException(Exception):
    pass

class TokenBucketRateLimiter:
    def __init__(self, capacity: float, replenish_rate: float):
        self.capacity: float = capacity
        self.replenish_rate: float = replenish_rate
        self.tokens: float = capacity
        self.last_update: float = time.monotonic()

    def _replenish(self) -> None:
        now = time.monotonic()
        delta = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + (delta * self.replenish_rate))
        self.last_update = now

    def consume(self, count: int) -> bool:
        """Determines if the bucket contains enough tokens. Consumes them if true."""
        self._replenish()
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False

class TenantBudgetController:
    def __init__(self, usd_limit: float):
        self.usd_limit: float = usd_limit
        self.usd_spent: float = 0.0
        self.limiters: Dict[str, TokenBucketRateLimiter] = {}

    def register_agent_limiter(self, agent_id: str, capacity: float, replenish_rate: float) -> None:
        self.limiters[agent_id] = TokenBucketRateLimiter(capacity, replenish_rate)

    def authorize_transaction(self, agent_id: str, estimated_tokens: int) -> None:
        if self.usd_spent >= self.usd_limit:
            raise BudgetExceededException("Overall financial budget limit breached.")
            
        limiter = self.limiters.get(agent_id)
        if limiter and not limiter.consume(estimated_tokens):
            raise BudgetExceededException(f"Agent '{agent_id}' rate limit capacity exceeded.")

    def record_cost(self, actual_cost_usd: float) -> None:
        self.usd_spent += actual_cost_usd
```

---

## 3. Dynamic Prefix Cache Manager

To prevent token waste, the Cache Manager calculates prompt hashes to verify prefix reuse.

```python
import hashlib
from typing import Dict, Tuple

class PrefixCacheManager:
    def __init__(self, token_block_size: int = 2048):
        self.token_block_size = token_block_size
        self.cache_registry: Dict[str, float] = {} # maps hash to last accessed time

    def _hash_prefix(self, prefix_text: str) -> str:
        return hashlib.sha256(prefix_text.encode("utf-8")).hexdigest()

    def evaluate_caching(self, prompt: str, system_len: int) -> Tuple[int, int]:
        """Calculates cache hit allocation.
        
        Returns a tuple: (cached_token_count, uncached_token_count)
        """
        # Determine number of blocks aligned to block size
        blocks = system_len // self.token_block_size
        if blocks == 0:
            return 0, len(prompt)
            
        aligned_length = blocks * self.token_block_size
        static_prefix = prompt[:aligned_length]
        prefix_hash = self._hash_prefix(static_prefix)
        
        if prefix_hash in self.cache_registry:
            # Hit: update access metadata
            self.cache_registry[prefix_hash] = time.time()
            return aligned_length, len(prompt) - aligned_length
            
        # Miss: register prefix structure
        self.cache_registry[prefix_hash] = time.time()
        return 0, len(prompt)
```

---

## 4. System Cross-References
*   For the token pricing formulas and financial rules, see [PART_13_AI_ECONOMICS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_13_AI_ECONOMICS.md).
*   For metrics exporters that collect token execution metrics, see [ENGINE_OBSERVABILITY_TELEMETRY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_OBSERVABILITY_TELEMETRY.md).
*   For how the state machine tracks iteration costs, see [ENGINE_WORKFLOW_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_WORKFLOW_ORCHESTRATION.md).
