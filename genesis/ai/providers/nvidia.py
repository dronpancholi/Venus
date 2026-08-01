from __future__ import annotations

import json
import time
from typing import Any, Iterator

import urllib.request
import urllib.error

from genesis.ai import (
    AIProvider, ChatResponse, Chunk, EmbeddingResponse, Message,
    MessageRole, ModelSpec, ProviderCapabilities, ProviderCapability,
    ProviderHealth, ToolSpec,
)

NVIDIA_NIM_CLOUD_HOST = "https://integrate.api.nvidia.com"
NVIDIA_NIM_LOCAL_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct"

NVIDIA_CLOUD_MODELS = [
    ModelSpec(id="nvidia/llama-3.1-nemotron-70b-instruct", name="Nemotron 70B Instruct",
              context_window=131072, supports_streaming=True, supports_tools=True, is_default=True),
    ModelSpec(id="meta/llama-3.1-405b-instruct", name="Llama 3.1 405B Instruct",
              context_window=131072, supports_streaming=True, supports_tools=True),
    ModelSpec(id="meta/llama-3.1-70b-instruct", name="Llama 3.1 70B Instruct",
              context_window=131072, supports_streaming=True, supports_tools=True),
    ModelSpec(id="meta/llama-3.1-8b-instruct", name="Llama 3.1 8B Instruct",
              context_window=131072, supports_streaming=True, supports_tools=True),
    ModelSpec(id="mistralai/mistral-nemo-12b-instruct", name="Mistral Nemo 12B",
              context_window=131072, supports_streaming=True, supports_tools=True),
    ModelSpec(id="mistralai/mistral-7b-instruct-v0.3", name="Mistral 7B v0.3",
              context_window=32768, supports_streaming=True, supports_tools=True),
    ModelSpec(id="google/gemma-2-27b-it", name="Gemma 2 27B IT",
              context_window=8192, supports_streaming=True),
    ModelSpec(id="google/gemma-2-9b-it", name="Gemma 2 9B IT",
              context_window=8192, supports_streaming=True),
    ModelSpec(id="microsoft/phi-3-medium-4k-instruct", name="Phi-3 Medium 4K",
              context_window=4096, supports_streaming=True),
    ModelSpec(id="qwen/qwen2-72b-instruct", name="Qwen2 72B Instruct",
              context_window=32768, supports_streaming=True),
    ModelSpec(id="upstage/solar-10.7b-instruct", name="Solar 10.7B Instruct",
              context_window=4096, supports_streaming=True),
    ModelSpec(id="ibm/granite-13b-chat-v2", name="Granite 13B Chat v2",
              context_window=8192, supports_streaming=True),
]


def _is_cloud_nim(api_key: str, base_url: str) -> bool:
    """Detect if we should use the NVIDIA cloud API based on key prefix."""
    if api_key.startswith("nvapi-"):
        return True
    if api_key.startswith("nvkey-"):
        return True
    return "nvcf.nvidia.com" in base_url or "integrate.api.nvidia.com" in base_url


