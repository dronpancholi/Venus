# ENGINE — CI/CD Builder
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates complete CI/CD pipeline definitions for any service. Produces GitHub Actions, GitLab CI, or CircleCI configurations with all quality gates, security checks, multi-environment promotion, and deployment automation applied by default.

---

## Pipeline Architecture

```
[PR Opened]
    │
    ▼
[PR Validation Pipeline]
  ├── Lint & Format Check
  ├── Type Check
  ├── Unit Tests + Coverage Gate
  ├── Security Scan (SAST + Secrets)
  ├── Dependency Audit
  ├── Build Validation
  └── Contract Tests
    │
    ▼ [All checks green + PR approved]
[Merge to Main]
    │
    ▼
[CI Pipeline]
  ├── Full Test Suite
  ├── Integration Tests
  ├── Build Docker Image (tagged with git SHA)
  ├── Push to Container Registry
  ├── Container Security Scan (Trivy)
  └── Generate SBOM
    │
    ▼
[Deploy to Staging]
  ├── Terraform Apply (if infra changes)
  ├── Database Migrations (dry-run first)
  ├── Kubernetes Rolling Deploy
  ├── Smoke Tests
  └── E2E Test Suite
    │
    ▼ [All staging checks pass]
[Deploy to Production] (automated or approval gate)
  ├── Database Migrations (backward-compatible)
  ├── Kubernetes Rolling Deploy (maxUnavailable: 0)
  ├── Smoke Tests
  ├── 10-minute canary monitoring window
  └── Automatic rollback if error rate spikes
```

---

## Generated GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  validate:
    name: Validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm type-check
      - run: pnpm test:unit --coverage
      - uses: codecov/codecov-action@v4
      - run: pnpm audit --prod
      - uses: gitleaks/gitleaks-action@v2

  build:
    name: Build & Scan
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,format=long
      - uses: docker/build-push-action@v5
        id: build
        with:
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.tags }}
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

  deploy-staging:
    name: Deploy to Staging
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: kubectl set image deployment/{service} {service}={image} -n {namespace}
      - run: kubectl rollout status deployment/{service} -n {namespace}
      - run: pnpm test:smoke --env=staging

  deploy-production:
    name: Deploy to Production
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.{domain}.com
    runs-on: ubuntu-latest
    steps:
      - run: kubectl set image deployment/{service} {service}={image} -n {namespace}
      - run: kubectl rollout status deployment/{service} -n {namespace}
      - run: pnpm test:smoke --env=production
```

---

## Deployment Strategies Supported
- **Rolling Update**: Zero-downtime, gradual pod replacement
- **Blue-Green**: Traffic switch via Kubernetes service selector
- **Canary**: Argo Rollouts with incremental traffic splitting
- **GitOps**: ArgoCD/Flux CD for declarative deployment

---

## Gates & Quality Thresholds
| Gate | Threshold | Action on Fail |
|---|---|---|
| Unit tests | 100% pass | Block deploy |
| Coverage | ≥ 85% | Block deploy |
| Critical CVEs | 0 | Block deploy |
| High CVEs | 0 | Block deploy |
| Smoke tests | 100% pass | Auto rollback |
| Error rate post-deploy | < 1% | Auto rollback |
