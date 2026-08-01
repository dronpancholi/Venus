# ENGINE — Terraform Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates complete, production-grade Terraform infrastructure-as-code for any cloud environment. Applies modular design, remote state management, environment separation, and all VENUS IaC standards.

---

## Input Requirements
```
Required:
  - Cloud provider (AWS / GCP / Azure)
  - Target environment (dev / staging / prod)
  - Services to provision (compute, database, cache, networking)
  - Region and availability zone requirements
  - Compliance requirements (SOC2, HIPAA, PCI-DSS)

Optional:
  - Existing VPC/network to integrate with
  - Cost optimization targets
  - Multi-region requirements
```

---

## Generated Structure
```
terraform/
├── modules/
│   ├── vpc/           # Network topology
│   ├── eks/           # Kubernetes cluster
│   ├── rds/           # PostgreSQL database
│   ├── elasticache/   # Redis cache
│   ├── s3/            # Object storage
│   └── secrets/       # Secrets Manager
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── global/
│   ├── iam/           # IAM roles and policies
│   └── route53/       # DNS management
└── backend.tf         # Remote state (S3 + DynamoDB lock)
```

---

## Generated Module Standards

### Remote State Backend
```hcl
terraform {
  backend "s3" {
    bucket         = "{org}-terraform-state"
    key            = "{service}/{environment}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "{org}-terraform-locks"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.6.0"
}
```

### Module Pattern
```hcl
# modules/rds/main.tf
resource "aws_db_instance" "main" {
  identifier     = "${var.service_name}-${var.environment}"
  engine         = "postgres"
  engine_version = var.postgres_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_encrypted     = true
  kms_key_id           = var.kms_key_arn

  multi_az               = var.environment == "prod" ? true : false
  deletion_protection    = var.environment == "prod" ? true : false
  skip_final_snapshot    = var.environment == "prod" ? false : true
  backup_retention_period = var.environment == "prod" ? 30 : 7

  performance_insights_enabled = true
  monitoring_interval          = 60

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  tags = local.common_tags
}
```

---

## Security Standards Applied
- All storage encrypted at rest (KMS)
- All traffic encrypted in transit (SSL)
- No public IP on databases or caches
- Security groups with minimal ingress/egress rules
- VPC flow logs enabled in production
- CloudTrail enabled for all API calls
- IAM roles with least-privilege policies
- MFA delete on S3 state buckets
