from __future__ import annotations

import json
import time
from typing import Any, Iterator

import urllib.request
import urllib.error

from genesis.ai import (
    AIProvider, ChatResponse, Chunk, EmbeddingResponse, Message,
    ModelSpec, ProviderCapabilities, ProviderCapability, ProviderHealth, ToolSpec,
)
from genesis.ai.providers.nvidia import _message_to_dict

LM_STUDIO_DEFAULT_URL = "http://localhost:1234/v1"


def _fetch_lm_studio_models(base_url: str) -> list[ModelSpec]:
    """Fetch available models from the LM Studio API (GET /v1/models)."""
    try:
        req = urllib.request.Request(f"{base_url}/models", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        models = []
        for entry in data.get("data", []):
            mid = entry.get("id", "")
            if mid:
                models.append(ModelSpec(
                    id=mid,
                    name=entry.get("id", mid),
                    context_window=entry.get("max_context_length", 4096),
                    supports_streaming=True,
                    supports_tools=True,
                ))
        if models:
            models[0].is_default = True
        return models
    except Exception:
        return []


class LMStudioProvider(AIProvider):
    provider_id = "lm_studio"

    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = (base_url.rstrip("/") if base_url else LM_STUDIO_DEFAULT_URL)
        self.api_key = api_key
        fetched = _fetch_lm_studio_models(self.base_url)
        if fetched:
            self.models = fetched
        else:
            self.models = [
                ModelSpec(id="local-model", name="LM Studio Default",
                          context_window=4096, supports_streaming=True,
                          supports_tools=True, is_default=True),
            ]

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _chat_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def _embeddings_url(self) -> str:
        return f"{self.base_url}/embeddings"

    def chat(self, messages: list[Message], model: str | None = None, **kwargs) -> ChatResponse:
        start = time.time()
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": False,
        }
        try:
            req = urllib.request.Request(
                self._chat_url(),
                data=json.dumps(body).encode(),
                headers=self._headers(),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                data = json.loads(resp.read())
            choice = data["choices"][0]
            latency = (time.time() - start) * 1000
            return ChatResponse(
                content=choice["message"]["content"],
                model=data.get("model", model or self.get_default_model()),
                provider=self.provider_id,
                usage=data.get("usage"),
                latency_ms=latency,
                tool_calls=choice["message"].get("tool_calls"),
            )
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"LM Studio error {e.code}: {e.read().decode()}") from e
        except Exception as e:
            raise RuntimeError(f"LM Studio request failed: {e}") from e

    def stream_chat(self, messages: list[Message], model: str | None = None, **kwargs) -> Iterator[Chunk]:
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": True,
        }
        try:
            req = urllib.request.Request(
                self._chat_url(),
                data=json.dumps(body).encode(),
                headers=self._headers(),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                buffer = ""
                while True:
                    chunk = resp.read(1).decode()
                    if not chunk:
                        break
                    buffer += chunk
                    if buffer.endswith("\n"):
                        line = buffer.strip()
                        buffer = ""
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                yield Chunk(content="", done=True)
                                return
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield Chunk(content=content)
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            raise RuntimeError(f"LM Studio stream failed: {e}") from e

    def embeddings(self, texts: list[str], model: str | None = None) -> EmbeddingResponse:
        start = time.time()
        body = {"model": model or self.get_default_model(), "input": texts}
        try:
            req = urllib.request.Request(
                self._embeddings_url(),
                data=json.dumps(body).encode(),
                headers=self._headers(),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            vectors = [d["embedding"] for d in data["data"]]
            latency = (time.time() - start) * 1000
            return EmbeddingResponse(
                vectors=vectors,
                model=data.get("model", model or self.get_default_model()),
                provider=self.provider_id,
                latency_ms=latency,
                usage=data.get("usage"),
            )
        except Exception as e:
            raise RuntimeError(f"LM Studio embeddings failed: {e}") from e

    def tool_call(self, messages: list[Message], tools: list[ToolSpec], model: str | None = None, **kwargs) -> ChatResponse:
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "tools": [t.to_openai_format() for t in tools],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        start = time.time()
        try:
            req = urllib.request.Request(
                self._chat_url(),
                data=json.dumps(body).encode(),
                headers=self._headers(),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                data = json.loads(resp.read())
            choice = data["choices"][0]
            latency = (time.time() - start) * 1000
            return ChatResponse(
                content=choice["message"].get("content", ""),
                model=data.get("model", model or self.get_default_model()),
                provider=self.provider_id,
                usage=data.get("usage"),
                latency_ms=latency,
                tool_calls=choice["message"].get("tool_calls"),
            )
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"LM Studio tool call error {e.code}: {e.read().decode()}") from e
        except Exception as e:
            raise RuntimeError(f"LM Studio tool call failed: {e}") from e

    def check_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            capabilities={
                ProviderCapability.CHAT,
                ProviderCapability.STREAMING,
                ProviderCapability.TOOL_CALLING,
                ProviderCapability.CODE_GENERATION,
            },
            max_context_window=4096,
        )

    def health(self) -> ProviderHealth:
        start = time.time()
        try:
            req = urllib.request.Request(f"{self.base_url}/models", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            healthy = len(data.get("data", [])) > 0
            latency = (time.time() - start) * 1000
            return ProviderHealth(healthy=healthy, latency_ms=latency, last_check=time.time())
        except Exception as e:
            return ProviderHealth(healthy=False, message=str(e), last_check=time.time())
