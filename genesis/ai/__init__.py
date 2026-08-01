from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, AsyncIterator, Iterator


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    role: MessageRole
    content: str
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = False


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_openai_format(self) -> dict[str, Any]:
        props = {}
        required = []
        for p in self.parameters:
            props[p.name] = {"type": p.type, "description": p.description}
            if p.required:
                required.append(p.name)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                },
            },
        }


@dataclass
class ChatResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, int] | None = None
    latency_ms: float = 0.0
    tool_calls: list[dict[str, Any]] | None = None


@dataclass
class Chunk:
    content: str
    done: bool = False
    usage: dict[str, int] | None = None


@dataclass
class EmbeddingResponse:
    vectors: list[list[float]]
    model: str
    provider: str
    latency_ms: float = 0.0
    usage: dict[str, int] | None = None


@dataclass
class ModelSpec:
    id: str
    name: str
    context_window: int = 4096
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False
    supports_embeddings: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    is_default: bool = False


class ProviderCapability(Enum):
    CHAT = auto()
    REASONING = auto()
    STREAMING = auto()
    EMBEDDINGS = auto()
    TOOL_CALLING = auto()
    STRUCTURED_OUTPUT = auto()
    VISION = auto()
    CODE_GENERATION = auto()
    LONG_CONTEXT = auto()


@dataclass
class ProviderCapabilities:
    capabilities: set[ProviderCapability] = field(default_factory=lambda: {ProviderCapability.CHAT})
    max_context_window: int = 4096
    max_batch_size: int = 1


@dataclass
class ProviderHealth:
    healthy: bool = True
    latency_ms: float = 0.0
    errors_last_minute: int = 0
    rate_limited: bool = False
    message: str = ""
    last_check: float = 0.0


@dataclass
class BenchmarkResult:
    provider_id: str
    model: str
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    tokens_per_second: float = 0.0
    success_rate: float = 1.0
    cost_per_1k_tokens: float = 0.0
    samples: int = 0
    timestamp: float = 0.0


class AIProvider(ABC):
    provider_id: str
    models: list[ModelSpec]

    @abstractmethod
    def chat(self, messages: list[Message], model: str | None = None, **kwargs) -> ChatResponse: ...

    @abstractmethod
    def stream_chat(self, messages: list[Message], model: str | None = None, **kwargs) -> Iterator[Chunk]: ...

    @abstractmethod
    def embeddings(self, texts: list[str], model: str | None = None) -> EmbeddingResponse: ...

    @abstractmethod
    def tool_call(self, messages: list[Message], tools: list[ToolSpec], model: str | None = None, **kwargs) -> ChatResponse: ...

    @abstractmethod
    def check_capabilities(self) -> ProviderCapabilities: ...

    @abstractmethod
    def health(self) -> ProviderHealth: ...

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def get_default_model(self) -> str:
        for m in self.models:
            if m.is_default:
                return m.id
        return self.models[0].id if self.models else ""



