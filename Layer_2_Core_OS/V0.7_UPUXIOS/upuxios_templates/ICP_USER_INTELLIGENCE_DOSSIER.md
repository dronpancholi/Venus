# Ideal Customer Profile (ICP) & User Intelligence Dossier

## 1. Overview
This dossier defines the Ideal Customer Profile (ICP) and key user personas for the product. It bridges target market demographics (firmographics) with day-to-day user realities (demographics/psychographics) to guide product, design, and marketing alignment.

---

## 2. Ideal Customer Profile (ICP) - Firmographics & Technographics
The ICP outlines the organizational characteristics of the high-value target accounts that get the most value from our product and provide the highest lifetime value (LTV).

| Attribute | Criteria / Range | Description |
| :--- | :--- | :--- |
| **Target Industries** | *e.g., Fintech, Enterprise SaaS, Healthcare* | Primary industry sectors where the problem is acute. |
| **Company Size (FTEs)**| *e.g., 100 - 1000 employees* | Scale of operations and organizational complexity. |
| **Annual Revenue** | *e.g., $10M - $100M ARR* | Financial capability to invest in premium solutions. |
| **Geography** | *e.g., North America, Western Europe* | Regulatory and operational footprint. |
| **Technographic Stack**| *e.g., AWS, Snowflake, Kubernetes, Salesforce*| Existing software/infrastructure dependencies. |
| **Key Regulatory Env** | *e.g., HIPAA, SOC2 Type II, GDPR* | Required compliance and security postures. |

---

## 3. User Persona Dossier: The Primary User
While the ICP is the company, the persona is the human being who uses or buys the software.

```
       +--------------------------------------------+
       |   [ PHOTO / ICON ]                         |
       |   Role: Lead Data Engineer                 |
       |   Name: "Data-driven Dave"                 |
       |   Age Range: 30-45 | Exp: Senior Level     |
       +--------------------------------------------+
       |   Goals:                                   |
       |   - Ensure zero downtime in pipelines.     |
       |   - Optimize cloud infrastructure costs.   |
       +--------------------------------------------+
```

### 3.1. Demographic Profile
*   **Job Title:** `[e.g., Lead Data Engineer, Head of Growth]`
*   **Department:** `[e.g., Engineering, Marketing, Operations]`
*   **Reports To:** `[e.g., VP of Engineering, CTO]`
*   **Education / Background:** `[e.g., BS in Computer Science, self-taught analyst]`

### 3.2. Psychographic Profile & Goals
*   **Primary Motivators:** [What drives them? e.g., Career growth, team efficiency, status]
*   **Core Work Goals:**
    1.  [e.g., Automate repetitive extraction tasks]
    2.  [e.g., Reduce report generation latency to < 5 minutes]
*   **Biggest Daily Frustrations:**
    *   [e.g., Debugging broken API integrations at 2 AM]
    *   [e.g., Copy-pasting data between legacy Excel sheets]

### 3.3. Tech & Product Habits
*   **Preferred Tools:** `[e.g., Slack, GitHub, VS Code, Terminal]`
*   **Device Mix:** `[e.g., 90% Desktop (macOS), 10% Mobile (iOS)]`
*   **Learning/Information Channels:** `[e.g., Hacker News, Reddit (r/dataengineering), StackOverflow]`

---

## 4. Buying Persona & Decision-Maker Profile
*If the primary user is not the economic buyer, detail the buyer profile.*

*   **Buyer Job Title:** `[e.g., VP of Operations, CTO, Chief Data Officer]`
*   **Buying Triggers:** `[e.g., Compliance audit failure, budget overruns, team retention drop]`
*   **Key Objections to Overcome:**
    1.  *Integration cost:* "How long will it take my team to configure this?"
    2.  *Data security:* "Does this vendor meet our SOC2 compliance requirements?"
    3.  *ROI proof:* "Can I prove that this tool will save us hours or money?"

---

## 5. Anti-ICP & Anti-Personas
We actively avoid designing for or selling to the following profiles, as they increase churn and divert support resources.

| Profile Name | Characteristics | Why We Avoid Them |
| :--- | :--- | :--- |
| **"The DIY Hacker"** | Small freelancer; wants deep customization; low willingness to pay. | High support overhead; requests edge-case features that don't scale. |
| **"Legacy Enterprise"**| Firm relying on on-prem databases; refuses cloud solutions. | Long sales cycles; requires custom engineering; conflicts with cloud-first architecture. |
| | | |

---

## 6. Revision History
*   **V1.0 (2026-06-26):** Initial creation of ICP & User Intelligence Dossier template.