def _fetch_nim_models(api_key: str) -> list[ModelSpec]:
    """Try to fetch available models from the NVIDIA catalog API."""
    try:
        req = urllib.request.Request(
            "https://api.nvcf.nvidia.com/v2/nvcf/assets?functionDeployments=true",
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        models = []
        for asset in data.get("assets", []):
            if asset.get("status") == "active" and asset.get("deploymentMethod") == "NIM":
                model_id = asset.get("name", "")
                if model_id:
                    models.append(ModelSpec(
                        id=model_id,
                        name=asset.get("displayName", model_id),
                        context_window=asset.get("contextLength", 4096),
                        supports_streaming=True,
                        supports_tools="tool" in str(asset.get("capabilities", [])).lower(),
                    ))
        if models:
            models[0].is_default = True
            return models
    except Exception:
        pass
    return []


class NvidiaNIMProvider(AIProvider):
    provider_id = "nvidia_nim"

    def __init__(self, base_url: str = "", api_key: str = ""):
        self.api_key = api_key
        self._is_cloud = _is_cloud_nim(api_key, base_url)
        if self._is_cloud:
            self.base_url = (base_url.rstrip("/") if base_url
                             else NVIDIA_NIM_CLOUD_HOST)
        else:
            self.base_url = (base_url.rstrip("/") if base_url
                             else "http://localhost:8000")
        if self._is_cloud:
            fetched = _fetch_nim_models(self.api_key) if self.api_key else []
            self.models = fetched if fetched else list(NVIDIA_CLOUD_MODELS)
        else:
            self.models = [
                ModelSpec(
                    id=NVIDIA_NIM_LOCAL_MODEL,
                    name="Nemotron 70B Instruct",
                    context_window=131072,
                    supports_streaming=True,
                    supports_tools=True,
                    supports_vision=False,
                    is_default=True,
                ),
            ]

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _chat_url(self) -> str:
        return f"{self.base_url}/v1/chat/completions"

    def _embeddings_url(self) -> str:
        return f"{self.base_url}/v1/embeddings"

    def chat(self, messages: list[Message], model: str | None = None, **kwargs) -> ChatResponse:
        start = time.time()
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "temperature": kwargs.get("temperature", 0.3),
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
            raise RuntimeError(f"NVIDIA NIM error {e.code}: {e.read().decode()}") from e
        except Exception as e:
            raise RuntimeError(f"NVIDIA NIM request failed: {e}") from e

    def stream_chat(self, messages: list[Message], model: str | None = None, **kwargs) -> Iterator[Chunk]:
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "temperature": kwargs.get("temperature", 0.3),
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
            raise RuntimeError(f"NVIDIA NIM stream failed: {e}") from e

    def embeddings(self, texts: list[str], model: str | None = None) -> EmbeddingResponse:
        start = time.time()
        body = {
            "model": model or self.get_default_model(),
            "input": texts,
        }
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
            raise RuntimeError(f"NVIDIA NIM embeddings failed: {e}") from e

    def tool_call(self, messages: list[Message], tools: list[ToolSpec], model: str | None = None, **kwargs) -> ChatResponse:
        body = {
            "model": model or self.get_default_model(),
            "messages": [_message_to_dict(m) for m in messages],
            "tools": [t.to_openai_format() for t in tools],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": False,
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
            raise RuntimeError(f"NVIDIA NIM tool call error {e.code}: {e.read().decode()}") from e
        except Exception as e:
            raise RuntimeError(f"NVIDIA NIM tool call failed: {e}") from e

    def check_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            capabilities={
                ProviderCapability.CHAT,
                ProviderCapability.STREAMING,
                ProviderCapability.TOOL_CALLING,
                ProviderCapability.CODE_GENERATION,
                ProviderCapability.LONG_CONTEXT,
            },
            max_context_window=131072,
        )

    def health(self) -> ProviderHealth:
        start = time.time()
        try:
            if self._is_cloud:
                req = urllib.request.Request(
                    f"{self.base_url}/v1/models",
                    headers=self._headers(),
                    method="GET",
                )
            else:
                req = urllib.request.Request(f"{self.base_url}/v1/health", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
            latency = (time.time() - start) * 1000
            return ProviderHealth(
                healthy=status == 200,
                latency_ms=latency,
                last_check=time.time(),
            )
        except Exception as e:
            return ProviderHealth(
                healthy=False,
                message=str(e),
                last_check=time.time(),
            )


def _message_to_dict(m: Message) -> dict[str, Any]:
    d: dict[str, Any] = {"role": m.role.value, "content": m.content}
    if m.tool_calls:
        d["tool_calls"] = m.tool_calls
    if m.tool_call_id:
        d["tool_call_id"] = m.tool_call_id
    if m.name:
        d["name"] = m.name
    return d
