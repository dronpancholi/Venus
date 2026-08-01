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


class OllamaProvider(AIProvider):
    provider_id = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self._models: list[ModelSpec] | None = None
        self.models = self._fetch_models()

    def _fetch_models(self) -> list[ModelSpec]:
        if self._models is not None:
            return self._models
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            models: list[ModelSpec] = []
            for m in data.get("models", []):
                name = m["name"]
                models.append(ModelSpec(
                    id=name, name=name, context_window=8192,
                    supports_streaming=True, supports_tools=False, supports_vision=False,
                    is_default=(name == self.default_model),
                ))
            if not models:
                models = [ModelSpec(id=self.default_model, name=self.default_model, is_default=True)]
            self._models = models
            return models
        except Exception:
            return [ModelSpec(id=self.default_model, name=self.default_model, is_default=True)]

    def _chat_url(self) -> str:
        return f"{self.base_url}/api/chat"

    def chat(self, messages: list[Message], model: str | None = None, **kwargs) -> ChatResponse:
        start = time.time()
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.3),
                "num_predict": kwargs.get("max_tokens", 4096),
            },
        }
        try:
            req = urllib.request.Request(
                self._chat_url(),
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                data = json.loads(resp.read())
            latency = (time.time() - start) * 1000
            return ChatResponse(
                content=data["message"]["content"],
                model=data.get("model", model or self.get_default_model()),
                provider=self.provider_id,
                latency_ms=latency,
            )
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Ollama error {e.code}: {e.read().decode()}") from e
        except Exception as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

    def stream_chat(self, messages: list[Message], model: str | None = None, **kwargs) -> Iterator[Chunk]:
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "stream": True,
        }
        try:
            req = urllib.request.Request(
                self._chat_url(),
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
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
                        try:
                            data = json.loads(buffer.strip())
                            if data.get("done"):
                                yield Chunk(content="", done=True)
                                return
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield Chunk(content=content)
                        except json.JSONDecodeError:
                            pass
                        buffer = ""
        except Exception as e:
            raise RuntimeError(f"Ollama stream failed: {e}") from e

    def embeddings(self, texts: list[str], model: str | None = None) -> EmbeddingResponse:
        start = time.time()
        try:
            vectors = []
            for text in texts:
                body = {"model": model or self.get_default_model(), "prompt": text}
                req = urllib.request.Request(
                    f"{self.base_url}/api/embeddings",
                    data=json.dumps(body).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read())
                vectors.append(data["embedding"])
            latency = (time.time() - start) * 1000
            return EmbeddingResponse(
                vectors=vectors,
                model=model or self.get_default_model(),
                provider=self.provider_id,
                latency_ms=latency,
            )
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Ollama embeddings error {e.code}: {e.read().decode()}") from e
        except Exception as e:
            raise RuntimeError(f"Ollama embeddings failed: {e}") from e

    def tool_call(self, messages: list[Message], tools: list[ToolSpec], model: str | None = None, **kwargs) -> ChatResponse:
        return self.chat(messages, model=model, **kwargs)

    def check_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            capabilities={ProviderCapability.CHAT, ProviderCapability.STREAMING, ProviderCapability.EMBEDDINGS},
            max_context_window=8192,
        )

    def health(self) -> ProviderHealth:
        start = time.time()
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            healthy = len(data.get("models", [])) > 0
            latency = (time.time() - start) * 1000
            return ProviderHealth(healthy=healthy, latency_ms=latency, last_check=time.time())
        except Exception as e:
            return ProviderHealth(healthy=False, message=str(e), last_check=time.time())
