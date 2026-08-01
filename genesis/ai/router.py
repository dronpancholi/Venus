from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Iterator

from genesis.ai import (
    AIProvider, ChatResponse, Chunk, EmbeddingResponse, Message, ModelSpec,
    ProviderCapabilities, ProviderHealth, ProviderCapability, ToolSpec,
)
from genesis.ai.registry import ProviderRegistry


@dataclass
class RoutingDecision:
    provider_id: str
    model: str
    confidence: float
    reason: str
    fallback_chain: list[str] = field(default_factory=list)


@dataclass
class ConsensusResult:
    text: str
    confidence: float
    providers_used: list[str]
    agreement: float
    responses: list[dict[str, Any]]


@dataclass
class DebateResult:
    topic: str
    arguments: list[dict[str, Any]]
    consensus: str
    agreement_level: float
    participants: list[str]
    rounds: int


@dataclass
class CritiqueResult:
    original: str
    critiques: list[dict[str, Any]]
    improved: str
    reviewer: str


@dataclass
class EvaluationResult:
    score: float
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    evaluator: str


class AIRouter:
    def __init__(self, registry: type[ProviderRegistry] = ProviderRegistry):
        self._registry = registry

    def chat(
        self,
        messages: list[Message],
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> ChatResponse:
        prov, model_id = self._resolve(provider, model, "chat")
        return prov.chat(messages, model=model_id, **kwargs)

    def stream_chat(
        self,
        messages: list[Message],
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> Iterator[Chunk]:
        prov, model_id = self._resolve(provider, model, "streaming")
        yield from prov.stream_chat(messages, model=model_id, **kwargs)

    def embeddings(
        self,
        texts: list[str],
        provider: str | None = None,
        model: str | None = None,
    ) -> EmbeddingResponse:
        prov, model_id = self._resolve(provider, model, "embeddings")
        return prov.embeddings(texts, model=model_id)

    def tool_call(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> ChatResponse:
        prov, model_id = self._resolve(provider, model, "tool_calling")
        return prov.tool_call(messages, tools, model=model_id, **kwargs)

    def parallel_chat(
        self,
        messages: list[Message],
        providers: list[str] | None = None,
        model: str | None = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> list[tuple[str, ChatResponse | None, str | None]]:
        candidates = providers or [p.provider_id for p in self._registry.healthy_providers()]
        results: list[tuple[str, ChatResponse | None, str | None]] = []

        def _query(p_id: str) -> tuple[str, ChatResponse | None, str | None]:
            try:
                prov = self._registry.get(p_id)
                if not prov:
                    return p_id, None, "Provider not found"
                model_id = model or prov.get_default_model()
                resp = prov.chat(messages, model=model_id, **kwargs)
                return p_id, resp, None
            except Exception as e:
                return p_id, None, str(e)

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidates)) as executor:
            futures = {executor.submit(_query, p_id): p_id for p_id in candidates}
            for future in concurrent.futures.as_completed(futures, timeout=timeout):
                results.append(future.result())

        return results

    def consensus_chat(
        self,
        messages: list[Message],
        min_providers: int = 2,
        model: str | None = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> ConsensusResult:
        candidates = [p.provider_id for p in self._registry.healthy_providers()]
        if len(candidates) < min_providers:
            return ConsensusResult(
                text="", confidence=0.0, providers_used=list(candidates),
                agreement=0.0, responses=[],
            )

        results = self.parallel_chat(messages, providers=candidates, model=model, timeout=timeout, **kwargs)
        successful = [(pid, resp) for pid, resp, err in results if resp is not None]

        if not successful:
            return ConsensusResult(
                text="", confidence=0.0, providers_used=list(candidates),
                agreement=0.0, responses=[],
            )

        texts = [resp.content for _, resp in successful]
        response_map: dict[str, list[str]] = {}
        for t in texts:
            key = t[:100]
            if key not in response_map:
                response_map[key] = []
            response_map[key].append(t)

        best_key = max(response_map, key=lambda k: len(response_map[k]))
        agreed_texts = response_map[best_key]
        agreement = len(agreed_texts) / len(texts) if texts else 0

        return ConsensusResult(
            text=agreed_texts[0] if agreed_texts else "",
            confidence=agreement,
            providers_used=[pid for pid, _ in successful],
            agreement=agreement,
            responses=[{"provider": pid, "text": resp.content[:200]} for pid, resp in successful],
        )

    def best_of_n(
        self,
        messages: list[Message],
        n: int = 3,
        model: str | None = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> ChatResponse:
        candidates = [p.provider_id for p in self._registry.healthy_providers()][:n]
        if not candidates:
            raise RuntimeError("No healthy providers available")

        results = self.parallel_chat(messages, providers=candidates, model=model, timeout=timeout, **kwargs)
        successful = [(pid, resp) for pid, resp, err in results if resp is not None]

        if not successful:
            prov = self._registry.get(candidates[0])
            model_id = model or prov.get_default_model()
            return prov.chat(messages, model=model_id, **kwargs)

        ranked = sorted(successful, key=lambda x: (
            len(x[1].content) if x[1].content else 0), reverse=True)

        return ranked[0][1]

    def debate_chat(
        self,
        topic: str,
        perspectives: list[str],
        providers: list[str] | None = None,
        model: str | None = None,
        rounds: int = 2,
        timeout: float = 60.0,
        **kwargs,
    ) -> DebateResult:
        candidates = providers or [p.provider_id for p in self._registry.healthy_providers()]
        arguments: list[dict[str, Any]] = []
        participant_map: dict[str, str] = {}

        for i, perspective in enumerate(perspectives[:len(candidates)]):
            pid = candidates[i % len(candidates)]
            debate_msg = [Message(role="system", content=f"Argue from this perspective: {perspective}")]
            debate_msg.append(Message(role="user", content=topic))
            try:
                prov = self._registry.get(pid)
                if not prov:
                    continue
                resp = prov.chat(debate_msg, model=model or prov.get_default_model(), **kwargs)
                arguments.append({
                    "perspective": perspective,
                    "provider": pid,
                    "argument": resp.content if resp else "",
                    "round": 1,
                })
                participant_map[pid] = perspective
            except Exception:
                continue

        for r in range(2, rounds + 1):
            new_args: list[dict[str, Any]] = []
            for arg in arguments:
                if arg["round"] != r - 1:
                    continue
                counter_msg = [
                    Message(role="system", content=f"You are debating. Respond to this argument: {arg['argument']}"),
                    Message(role="user", content=topic),
                ]
                for pid, perspective in participant_map.items():
                    if pid == arg.get("provider_override", ""):
                        continue
                    try:
                        prov = self._registry.get(pid)
                        if prov:
                            resp = prov.chat(counter_msg, model=model or prov.get_default_model(), **kwargs)
                            new_args.append({
                                "perspective": perspective,
                                "provider": pid,
                                "argument": resp.content if resp else "",
                                "round": r,
                                "responding_to": arg["perspective"],
                            })
                    except Exception:
                        continue
            arguments.extend(new_args)

        consensus_text = "Synthesis of debate perspectives: " + " | ".join(
            a["argument"][:200] for a in arguments if a["round"] == rounds
        )
        return DebateResult(
            topic=topic,
            arguments=arguments,
            consensus=consensus_text,
            agreement_level=0.5,
            participants=list(participant_map.keys()),
            rounds=rounds,
        )

    def critique_chat(
        self,
        content: str,
        criteria: list[str] | None = None,
        reviewer_provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> CritiqueResult:
        reviewer = reviewer_provider or self.best_provider("chat").provider_id
        prov = self._registry.get(reviewer)
        if not prov:
            raise ValueError(f"Reviewer provider not found: {reviewer}")

        criteria_str = "\n".join(f"- {c}" for c in (criteria or ["clarity", "correctness", "completeness"]))
        critique_msg = [
            Message(role="system", content=f"Critique the following content based on:\n{criteria_str}\nProvide specific, actionable feedback."),
            Message(role="user", content=content),
        ]
        critique_resp = prov.chat(critique_msg, model=model or prov.get_default_model(), **kwargs)
        critique_text = critique_resp.content if critique_resp else ""

        improve_msg = [
            Message(role="system", content=f"Improve this content based on this critique:\n{critique_text}\nReturn only the improved version."),
            Message(role="user", content=content),
        ]
        improved_resp = prov.chat(improve_msg, model=model or prov.get_default_model(), **kwargs)
        improved_text = improved_resp.content if improved_resp else content

        return CritiqueResult(
            original=content,
            critiques=[{"reviewer": reviewer, "text": critique_text}],
            improved=improved_text,
            reviewer=reviewer,
        )

    def evaluate_chat(
        self,
        content: str,
        rubric: dict[str, float] | None = None,
        evaluator_provider: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> EvaluationResult:
        evaluator = evaluator_provider or self.best_provider("chat").provider_id
        prov = self._registry.get(evaluator)
        if not prov:
            raise ValueError(f"Evaluator provider not found: {evaluator}")

        rubric = rubric or {"correctness": 0.4, "completeness": 0.3, "clarity": 0.3}
        rubric_str = "\n".join(f"- {k}: {v*100:.0f}% weight" for k, v in rubric.items())

        eval_msg = [
            Message(role="system", content=(
                f"Evaluate the following content based on this rubric:\n{rubric_str}\n"
                "Return a JSON with: overall_score (0-1), strengths (list), weaknesses (list), recommendations (list)"
            )),
            Message(role="user", content=content),
        ]
        resp = prov.chat(eval_msg, model=model or prov.get_default_model(), **kwargs)
        resp_text = resp.content if resp else "{}"

        import json as _json
        try:
            result = _json.loads(resp_text)
        except Exception:
            result = {"overall_score": 0.5, "strengths": [], "weaknesses": [], "recommendations": []}

        return EvaluationResult(
            score=result.get("overall_score", 0.5),
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            recommendations=result.get("recommendations", []),
            evaluator=evaluator,
        )

    def _resolve(self, provider: str | None, model: str | None, required_capability: str) -> tuple[AIProvider, str]:
        if provider:
            prov = self._registry.get(provider)
            if not prov:
                raise ValueError(f"Provider not found: {provider}")
            model_id = model or prov.get_default_model()
            return prov, model_id

        candidates = self._rank_providers(required_capability)
        if not candidates:
            raise RuntimeError(f"No healthy providers available for {required_capability}")

        prov = candidates[0]
        model_id = model or prov.get_default_model()
        return prov, model_id

    def best_provider(self, capability: str = "chat") -> AIProvider:
        candidates = self._rank_providers(capability)
        if not candidates:
            raise RuntimeError(f"No healthy providers available for {capability}")
        return candidates[0]

    def _rank_providers(self, required_capability: str) -> list[AIProvider]:
        cap_map = {
            "chat": ProviderCapability.CHAT,
            "streaming": ProviderCapability.STREAMING,
            "embeddings": ProviderCapability.EMBEDDINGS,
            "tool_calling": ProviderCapability.TOOL_CALLING,
            "vision": ProviderCapability.VISION,
            "reasoning": ProviderCapability.REASONING,
            "code_generation": ProviderCapability.CODE_GENERATION,
        }
        required = cap_map.get(required_capability, ProviderCapability.CHAT)

        scored: list[tuple[float, AIProvider]] = []
        for prov in self._registry.healthy_providers():
            caps = self._registry.get_capabilities(prov.provider_id)
            if caps and required not in caps.capabilities:
                continue
            benchmark = self._registry.get_benchmark(prov.provider_id)
            score = 0.0
            if benchmark:
                score += benchmark.success_rate * 50
                score += max(0, 1.0 - benchmark.latency_p50 / 5000.0) * 30
            else:
                score += 50.0
            if caps and ProviderCapability.CODE_GENERATION in caps.capabilities:
                score += 10.0
            scored.append((score, prov))

        scored.sort(key=lambda x: -x[0])
        return [p for _, p in scored]

    def routing_decision(self, capability: str = "chat") -> RoutingDecision:
        try:
            prov = self.best_provider(capability)
            bench = self._registry.get_benchmark(prov.provider_id)
            confidence = bench.success_rate if bench else 0.8
            fallback = [p.provider_id for p in self._registry.healthy_providers() if p.provider_id != prov.provider_id]
            return RoutingDecision(
                provider_id=prov.provider_id,
                model=prov.get_default_model(),
                confidence=confidence,
                reason=f"Highest-ranked provider for {capability}",
                fallback_chain=fallback,
            )
        except RuntimeError as e:
            return RoutingDecision(
                provider_id="",
                model="",
                confidence=0.0,
                reason=str(e),
            )
