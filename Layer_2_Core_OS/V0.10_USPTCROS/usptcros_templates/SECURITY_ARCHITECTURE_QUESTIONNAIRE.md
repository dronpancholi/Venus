# USPTCROS Security Architecture Questionnaire
**Document Link:** [Security Architecture Questionnaire](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURITY_ARCHITECTURE_QUESTIONNAIRE.md)

Standard questionnaire for assessing system architecture designs against security parameters.

## 1. Identity & Access Control
* **Q1.1:** How are users authenticated (e.g. OIDC federated provider)?
* **Q1.2:** Is MFA enforced for all privileges? What factors are allowed?
* **Q1.3:** How are microservices authorized to communicate with other backend services?

## 2. Data Protection & Cryptography
* **Q2.1:** What encryption standard is used at rest? Are keys managed in HSM?
* **Q2.2:** What TLS version is configured for web connections? Are older ciphers disabled?
* **Q2.3:** Where is the data masked, and how is raw data separated from processing nodes?

## 3. System Boundary & Isolation
* **Q3.1:** Draw or describe the trust boundary boundaries. Which ports cross these boundaries?
* **Q3.2:** How is malicious traffic mitigated at the perimeter edge (WAF, IP Whitelisting)?
* **Q3.3:** How are databases protected from direct microservice access (DB Proxies, IAM)?
