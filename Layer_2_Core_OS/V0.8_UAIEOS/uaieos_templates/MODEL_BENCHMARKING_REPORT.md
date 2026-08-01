# Model Benchmarking Report
**Document ID:** Venus-UAIEOS-TEMP-27  
**Version:** V0.8  
**Classification:** Institutional-Grade Operations Template  
**Target Directory:** `file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_templates/`  

---

## 1. Executive Summary & Objectives

Selecting the appropriate LLM for production agents requires a continuous, multi-dimensional trade-off analysis between task accuracy, latency, execution cost, and operational footprint.

This document serves as the **Model Benchmarking Report Template** to:
1. Standardize reporting on throughput, TTFT (Time to First Token), and cost metrics.
2. Outline statistical validation calculations to assess model performance gains.
3. Compare proprietary frontier models against fine-tuned local models.
4. Document deployment recommendation decisions.

---

## 2. Benchmark Metrics & Formulations

Every candidate model evaluation must compile the following core metrics:

### 2.1 Latency Metrics
*   **Time to First Token (TTFT):** The time from sending the request to receiving the first generated chunk.
*   **Inter-Token Latency (ITL):** Average time between sequential tokens generated during stream output.
*   **Throughput (T):** Total output tokens divided by generation time:

$$T = \frac{N_{\text{output tokens}}}{T_{\text{total latency}} - \text{TTFT}} \quad [\text{tokens/sec}]$$

### 2.2 Cost Model (Token Cost)
The total Cost ($C_{\text{run}}$) is computed using the unit pricing for input and output tokens:

$$C_{\text{run}} = \left( N_{\text{input tokens}} \cdot P_{\text{input\_unit}} \right) + \left( N_{\text{output tokens}} \cdot P_{\text{output\_unit}} \right)$$

Where $P_{\text{unit}}$ is standard pricing per 1,000,000 tokens.

### 2.3 Statistical Performance Difference (Z-score)
To determine if a model upgrade results in a statistically significant change in accuracy, the Cohort Z-score is calculated:

$$Z = \frac{p_{\text{challenger}} - p_{\text{champion}}}{\sqrt{p(1-p)\left(\frac{1}{n_{\text{challenger}}} + \frac{1}{n_{\text{champion}}}\right)}}$$

Where $p$ is the pooled success rate. A Z-score greater than $|1.96|$ indicates significance at the $95\%$ confidence level.

---

## 3. Benchmarking Evaluation Matrix

*Enter actual test run data in the table below to analyze model performance profiles.*

| Model Identifier | Parameter Count | Mean TTFT (ms) | Mean ITL (ms) | Output Throughput (tok/sec) | Input Cost / 1M | Output Cost / 1M | ECE Score | Z-score vs Champion |
|---|---|---|---|---|---|---|---|---|
| `frontier-champion` | Closed | 280ms | 12ms | 83 tok/s | $5.00 | $15.00 | 0.038 | *Reference* |
| `frontier-challenger`| Closed | 210ms | 10ms | 100 tok/s | $2.50 | $10.00 | 0.045 | +2.18 (Significant) |
| `local-llama-70b` | 70B | 450ms | 22ms | 45 tok/s | $0.80 | $0.80 | 0.058 | -1.88 (Insignificant) |
| `local-llama-8b`  | 8B | 120ms | 8ms | 125 tok/s | $0.15 | $0.15 | 0.082 | -4.62 (Degraded) |

---

## 4. Workload Profile Selection Guide

```mermaid
decisionDiagram
    TaskType: Is the task latency-critical or reasoning-heavy?
    TaskType -->|Latency-Critical| LatencyCheck: Check Llama-8B (TTFT < 150ms)
    TaskType -->|Reasoning-Heavy| CostCheck: Check budget constraints
    CostCheck -->|High Budget| Frontier: Select Frontier-Challenger (Z-score +2.18)
    CostCheck -->|Low Budget| LocalBig: Select Local-Llama-70b
```

---

## 5. Benchmarking Execution Framework (Python Harness)

```python
"""
Venus Benchmark Execution and Latency Log
"""
import time
import requests
from typing import Dict, Any

def run_latency_benchmark(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, float]:
    """
    Executes a benchmark run calculating TTFT and generation throughput.
    """
    start_time = time.perf_counter()
    response = requests.post(url, headers=headers, json=payload, stream=True)
    
    ttft = 0.0
    first_token_received = False
    tokens_count = 0
    
    for chunk in response.iter_content(chunk_size=128):
        if not first_token_received:
            ttft = (time.perf_counter() - start_time) * 1000 # ms
            first_token_received = True
        # Parse chunk stream to count tokens...
        tokens_count += 1
        
    total_time = (time.perf_counter() - start_time) * 1000 # ms
    generation_time = total_time - ttft
    
    throughput = (tokens_count / (generation_time / 1000)) if generation_time > 0 else 0
    
    return {
        "ttft_ms": ttft,
        "total_time_ms": total_time,
        "throughput_tps": throughput,
        "tokens_generated": tokens_count
    }
```

---

## 6. Recommendations & Approvals

Use this signature block to approve model migration updates:

*   **Benchmarking Engineer Signature:** `____________________` **Date:** `__________`
*   **Lead ML Architect Signature:** `____________________` **Date:** `__________`
*   **Operational Decision:** `[PROMPT FOR DEPLOYMENT / STAGE RETENTION / ROLLBACK]`

---
*For questions regarding benchmarking metrics, refer to the performance tuning office at [Venus Systems](file:///Users/dronpancholi/Developer/01_Strategic/Venus/).*
