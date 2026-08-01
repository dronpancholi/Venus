# M167: AI Collaboration Layer

**Status:** Implemented
**Files:** `genesis/ai/router.py`
**Integration:** AIRouter.debate_chat(), critique_chat(), evaluate_chat()

## Changes

AI orchestration now supports multi-model reasoning:

- **debate_chat(topic, perspectives, providers, rounds)** — multi-perspective debate across providers with rebuttal rounds
- **critique_chat(content, criteria, reviewer)** — critique → improve pipeline
- **evaluate_chat(content, rubric, evaluator)** — scored evaluation against rubric

## Collaboration Patterns

| Pattern | Description | Providers |
|---------|-------------|-----------|
| **parallel_chat** | All providers answer simultaneously | N providers |
| **consensus_chat** | Find agreement across providers | N providers |
| **best_of_n** | Return the best response | N providers |
| **debate_chat** | Multi-perspective debate with rounds | N providers |
| **critique_chat** | Critique → improve cycle | 1 reviewer |
| **evaluate_chat** | Scored evaluation against rubric | 1 evaluator |
| **routing_decision** | Select best provider for capability | N/A |

## Debate Flow

```
Topic: "Best architecture for microservices"
  Provider A (perspective: "event-driven") → Argument 1
  Provider B (perspective: "REST-first")   → Argument 2
  Round 2:
    A responds to B's argument → Rebuttal 1
    B responds to A's argument → Rebuttal 2
  Result: synthesized consensus
```
