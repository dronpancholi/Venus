# UAIEOS Engine Specification: AI Safety Guardrails

This technical specification details the software architectures, interceptor middleware implementations, and safety analysis algorithms of the UAIEOS AI Safety Guardrails Engine.

---

## 1. Interceptor Middleware Architecture

The Safety Guardrails Engine operates as an interceptor pipeline within the Core Runtime, filtering queries on ingress and generated completions on egress.

```
       [Request Ingress]
               |
               v
  +--------------------------+
  |  Jailbreak Interceptor   | -> (Fails if score < threshold)
  +--------------------------+
               |
               v
  +--------------------------+
  |    PII Redactor Unit     | -> (Redacts matching entity patterns)
  +--------------------------+
               |
               v
    [Model Inference Run]
               |
               v
  +--------------------------+
  |   Toxicity Interceptor   | -> (Fails if toxic probability > 0.01)
  +--------------------------+
               |
               v
  +--------------------------+
  |   Semantic Drift Check   | -> (Fails if Cosine Similarity < 0.65)
  +--------------------------+
               |
               v
       [Response Egress]
```

---

## 2. Interface and Interceptor Definitions (Python)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import re

class GuardrailException(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

class ISafetyInterceptor(ABC):
    @abstractmethod
    def process_request(self, content: str, context: Dict[str, Any]) -> str:
        """Processes and filters/redacts inbound request strings.
        Raises GuardrailException if security threshold is breached.
        """
        pass

    @abstractmethod
    def process_response(self, content: str, context: Dict[str, Any]) -> str:
        """Processes and filters outbound model completions before delivery.
        Raises GuardrailException if output validation fails.
        """
        pass
```

---

## 3. Concrete Interceptor Implementations

### 3.1 PII Redaction Interceptor
This class detects and replaces sensitive identifiers (such as US Social Security Numbers or generic API Keys) using regular expressions.

```python
class PIIRedactionInterceptor(ISafetyInterceptor):
    def __init__(self):
        # Compiled patterns for SSN and Generic API Secret Keys
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.key_pattern = re.compile(r'\b(sk_[a-zA-Z0-9]{32,48})\b')

    def process_request(self, content: str, context: Dict[str, Any]) -> str:
        content = self.ssn_pattern.sub("[REDACTED_SSN]", content)
        content = self.key_pattern.sub("[REDACTED_API_KEY]", content)
        return content

    def process_response(self, content: str, context: Dict[str, Any]) -> str:
        # Re-apply filters to verify generated output does not leak secrets
        content = self.ssn_pattern.sub("[REDACTED_SSN]", content)
        content = self.key_pattern.sub("[REDACTED_API_KEY]", content)
        return content
```

### 3.2 Semantic Drift and Vector Guardrail
Calculates the semantic distance between the target user prompt and the generated completion using cosine similarity metrics as specified in [PART_10_AI_SAFETY_GOVERNANCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_10_AI_SAFETY_GOVERNANCE.md#L50-L65).

```python
import numpy as np

class VectorSemanticGuardrail(ISafetyInterceptor):
    def __init__(self, embedding_client: Any, min_similarity: float = 0.65):
        self.embedding_client = embedding_client
        self.min_similarity = min_similarity

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))

    def process_request(self, content: str, context: Dict[str, Any]) -> str:
        # Request passes through; baseline embedding cached for response checking
        context["request_embedding"] = self.embedding_client.get_embedding(content)
        return content

    def process_response(self, content: str, context: Dict[str, Any]) -> str:
        if "request_embedding" not in context:
            return content
        
        response_embedding = self.embedding_client.get_embedding(content)
        req_emb = np.array(context["request_embedding"])
        res_emb = np.array(response_embedding)
        
        similarity = self._cosine_similarity(req_emb, res_emb)
        if similarity < self.min_similarity:
            raise GuardrailException(
                "SEMANTIC_DRIFT_DETECTED",
                f"Output similarity {similarity:.4f} fell below minimum limit of {self.min_similarity}."
            )
        return content
```

### 3.3 Prompt Injection Guardrail
Checks input text for common prompt injection patterns using token probability scoring or signature keywords.

```python
class InjectionGuardrail(ISafetyInterceptor):
    def __init__(self):
        self.blacklist = [
            "ignore previous instructions",
            "ignore all instructions",
            "bypass system instructions",
            "system override",
            "you are now a simulator"
        ]

    def process_request(self, content: str, context: Dict[str, Any]) -> str:
        normalized_content = content.lower()
        for phrase in self.blacklist:
            if phrase in normalized_content:
                raise GuardrailException(
                    "PROMPT_INJECTION_VIOLATION",
                    f"Forbidden control instruction detected: '{phrase}'."
                )
        return content

    def process_response(self, content: str, context: Dict[str, Any]) -> str:
        return content
```

---

## 4. System Cross-References
*   For the safety metrics, ECE calculation requirements, and red-teaming criteria details, see [PART_10_AI_SAFETY_GOVERNANCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_10_AI_SAFETY_GOVERNANCE.md).
*   For evaluation metrics used during safety test suites, see [ENGINE_EVALUATION_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_EVALUATION_ORCHESTRATION.md).
*   For error tracing integration configurations, see [ENGINE_OBSERVABILITY_TELEMETRY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_OBSERVABILITY_TELEMETRY.md).
