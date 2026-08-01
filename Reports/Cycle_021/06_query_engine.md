# Universal Query Engine (M179)

**File:** `genesis/query/__init__.py`
**Tests:** 9

One query layer across all subsystems: events, engineering, knowledge, audit, timeline, providers, agents.

### API
```python
from genesis.query import QueryEngine, Query, QueryResult

qe = QueryEngine()
qe.register_fabric_kernel(kernel)

# Simple search
results = qe.search("AI providers")

# Advanced query
q = Query(text="architecture decision", sources=["events", "knowledge"],
          limit=10, min_relevance=0.5)
results = qe.query(q)

# Custom handler
def custom_handler(q: Query) -> list[QueryResult]:
    return [QueryResult(source="custom", type="item", 
            label=f"Found: {q.text}", relevance=0.8)]

qe.register("custom", custom_handler)
```
