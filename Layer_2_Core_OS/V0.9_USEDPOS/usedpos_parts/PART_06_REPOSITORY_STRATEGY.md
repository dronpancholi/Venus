# PART 06 — Repository Strategy
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Repository Strategy defines how source code is organized across teams, services, and products. The choice of repository structure has profound implications for developer velocity, CI/CD pipeline design, dependency management, code reuse, and organizational autonomy. VENUS defines a principled, evidence-based approach to repository topology.

---

## 2. Repository Models

### 2.1 Monorepo
A single repository containing multiple projects, services, libraries, and applications.

**Characteristics**:
- Unified versioning and dependency graph
- Atomic cross-service changes in a single PR
- Shared tooling, linting, and CI configuration
- Requires investment in build tooling (Nx, Turborepo, Bazel)
- Single source of truth for all code

**Adopted by**: Google (Piper), Meta (fbsource), Microsoft (One Engineering System), Stripe, Airbnb

**Best suited for**:
- Platform teams with strong shared libraries
- Tightly coupled services that version together
- Organizations with strong engineering platform investment
- Teams < 500 engineers

### 2.2 Polyrepo
Multiple independent repositories, one per service or domain.

**Characteristics**:
- Full team autonomy per repository
- Independent release cycles per service
- Simpler CI/CD per repository
- Cross-repo changes require coordinated PRs
- Dependency drift risk across repositories

**Best suited for**:
- Genuinely independent services with separate deployment cadences
- Large organizations with separate product lines
- Teams > 500 engineers with strong platform maturity

### 2.3 Hybrid (VENUS Default)
Domain-scoped monorepos with cross-domain polyrepo boundaries.

```
organization/
├── platform-monorepo/         # Shared libraries, design system, SDKs
├── core-services-monorepo/    # Core domain services (Order, Billing, Identity)
├── data-platform-monorepo/    # Data pipelines, ML infrastructure
└── frontend-monorepo/         # All frontend applications
```

---

## 3. Repository Naming Conventions

| Type | Pattern | Example |
|---|---|---|
| Monorepo | `{org}-{domain}` | `acme-core`, `acme-platform` |
| Service Repo | `{domain}-{service}-service` | `billing-invoice-service` |
| Library Repo | `{org}-{name}-lib` | `acme-ui-lib` |
| Infrastructure Repo | `{org}-infra` | `acme-infra` |
| Documentation Repo | `{org}-docs` | `acme-docs` |

---

## 4. Repository Structure Standard

### 4.1 Service Repository Structure
```
service-name/
├── src/                        # Source code
│   ├── domain/                 # Domain layer
│   ├── application/            # Application layer
│   ├── infrastructure/         # Infrastructure layer
│   └── shared/                 # Shared utilities
├── tests/                      # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                       # Documentation
│   ├── architecture/
│   ├── api/
│   └── runbooks/
├── k8s/                        # Kubernetes manifests
├── terraform/                  # Infrastructure as code
├── .github/                    # GitHub Actions workflows
│   └── workflows/
├── scripts/                    # Development and deployment scripts
├── Dockerfile
├── docker-compose.yml          # Local development
├── .env.example                # Environment variable template
├── package.json / pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── CODEOWNERS
```

### 4.2 CODEOWNERS Policy
Every file must have a defined owner. No orphaned code.

```
# CODEOWNERS
*                           @org/platform-team         # Default owner
src/domain/                 @org/domain-experts
src/infrastructure/         @org/platform-engineers
k8s/                        @org/sre-team
terraform/                  @org/infra-team
```

---

## 5. Repository Access Control

| Role | Permissions |
|---|---|
| **Owner** | Full admin: create, delete, configure branch protection |
| **Maintainer** | Merge PRs, manage settings, review code |
| **Developer** | Push to feature branches, open PRs |
| **Reviewer** | Approve PRs, read access |
| **Read** | Clone, view code, read issues |

---

## 6. Repository Health Metrics

Repositories are evaluated weekly against these metrics:

| Metric | Target | Alert Threshold |
|---|---|---|
| Mean Time to Merge PR | < 2 business days | > 5 business days |
| Open PR count | < 10 | > 25 |
| Open bug issues (P0/P1) | 0 | > 3 |
| Test coverage | ≥ 85% | < 70% |
| Build success rate | ≥ 99% | < 95% |
| Stale branches (> 30 days) | 0 | > 5 |

---

## 7. Repository Lifecycle

```
Creation → Active Development → Maintenance → Deprecation → Archival → Deletion
```

| Phase | Definition |
|---|---|
| **Creation** | Templated from VENUS repository template; CODEOWNERS defined |
| **Active** | Regular commits; all health metrics green |
| **Maintenance** | Bug fixes only; no new features |
| **Deprecation** | Notice period: 90 days minimum; consumers notified |
| **Archival** | Read-only; accessible for 2 years |
| **Deletion** | Only with VP Engineering sign-off |
