# Part 18 — Autonomous Product AI

## 1. Context & Strategy

### 1.1 Purpose
The Autonomous Product AI Part details standardized prompt engineering, input validation, and system instructions for AI agents generating PRDs, screen layouts, and user storyboards.

---

## 2. Automated PRD Generation Prompts

To generate consistent, institution-grade Product Requirements Documents (PRDs), AI agents use the following structured system prompt:

```yaml
System Prompt: |
  You are the Lead Product Architect of Project Venus. Your task is to generate a comprehensive Product Requirements Document (PRD) for the target feature.
  
  Your output MUST adhere strictly to the following sections:
  1. Executive Summary & Problem Validation (JTBD mapping)
  2. Scope & Target Audience (ICP profiles, exclusions)
  3. Feature Requirements Table (Feature ID, priority, user story, acceptance criteria)
  4. Non-Functional Requirements (Performance, Security, Compliance)
  5. Metrics & Success Criteria (KPIs, analytics tracking coordinates)
  
  Strict Constraint: DO NOT use placeholders, "TODOs", or ellipses. Write every requirement in full detail.
```

---

## 3. Screen Wireframing & Layout Generation

AI agents can generate text-based ASCII wireframe designs and schema-valid layouts for developer handoff.

### 3.1 ASCII Layout Schema Prompt
```yaml
System Prompt: |
  Generate an ASCII representation of the target user interface.
  Your layout must specify the column layout (desktop 12-column grid or mobile 4-column stack) and touch target bounding sizes (>= 48px).
  
  Example Output Format:
  +--------------------------------------------------------+
  |  [Logo]   [Search input: size=48px]   [Avatar: size=48px] |
  +--------------------------------------------------------+
  |  (Sidebar) |  [Dashboard Title]                        |
  |  - Home    |  +-------------------------------------+  |
  |  - Reports |  |  [Metric Widget]                    |  |
  |  - Settings|  |  Total Users: 12,450 (+12% MoM)     |  |
  |            |  +-------------------------------------+  |
  +------------+-------------------------------------------+
```

### 3.2 JSON UI Schema for Automated Rendering
AI engines generate JSON representations of layouts that UI rendering engines parse directly:

```json
{
  "$schema": "https://projectvenus.ai/schemas/ui-layout-v1.json",
  "component": "PageLayout",
  "props": { "grid": "desktop-12", "margin": 32 },
  "children": [
    {
      "component": "Header",
      "props": { "height": 64, "ariaLabel": "Global Header" },
      "children": [
        { "component": "SearchInput", "props": { "minWidth": 240, "height": 48 } }
      ]
    }
  ]
}
```

---

## 4. Automated User Storyboards

Storyboarding maps user workflows across multiple contexts to clarify emotional states, actions, and system feedback.

### 4.1 Storyboard Prompt Structure
```yaml
System Prompt: |
  Generate a 3-act User Storyboard mapping the target user journey.
  For each act, specify:
  - User Context (Environment, motivation)
  - Action Taken (Direct interface interaction)
  - System Response (Visual, dynamic state change)
  - User Emotion (High, Neutral, Frustrated - with explanation)
```

### 4.2 Act Mapping Schema
```
Act 1: Discovery  ──►  Act 2: Action  ──►  Act 3: Success
 (User logs in)         (Invites colleague)     (Colleague joins)
```

---

## 5. Autonomous Product AI Checklist
*   [ ] Checked target AI model system prompt matches PRD requirements.
*   [ ] Verified ASCII/JSON wireframe output matches grid layout rules.
*   [ ] Checked that UI schemas define appropriate aria labels and touch sizing.
*   [ ] Executed storyboard generation loops and mapped user emotional states.
*   [ ] Confirmed generated outputs do not contain placeholders.
