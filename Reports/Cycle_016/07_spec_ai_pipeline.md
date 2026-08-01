# Cycle 016 — AI Pipeline Design (M117)

## Current State
3 AI providers (NVIDIA, Ollama, OpenAI-compat) behind an `AIRouter` with naive ranking (magic-number formula). No pipeline stages — user request goes directly to model. No verification, no critic, no reflection.

## Target: 14-Stage Pipeline
```
User Request → Planner → Retriever → Memory → Context Builder
→ Model Router → Primary Model → Verifier → Critic
→ Reflector → Knowledge Writer → Report Writer
→ Artifact Generator → Timeline Update → User
```

## Stage Specifications

| Stage | Input | Output | Observable |
|-------|-------|--------|------------|
| Planner | User request | Decomposed plan | Plan steps shown in UI |
| Retriever | Plan | Relevant context | Retrieved documents shown |
| Memory | Context | Enriched context | Memory entries displayed |
| Context Builder | Enriched context | Prompt + system message | Full prompt shown |
| Model Router | Prompt | Model assignment | Routing decision shown |
| Primary Model | Prompt | Raw response | Streaming visible |
| Verifier | Response | Verified/Rejected | Verification result |
| Critic | Verified response | Critique + suggestions | Critique text shown |
| Reflector | Critique | Improved response | Diff shown |
| Knowledge Writer | Final response | Memory update | Knowledge graph updated |
| Report Writer | Response | Formatted report | Report preview |
| Artifact Generator | Response | Generated files | Artifact tree shown |
| Timeline Update | All stages | Event chain | Events in inspector |

## API
```python
class AIPipeline:
    async def run(self, request: PipelineRequest) -> PipelineResult:
        # Each stage is a replaceable step
        plan = await self.planner.plan(request)
        context = await self.retriever.retrieve(plan)
        context = await self.memory.enrich(context)
        prompt = await self.context_builder.build(context)
        model = await self.model_router.route(prompt)
        response = await model.generate(prompt)
        verified = await self.verifier.verify(response)
        ...
```

## Deferred to Cycle 017
Pipeline architecture designed but not implemented. Requires multi-agent system (M115) as prerequisite.
