# Part 27: Infrastructure as Code (IaC)

## 1. Context & Strategy
Infrastructure as Code (IaC) under Project Venus mandates that all physical and logical resources—servers, databases, network rules, IAM policies, and DNS entries—must be defined declaratively in Terraform. Manual resource management through cloud consoles is strictly prohibited. State files must be locked, code must be linted and scanned, and drift must be automatically reconciled.

---

## 2. IaC Drift & Reliability Mathematics

### 2.1 Infrastructure Drift Score
Drift occurs when the real-world state of a resource diverges from the declared configuration. The Drift Index ($DI$) measures compliance:

$$DI = \frac{N_{drifted}}{N_{total}} \times 100$$

Where:
*   $N_{drifted}$: Number of resources identified as modified, added, or deleted outside IaC pipelines during a plan run.
*   $N_{total}$: Total count of declared resources in state.
*   *Requirement*: The system must trigger immediate warnings if $DI > 0\%$. Production environments must maintain $DI = 0\%$.

### 2.2 Shared Resource Dependency Risk Score
To minimize the impact of failures during Terraform runs, states must be split (decoupled). The Risk Score ($R_{state}$) of a state file is defined by the number of resources ($N$) and external references ($Ref_{ext}$):

$$R_{state} = N \times (Ref_{ext} + 1)$$

*   Keep $R_{state} \le 150$ per workspace by splitting networking, database, and application runtime layers.

---

## 3. Terraform Lifecycle & Configuration Standards

### 3.1 Backend Configuration with GCS State Locking
State files must be stored in secure bucket systems with active versioning and locking mechanisms.

```tf
# providers.tf
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.80.0"
    }
  }
  backend "gcs" {
    bucket      = "venus-tf-state-prod"
    prefix      = "terraform/state/application-layer"
  }
}

provider "google" {
  project = "project-venus-prod"
  region  = "us-central1"
}
```

### 3.2 Resource Metadata & Tagging Schema
All resources must define a standardized set of labels to track cost allocations and ownership.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TerraformResourceMetadata",
  "type": "object",
  "properties": {
    "labels": {
      "type": "object",
      "properties": {
        "environment": { "type": "string", "enum": ["dev", "staging", "prod"] },
        "cost-center": { "type": "string" },
        "owner": { "type": "string" },
        "service-name": { "type": "string" }
      },
      "required": ["environment", "cost-center", "owner", "service-name"]
    }
  },
  "required": ["labels"]
}
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that states are decoupled into logical modules (e.g., Network, DB, App).
*   [ ] Confirmed state versioning is enabled on GCS buckets.
*   [ ] Verified Terraform formatting (`terraform fmt -check`) passes validation.
*   [ ] Checked that security scanners (e.g., `tfsec`, `trivy`) run on code before execution.
*   [ ] Verified no secret variables or tokens are committed or stored in plaintext inside `.tfvars`.
