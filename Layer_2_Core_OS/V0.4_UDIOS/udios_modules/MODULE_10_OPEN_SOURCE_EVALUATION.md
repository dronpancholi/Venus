# Module 10 — Open Source Evaluation

## 1. Context & Strategy

### 1.1 Purpose
The Open Source Evaluation module rates the health, licensing safety, security profile, and activity of open-source packages before they are approved for deployment.

### 1.2 Philosophy
Importing a dependency is importing someone else's code. We evaluate package health to avoid abandoned packages, security vulnerabilities, or license compliance failures.

---

## 2. Ingest Parameters & Scoring Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Package name and repository URL.
*   **Outputs**: Open Source Health Score (OSHS) and license compliance certificate.

### 2.2 Scoring Taxonomy
Packages are scored from 0 to 100 based on four indicators:
*   **License Class (x0.3)**: Permissive (MIT/Apache2 = 100), Copyleft (GPLv3 = 20), AGPL (0).
*   **Maintenance Activity (x0.3)**: Commits in past 90 days, active maintainer count.
*   **Community Footprint (x0.2)**: Open issues/PR ratio, stars count.
*   **Security Health (x0.2)**: Number of outstanding CVEs, patch frequency.

---

## 3. Operational Algorithm & Decision Tree

### 3.1 The OSHS Algorithm
\[OSHS = (License\_Score \times 0.3) + (Maintenance\_Score \times 0.3) + (Community\_Score \times 0.2) + (Security\_Score \times 0.2)\]

### 3.2 Decision Tree logic
```
                          [Evaluate OSHS]
                                 │
                     [Is License Permissive?]
                     ├── NO  ──► [Reject Package: License Blocked]
                     └── YES ──► [Check OSHS Score]
                                       ├── OSHS >= 70 ──► [Approve Package]
                                       └── OSHS < 70  ──► [Block; Require Review]
```

---

## 4. Reusable Templates & Checklists

### 4.1 Template: Dependency Vetting Record
```markdown
### 1. Dependency Profile
*   **Package Name**: [e.g., celery]
*   **License**: BSD-3-Clause (Permissive) | **Score**: 100
*   **Outstanding CVEs**: 0 | **Score**: 100
*   **Last Commit**: 3 days ago | **Score**: 90
*   **Calculated OSHS**: **97.0** (Approved)
```

### 4.2 Checklist
*   [ ] Checked package license text.
*   [ ] Searched CVE database for known vulnerabilities.
*   [ ] Checked commit history on main branch.
*   [ ] Checked open issue counts and resolutions.

---

## 5. SRE, AI-Agent, & Safety Parameters

### 5.1 AI-Agent Execution Instructions
1.  **Parse**: Read `package.json` or `requirements.txt` changes in PRs.
2.  **API Call**: Query npm/PyPI APIs and GitHub repos to fetch OSHS inputs.
3.  **Gate**: Block PR merge if OSHS is below 70.

### 5.2 Common Anti-patterns
*   *The "Abandoned Helper" Trap*: Importing single-utility packages (e.g. `left-pad`) that haven't been committed to in 5 years, increasing security attack surface.

### 5.3 Exit Criteria
*   Dependency Vetting Record completed and **OSHS approved**.
*   Proceed to **Module 11: Vendor Evaluation**.
