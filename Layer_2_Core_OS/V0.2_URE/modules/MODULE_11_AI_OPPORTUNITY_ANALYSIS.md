# Module 11 — AI Opportunity Analysis

## 1. Context & Strategy

### 1.1 Purpose
AI adds complexity, cost, and non-determinism to software systems. The AI Opportunity Analysis Engine evaluates all automation opportunities identified in the problem space, classifying them into distinct execution models (from No AI to Multi-Agent Planning) and providing objective justifications for each choice.

### 1.2 Philosophy
AI is not a default; it is a last resort for tasks that cannot be solved via deterministic rules. Our objective is to minimize AI usage in critical control loops, reserving LLM/ML calls for semantic tasks.

---

## 2. AI Automation Taxonomy

We classify automation requirements into eleven execution tiers:
1.  **No AI**: Tasks solved via basic SQL queries, Regex parsing, or standard mathematical formulas.
2.  **Simple Automation**: Basic scripts, cron jobs, and email delivery.
3.  **Workflow Automation**: State machines and durable orchestration sagas (Temporal).
4.  **Machine Learning (ML)**: Traditional predictive models (regression, classification, clustering).
5.  **Large Language Model (LLM)**: Single call text generation, translation, or extraction.
6.  **Multi-Agent**: Independent LLM agents executing parallel activities.
7.  **Planning Agent**: Agents that construct their own execution graphs based on a prompt.
8.  **Reasoning Agent**: Models utilizing chain-of-thought processing to solve complex logic.
9.  **Computer Vision**: Image extraction, target detection, layout checking.
10. **Speech**: Audio transcription, text-to-speech.
11. **Hybrid**: Structured combinations of ML models, LLMs, and deterministic rules.

---

## 3. Inputs & Outputs

### 3.1 Inputs
*   Verified Problem Statement (from Stage 1).
*   User Journey high-friction steps (from Stage 3).
*   Economic Model bounds (from Stage 7).

### 3.2 Outputs
*   **AI Suitability Directory**: Classified list of system features with target tiers.
*   **AI Architecture Justifications Document**: Written evidence backing model allocations.

---

## 4. Operational Methodology & Decision Matrix

### 4.1 Automated Capability Router
For every proposed feature, the engine runs the following logic path:

```
                            Feature Target
                                  │
      ┌───────────────────────────┴───────────────────────────┐
      ▼                                                       ▼
[Deterministic Logic]                                 [Semantic Logic]
(Use Tiers 1, 2, 3)                                    (Ask: Is order critical?)
                                                              │
                                            ┌─────────────────┴─────────────────┐
                                            ▼                                   ▼
                                          [Yes]                                [No]
                                    (Use Tier 11 Hybrid)                  (Ask: Planning needed?)
                                                                                │
                                                              ┌─────────────────┴─────────────────┐
                                                              ▼                                   ▼
                                                            [Yes]                                [No]
                                                      (Use Tier 7/8 Agents)              (Use Tier 5 LLM Wrapper)
```

---

## 5. Reusable Checklists & Templates

### 5.1 AI Analysis Checklist
*   [ ] Evaluated and rejected deterministic alternatives for every feature.
*   [ ] Checked LLM token costs against user subscription pricing models.
*   [ ] Mapped the target execution tier for all automation features.
*   [ ] Documented fallbacks for non-deterministic model failures.
*   [ ] Vetted data policy agreements for target inference providers.

### 5.2 Template: AI Capability Assessment Entry
```markdown
### 1. Feature Profile: AIC-[UUID]
*   **Feature Name**: [e.g., Competitor Competitor Discovery Fallback]
*   **Assigned Automation Tier**: Tier 11 (Hybrid: DataForSEO API + LLM fallback)
*   **Why Deterministic Fails**: Competitor databases can be incomplete or contain unclassified new startups, requiring LLM inference of likely related brands based on business context.

### 2. Architectural Justification
*   *Primary Route*: Call DataForSEO API (Tier 1). If API returns empty list, trigger LLM generation activity (Tier 5).
*   *Grounding Method*: Check LLM generated competitors against Google search results using a regex match.
*   *Economic Feasibility*: Est. Cost per query: $0.005. Gross margin impact: Negligible.
```

---

## 6. SRE, AI-Agent, & Safety Parameters

### 6.1 AI-Agent Execution Instructions
1.  **Read**: Review the list of user actions and input data types.
2.  **Evaluate**: Run the capability router across all features.
3.  **Validate**: Verify that no LLM/agent call is placed in a critical system control loop (e.g. billing validation) where 100% determinism is required.

### 6.2 Common Anti-patterns
*   **Prompt-for-Everything**: Using LLM calls for structured data formatting tasks that could be handled via JSON parsers.
*   **Agent Inflation**: Building complex multi-agent frameworks for simple sequential workflows where a single state machine (Temporal) is more reliable and 10x cheaper.

### 6.3 Exit Criteria
*   AI Suitability Directory compiled and **AI justifications signed-off**.
*   Proceed to **Module 12: Success Definition**.
