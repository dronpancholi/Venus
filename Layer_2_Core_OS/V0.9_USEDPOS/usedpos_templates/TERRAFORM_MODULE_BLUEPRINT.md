# Terraform Module Blueprint
**Document ID:** VENUS-STD-078
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Scope
This blueprint establishes the standard design pattern for reusable infrastructure modules using HashiCorp Terraform. All module code must be organized into strict directories.

## 2. Directory Layout
```text
/my-terraform-module/
├── main.tf          # Resource creation definitions
├── variables.tf     # Input variables schemas and descriptions
├── outputs.tf       # Exported resource identifiers
├── providers.tf     # Pin provider versions
└── README.md        # Usage instructions and documentation
```

## 3. Terraform Module Code Templates

### 3.1 `main.tf`
```hcl
# Create target storage resource
resource "google_storage_bucket" "venus_bucket" {
  name          = var.bucket_name
  location      = var.gcp_region
  project       = var.gcp_project_id
  force_destroy = var.force_destroy_enabled

  uniform_bucket_level_access = true

  versioning {
    enabled = var.versioning_enabled
  }

  encryption {
    default_kms_key_name = var.kms_key_link
  }

  labels = {
    environment = var.environment_label
    managed_by  = "terraform"
    project     = "venus"
  }
}
```

### 3.2 `variables.tf`
```hcl
variable "bucket_name" {
  type        = string
  description = "Unique bucket identifier name"
}

variable "gcp_region" {
  type        = string
  default     = "us-central1"
  description = "Target geographical location for bucket deployment"
}

variable "gcp_project_id" {
  type        = string
  description = "GCP Project Identifier"
}

variable "force_destroy_enabled" {
  type        = bool
  default     = false
  description = "If true, allows destroying bucket with contents"
}

variable "versioning_enabled" {
  type        = bool
  default     = true
  description = "Maintains revision history changes of objects"
}

variable "kms_key_link" {
  type        = string
  description = "The KMS key Resource URI link to encrypt data"
}

variable "environment_label" {
  type        = string
  description = "Deployment tag environment (dev, staging, prod)"
}
```

### 3.3 `outputs.tf`
```hcl
output "bucket_url" {
  value       = google_storage_bucket.venus_bucket.url
  description = "URI identifier link of bucket"
}

output "bucket_name" {
  value       = google_storage_bucket.venus_bucket.name
  description = "Configured name identifier of the storage bucket"
}
```

## 4. Cross-References
- [Terraform State Locking Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TERRAFORM_STATE_LOCKING_POLICY.md)
