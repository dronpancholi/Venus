# Template: Infrastructure Blueprint

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Infra ID**: INF-BLU-[UUID]
*   **Last Updated**: [Date]

---

## 2. Infrastructure as Code (Terraform Skeletons)
*Provide a skeleton schema mapping target resources.*

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "venus-vpc"
  }
}

resource "aws_security_group" "db" {
  name        = "db-security-group"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.1.0/24"] # API subnet only
  }
}
```

---

## 3. Provisioned Resources Inventory
*   **VPC Class**: `10.0.0.0/16`
*   **Database Node**: `db.r6g.large` (Aurora Postgres compatibility).
*   **Cache Instance**: `cache.t4g.micro` (Redis single node).

---

## 4. Safety & IAM Configurations
*   [ ] Disabled public database access parameters.
*   [ ] Configured AWS secrets manager rotation rules.
*   [ ] Checked subnet CIDR allocations.
