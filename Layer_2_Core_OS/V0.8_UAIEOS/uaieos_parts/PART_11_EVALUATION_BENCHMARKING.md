# UAIEOS Part 11: Evaluation & Benchmarking Manual

This manual details the procedures, metrics, mathematical formulations, and validation engines required to benchmark large language models and autonomous agents within the UAIEOS.

---

## 1. Ground Truth Dataset Construction

Evaluation is only as good as the reference dataset. The UAIEOS requires a three-tiered dataset architecture:

1.  **Golden Set (Static):** Hand-curated, highly validated query-context-response pairs representing edge cases and standard enterprise tasks. Size: $\ge 1,000$ cases.
2.  **Synthetic Drift Set (Dynamic):** Generated using LLM-based perturbations (rephrasing, negative constraints) to test model robusteness under prompt variation.
3.  **Adversarial Set (Red-Teaming):** Explicitly designed jailbreak attempts, prompt injections, and invalid instruction formatting sets.

---

## 2. Evaluation Metrics: Grounding, Relevance, and Citations

For Retrieval-Augmented Generation (RAG) and retrieval-grounded tasks, evaluation relies on mathematical scores derived from semantic and lexical overlap metrics.

### 2.1 Grounding Score ($S_{\text{ground}}$)
Measures the extent to which the generated answer relies strictly on the retrieved context, penalizing hallucinations.

Let $E_{\text{ent}}$ be the set of factual entities (extracted via named entity recognition) present in the generated answer $A$, and $C_{\text{ent}}$ be the set of factual entities present in the retrieved context $C$.

$$S_{\text{ground}} = \frac{|E_{\text{ent}} \cap C_{\text{ent}}|}{|E_{\text{ent}}|}$$

If $|E_{\text{ent}}| = 0$, the system defaults to sentence-level semantic containment scoring using embedding alignments:

$$S_{\text{ground}} = \frac{1}{|S_A|} \sum_{s \in S_A} \max_{c \in S_C} \left( \text{Cos}(s, c) \right)$$

Where $S_A$ are sentences in the answer, $S_C$ are sentences in the context, and $\text{Cos}(s, c)$ is the cosine similarity of their embedding representations.

### 2.2 Relevance Score ($S_{\text{rel}}$)
Measures how directly the generated answer addresses the user's initial query $Q$.

$$S_{\text{rel}} = \text{Cos}(Q, A) = \frac{Q \cdot A}{\|Q\| \|A\|}$$

*   **Acceptance Target:** $S_{\text{rel}} \ge 0.78$ for standard retrieval configurations.

### 2.3 Citation Precision ($S_{\text{cite}}$)
Measures whether inline citations accurately link to the underlying retrieved document chunks.

Let $C_{\text{total}}$ be the total number of citations generated in the response, and $C_{\text{verified}}$ be the subset of citations whose referenced content mathematically contains the factual assertions made in the text segment.

$$S_{\text{cite}} = \frac{|C_{\text{verified}}|}{|C_{\text{total}}|}$$

---

## 3. Automatic Evaluation Pipelines (LLM-as-a-Judge)

To scale evaluation, the UAIEOS orchestrates a LLM-as-a-Judge pipeline. The evaluator agent is provided a meta-prompt containing:
*   The raw user query.
*   The retrieved context.
*   The system instructions.
*   The generated agent response.
*   A evaluation rubrics matrix.

The judge must return a structured JSON report mapping to the following parameters:

```json
{
  "evaluation_id": "eval-88112-xyz",
  "scores": {
    "grounding_score": 0.92,
    "relevance_score": 0.88,
    "citation_precision": 1.00
  },
  "rationale": "The response accurately summarized the database schemas in the context without introducing external entities. The citation perfectly matches paragraph 3.",
  "verdict": "PASS"
}
```

---

## 4. Cohort Z-Score Statistical Validation

When assessing if a newly tuned prompt or a model update (Cohort 1) outperforms the existing production system (Cohort 2), evaluation cannot rely on raw averages alone. We perform statistical validation using a two-proportion Z-test.

$$Z = \frac{p_1 - p_2}{\sqrt{p(1-p)\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}}$$

Where:
*   $p_1$ is the proportion of successful responses in Cohort 1 ($p_1 = x_1 / n_1$).
*   $p_2$ is the proportion of successful responses in Cohort 2 ($p_2 = x_2 / n_2$).
*   $n_1, n_2$ are the total test samples evaluated for each cohort.
*   $p$ is the pooled success proportion:
    $$p = \frac{x_1 + x_2}{n_1 + n_2}$$

### 4.1 Statistical Thresholds
*   **$|Z| > 1.96$:** Reject the null hypothesis. The difference between cohorts is statistically significant at the $95\%$ confidence level ($\alpha = 0.05$).
*   **$|Z| > 2.58$:** Statistically significant at the $99\%$ confidence level ($\alpha = 0.01$).
*   **Policy:** A change is only promoted to production if $Z > 1.96$ in favor of the new cohort and no safety regressions occur.

---

## 5. System Cross-References
*   To implement these evaluation metrics programmatically, see [ENGINE_EVALUATION_ORCHESTRATION.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_EVALUATION_ORCHESTRATION.md).
*   For safety evaluation rules and calibration methods, see [PART_10_AI_SAFETY_GOVERNANCE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_10_AI_SAFETY_GOVERNANCE.md).
*   For trace collectors supporting the evaluation datasets, see [PART_12_OBSERVABILITY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_12_OBSERVABILITY.md).
