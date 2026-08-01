# USPTCROS Database Storage Encryption Policy
**Document Link:** [Database Storage Encryption Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DATABASE_STORAGE_ENCRYPTION_POLICY.md)  
**References:** [Encryption Standards Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ENCRYPTION_STANDARDS_MATRIX.md), [Data Classification Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DATA_CLASSIFICATION_MATRIX.md)

Rules for encrypting database storage volumes.

## 1. Volume and Storage Cryptography
* All physical disks holding database files must utilize block-level disk encryption.
* Cloud SQL / Cloud Spanner: Enforce Customer-Managed Encryption Keys (CMEK) via Cloud KMS.
* Cache storage (Redis): Run persistence files on encrypted volumes.

## 2. GCP Cloud SQL CMEK Spec Configuration (Terraform Pattern)
```hcl
resource "google_sql_database_instance" "venus_database" {
  name             = "venus-db-instance"
  database_version = "POSTGRES_14"
  region           = "us-central1"
  
  # Bind KMS cryptokey for CMEK storage encryption
  encryption_key_name = "projects/project-venus-prod/locations/us-central1/keyRings/db-ring/cryptoKeys/db-storage-key"

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled    = false
      private_network = "projects/project-venus-prod/global/networks/venus-vpc"
    }
  }
}
```
