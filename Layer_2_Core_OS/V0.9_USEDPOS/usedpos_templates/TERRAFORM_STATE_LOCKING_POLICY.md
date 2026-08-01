# Terraform State and Locking Policy
**Document ID:** VENUS-STD-079
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This policy details the management, security configurations, and disaster recovery processes for Terraform state files (`.tfstate`). State locks prevent concurrent executions from causing state corruption.

## 2. Remote Backend State Configuration

### 2.1 GCP Cloud Storage Backend (`backend.tf`)
For platforms deploying on Google Cloud Platform (GCP):
```hcl
terraform {
  backend "gcs" {
    bucket      = "venus-tf-state-storage"
    prefix      = "env/production"
    credentials = "/secrets/gcp-tf-service-account.json"
  }
}
```

### 2.2 AWS S3 + DynamoDB State Backend (`backend.tf`)
For platforms deploying on Amazon Web Services (AWS):
```hcl
terraform {
  backend "s3" {
    bucket         = "venus-tf-state-storage-s3"
    key            = "global/s3/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "venus-tf-state-locks-db"
    encrypt        = true
  }
}
```

## 3. Security Requirements
1. **Access Isolation:** Only Jenkins/GitHub runner service accounts have read/write access to state buckets. Developers have Read-Only roles.
2. **Encryption:** State buckets must enforce server-side encryption with KMS customer-managed keys.
3. **Versioning:** The backend bucket must maintain at least 90 days of version history to allow rollbacks during state failures.

## 4. Disaster Recovery of Terraform State
If a Terraform state is corrupted:
1. Locate the last working state version in the bucket history.
2. Copy the state version to a local scratch file `state_backup.tfstate`.
3. Push the state file back to the remote backend:
   ```bash
   terraform state push state_backup.tfstate
   ```
4. If a state lock is stuck during a crashed process:
   ```bash
   # Identify Lock ID from error logs
   terraform force-unlock <LOCK_ID>
   ```

## 5. Cross-References
- [Terraform Module Blueprint](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TERRAFORM_MODULE_BLUEPRINT.md)
