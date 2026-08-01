# USPTCROS Role Definition Catalog
**Document Link:** [Role Definition Catalog](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ROLE_DEFINITION_CATALOG.md)  
**Matrix Reference:** [RBAC Permissions Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/RBAC_PERMISSIONS_MATRIX.md)

## 1. Role Descriptions & Scope

### Role: SuperAdmin
* **Description:** Access to all system resources. Full control over system orchestration, keys, and network architectures.
* **Justification:** Required for catastrophic system recovery and initial provisioning operations.
* **Access Scope:** Global wildcard permissions (`*:*`).

### Role: SecurityAdmin
* **Description:** Configuration of security boundaries, encryption settings, IAM controls, and WAF endpoints.
* **Justification:** Separation of duties from day-to-day operators.
* **Access Scope:** Cryptographic management, network configuration, security logs.

### Role: Operator
* **Description:** Executes standard application deployments, system monitoring, and database management.
* **Justification:** Basic operational duties. Cannot manipulate HSM keys or network routing configurations.
* **Access Scope:** Read/Write access on application namespace.

### Role: ReadOnly
* **Description:** Auditing and performance monitoring access.
* **Justification:** Compliance reporting.
* **Access Scope:** Read access to metrics and non-PII audit endpoints.
