# Project Venus USPTCROS — Part 05: PASTA Threat Modeling

## 1. Executive Summary
The Process for Attack Simulation and Threat Analysis (PASTA) is a risk-centric threat modeling methodology. It provides a structured process to align security mitigations directly with business objectives and asset impacts.

## 2. The Seven Stages of PASTA
```
+-----------------------------------------------------------------+
| Stage 1: Define Objectives (Business context & compliance)      |
+-----------------------------------------------------------------+
                               │
                               ▼
+-----------------------------------------------------------------+
| Stage 2: Define Technical Scope (Asset inventory & boundaries)  |
+-----------------------------------------------------------------+
                               │
                               ▼
+-----------------------------------------------------------------+
| Stage 3: Decomposition (Data flow diagrams & functional code)   |
+-----------------------------------------------------------------+
                               │
                               ▼
+-----------------------------------------------------------------+
| Stage 4: Threat Analysis (Threat intelligence & log parsing)    |
+-----------------------------------------------------------------+
                               │
                               ▼
+-----------------------------------------------------------------+
| Stage 5: Vulnerability & Weakness Analysis (Static/Dynamic scans)|
+-----------------------------------------------------------------+
                               │
                               ▼
+-----------------------------------------------------------------+
| Stage 6: Attack Modeling & Simulation (Penetration testing)    |
+-----------------------------------------------------------------+
                               │
                               ▼
+-----------------------------------------------------------------+
| Stage 7: Risk & Impact Analysis (Mitigation & residual risk)    |
+-----------------------------------------------------------------+
```

---

## 3. Mathematical Risk Analysis in PASTA
To assess the final risk $R_i$ for a threat $i$:
$$R_i = P_i \times I_i$$
Where:
- $P_i$ is the probability of threat execution, calculated as:
  $$P_i = \omega_1 \cdot \text{Exploitability} + \omega_2 \cdot \text{Actor Capability}$$
- $I_i$ is the operational and financial impact on the business.
- $\omega_1, \omega_2$ are weights assigned to the system environment (typically $\omega_1 = 0.6, \omega_2 = 0.4$).

---

## 4. Verification Checklists for PASTA

### Stage 1 Checklist: Define Objectives
- [ ] Document all business objectives and compliance mandates (GDPR, SOC2, HIPAA).
- [ ] Determine risk tolerance limits for system unavailability.

### Stage 2 Checklist: Define Technical Scope
- [ ] Create a full inventory of microservices, databases, and third-party SaaS integration endpoints.
- [ ] Audit host infrastructure, cloud provider boundaries, and ingress/egress firewalls.

### Stage 3 Checklist: Decomposition
- [ ] Map high-fidelity Data Flow Diagrams (DFDs).
- [ ] Document protocol details, APIs, payload structures, and trust boundaries.

### Stage 4 Checklist: Threat Analysis
- [ ] Gather log intelligence and map potential attack vectors to known intelligence feeds.
- [ ] Enumerate threat actors (insiders, nation-states, automated scrapers).

### Stage 5 Checklist: Vulnerability Analysis
- [ ] Perform Static Application Security Testing (SAST) and Software Composition Analysis (SCA).
- [ ] Enumerate Common Vulnerabilities and Exposures (CVEs) and Common Weakness Enumerations (CWEs).

### Stage 6 Checklist: Attack Simulation
- [ ] Conduct vulnerability verification and execute automated penetration testing scripts.
- [ ] Map vulnerabilities to feasible attack paths (Attack Trees).

### Stage 7 Checklist: Risk & Impact Analysis
- [ ] Quantify business impact of compromised components.
- [ ] Define remediations and formally document residual risks.

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 04: STRIDE](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_04_STRIDE.md)
- **Next Chapter**: [Part 06: Attack Trees](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_06_ATTACK_TREES.md)
