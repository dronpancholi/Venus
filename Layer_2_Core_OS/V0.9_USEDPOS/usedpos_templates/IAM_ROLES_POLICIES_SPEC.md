# IAM Roles and Policies Specification
**Document ID:** VENUS-STD-085
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Security Philosophy
We enforce the Principle of Least Privilege (PoLP). No entity (service account, container, developer) shall possess authorizations beyond the minimal scope required to fulfill its function.

## 2. Policy Definitions

### 2.1 GCP IAM Service Account Keyless Mapping Configuration
GCP Cloud services bind identities utilizing Workload Identity Federation. Do not distribute JSON credentials to pods.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "accounts.google.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "accounts.google.com:sub": "system:serviceaccount:venus-prod:venus-application-sa"
        }
      }
    }
  ]
}
```

### 2.2 AWS IAM S3 + Secrets Manager Policy Blueprint
For microservices requiring access to configuration storage and encrypted settings:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBucketMetadataRead",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::venus-application-assets"
    },
    {
      "Sid": "AllowObjectReadAndWriteOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::venus-application-assets/user-uploads/*"
    },
    {
      "Sid": "AllowDatabaseSecretRetrieval",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:venus-db-secrets-*"
    }
  ]
}
```

## 3. Governance Audit Schedule
IAM permissions are scanned monthly. Any role possessing permissions like `*` or `AdminAccess` in production without a written waiver will be automatically flagged for removal.

## 4. Cross-References
- [Secrets Management Vault Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/SECRETS_MANAGEMENT_VAULT_POLICY.md)
