# UAIEOS Engine Specification: Evaluation Orchestration

This document details the code implementations, evaluation algorithms, and reporting pipeline configurations of the UAIEOS Evaluation Orchestration Engine.

---

## 1. Batch Execution Pipeline

The Evaluation Engine reads candidate test sets, runs batch inferences, applies quality evaluation metrics, and determines if a pipeline can proceed to certification.

```
       [Load Test Set JSON]
                 |
                 v
     +-----------------------+
     | Batch Runner Thread   |
     |   (Model Inferences)  |
     +-----------------------+
                 |
                 v
     +-----------------------+
     | Evaluation Scoring    | -> (Calculates ECE, Z-score, Grounding)
     +-----------------------+
                 |
                 v
     +-----------------------+
     |   Regression Report   | -> (Compares Cohort metrics)
     +-----------------------+
```

---

## 2. Evaluation Engine Implementation (Python)

```python
from typing import List, Dict, Any
import numpy as np
import math
import json

class EvaluationMetricsCalculator:
    
    @staticmethod
    def calculate_ece(confidences: List[float], accuracies: List[int], num_bins: int = 10) -> float:
        """Calculates the Expected Calibration Error (ECE) for safety classifications.
        
        ECE = Sum_m (|B_m| / N) * |acc(B_m) - conf(B_m)|
        """
        n = len(confidences)
        if n == 0:
            return 0.0
            
        bins = np.linspace(0.0, 1.0, num_bins + 1)
        ece = 0.0
        
        for i in range(num_bins):
            bin_lower = bins[i]
            bin_upper = bins[i+1]
            
            # Select samples that fall within bin bounds
            in_bin = [
                j for j in range(n)
                if confidences[j] >= bin_lower and confidences[j] < bin_upper
            ]
            
            bin_size = len(in_bin)
            if bin_size > 0:
                bin_acc = sum(accuracies[j] for j in in_bin) / bin_size
                bin_conf = sum(confidences[j] for j in in_bin) / bin_size
                ece += (bin_size / n) * abs(bin_acc - bin_conf)
                
        return float(ece)

    @staticmethod
    def calculate_z_score(success_rate_1: float, count_1: int, success_rate_2: float, count_2: int) -> float:
        """Computes the Cohort Z-score for evaluating model updates.
        
        Z = (p1 - p2) / sqrt(p*(1-p)*(1/n1 + 1/n2))
        """
        p1 = success_rate_1
        p2 = success_rate_2
        n1 = count_1
        n2 = count_2
        
        if n1 == 0 or n2 == 0:
            return 0.0
            
        # Reconstruct total successes
        x1 = p1 * n1
        x2 = p2 * n2
        
        p = (x1 + x2) / (n1 + n2)
        if p == 0.0 or p == 1.0:
            return 0.0
            
        se = math.sqrt(p * (1.0 - p) * ((1.0 / n1) + (1.0 / n2)))
        return (p1 - p2) / se
```

---

## 3. LLM-as-a-Judge Prompt and Parser Engine

The parser leverages structured schema parsing to extract raw JSON results from the judge's completion payload.

### 3.1 LLM-as-a-Judge Meta-Prompt Template
```python
LLM_JUDGE_PROMPT = """
You are a highly precise evaluation judge. Rate the candidate response based on the retrieved context.

[RETRIEVED CONTEXT]
{context}

[USER QUERY]
{query}

[CANDIDATE RESPONSE]
{response}

[EVALUATION RULES]
1. Grounding: Check if the response contains facts NOT found in the context.
2. Relevance: Check if the response directly addresses the query.

Provide your evaluation output strictly as a JSON object inside markdown backticks:
```json
{{
  "grounding_score": <float between 0.0 and 1.0>,
  "relevance_score": <float between 0.0 and 1.0>,
  "reasoning": "<Reason for calculation>"
}}
```
"""
```

### 3.2 Evaluation Parser Implementation
```python
class LLMJudgeParser:
    @staticmethod
    def parse_judge_output(raw_completion: str) -> Dict[str, Any]:
        """Extracts JSON block from markdown response output."""
        try:
            # Find the markdown code block boundary
            start_marker = "```json"
            end_marker = "```"
            
            if start_marker in raw_completion:
                start_idx = raw_completion.find(start_marker) + len(start_marker)
                end_idx = raw_completion.find(end_marker, start_idx)
                json_content = raw_completion[start_idx:end_idx].strip()
            else:
                json_content = raw_completion.strip()
                
            parsed = json.loads(json_content)
            required_keys = ["grounding_score", "relevance_score", "reasoning"]
            for key in required_keys:
                if key not in parsed:
                    raise KeyError(f"Missing required key: {key}")
            return parsed
        except Exception as e:
            return {
                "grounding_score": 0.0,
                "relevance_score": 0.0,
                "reasoning": f"Failed to parse evaluator response: {str(e)}"
            }
```

---

## 4. System Cross-References
*   For dataset design and the grounding/relevance score formulations, see [PART_11_EVALUATION_BENCHMARKING.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_11_EVALUATION_BENCHMARKING.md).
*   For safety classification validation tests, see [PART_10_AI_SAFETY_GOVERNANCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_10_AI_SAFETY_GOVERNANCE.md).
*   For the deployment gatekeeper which queries this evaluation engine, see [ENGINE_CERTIFICATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_CERTIFICATION.md).
