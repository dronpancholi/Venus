# Template: AI Opportunity Assessment

## 1. Meta Control
*   **Project Name**: [Project Name]
*   **Intake ID**: INT-[UUID]
*   **Assessment ID**: AI-OPP-[UUID]
*   **Last Updated**: [Date]
*   **Lead AI Engineer**: [Name]

---

## 2. The AI Suitability Decision Flow
*Ensure that AI is only introduced where it provides a measurable advantage over traditional algorithms.*

```
                 [Is the logic purely rules-based or mathematical?]
                                         │
                        ┌────────────────┴────────────────┐
                       YES                                NO
                        │                                 │
            [Classify: Simple Automation]         [Is high accuracy critical with
            *Use regex, SQL, or code*             zero tolerance for hallucination?]
                                                                  │
                                                 ┌────────────────┴────────────────┐
                                                YES                                NO
                                                 │                                 │
                                     [Classify: Traditional ML/SQL]    [Does the task require
                                     *Use regression, XGBoost, etc.*   semantic synthesis / chat?]
                                                                                   │
                                                                   ┌───────────────┴───────────────┐
                                                                  YES                              NO
                                                                   │                               │
                                                        [Classify: LLM / Agents]          [No AI/Automation]
                                                        *Use LLM or Multi-Agent*
```

---

## 3. Component Capability Classification
Evaluate each core component of the proposed system to determine the correct technology profile:

| Component Name | Description of Task | Selected Technology Profile | Justification | Alternatives Considered | Expected Cost / Token Budget |
|---|---|---|---|---|---|
| **Email Filter** | Identify blocklisted domain names | **Simple Automation** (Regex/SQL) | Rules are static; zero room for hallucination, zero compute cost. | LLM classification | $0.00 |
| **Site Quality** | Score web page authority and spam profile | **Machine Learning** (XGBoost) | Requires numerical prediction based on 50 distinct inputs; logic is static. | Multi-Agent planning | $0.00 (Self-hosted) |
| **Review Queue** | Synthesize text from emails, draft responses | **LLM** (Structured output JSON) | High semantic variety, requires synthesis. | Simple Automation | $0.002 / email |
| **Outreach Planner**| Research contact info, design path, coordinate | **Multi-Agent / Planning Agent** | Requires long-term multi-step execution. | Rigid workflow scripts | $0.25 / campaign |

---

## 4. Technology Profiles Directory
*   **Simple Automation**: Heuristic rules, regular expressions, Cron jobs, database procedures.
*   **Workflow Automation**: Zapier, Temporal, Airflow DAGs, state machines.
*   **Machine Learning (ML)**: Scikit-learn, XGBoost, clustering models, TensorFlow.
*   **LLM**: Zero/few-shot semantic classification, parsing, JSON extraction, summarization.
*   **Multi-Agent**: Independent LLM processes cooperating via messaging protocols.
*   **Planning Agent**: Tree-of-Thought planning, self-correction, tools use.
*   **Hybrid**: Combined heuristics (filter) and LLM (inference) to minimize cost and latency.

---

## 5. Security & Hallucination Mitigation Plan
*If LLM/Agent technology is selected, describe the mitigation strategies used to prevent typical AI failures.*

*   **Risk Vector**: Hallucination of outreach content.
    *   *Mitigation Strategy*: Strict JSON schema mapping + downstream regex checks on outgoing URLs.
*   **Risk Vector**: Prompt Injection on inbound emails.
    *   *Mitigation Strategy*: Treat all parsed outputs as unverified strings; separate user payload content from prompt system variables.
*   **Risk Vector**: Token Cost Escalation.
    *   *Mitigation Strategy*: Implement maximum rate limits per user key; cache semantic vector search queries to bypass raw LLM hits.
