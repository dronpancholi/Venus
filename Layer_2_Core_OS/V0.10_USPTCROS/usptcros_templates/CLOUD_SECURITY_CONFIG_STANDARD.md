# USPTCROS Cloud Security Config Standard
**Document Link:** [Cloud Security Config](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CLOUD_SECURITY_CONFIG_STANDARD.md)  
**References:** [Terraform Security Blueprint](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TERRAFORM_SECURITY_BLUEPRINT.md)

## 1. Cloud Baseline Configuration Rules
These standards enforce basic security posture across target cloud landing zones (GCP focus).
* **Metadata Protection:** Enforce Instance Metadata Service Version 2 (IMDSv2) or GCP metadata headers.
* **Storage Encryption:** All storage buckets must enforce Customer-Managed Encryption Keys (CMEK).
* **Logging:** Enable VPC Flow Logs, Cloud Audit Logs (Data Access + Admin Activity), and set retention to 365 days.

## 2. CIS Benchmark Auditing
Run automated CIS benchmarks tools monthly to verify compliance baseline configurations:
```bash
# Verify project-level compliance controls via security health logs
gcloud scc findings list --project=project-venus-prod --filter="category:COMPLIANCE_VIOLATION"
```
