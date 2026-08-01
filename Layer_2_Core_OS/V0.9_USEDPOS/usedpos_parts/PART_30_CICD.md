# Part 30: CI/CD (Continuous Integration & Continuous Deployment)

## 1. Context & Strategy
CI/CD under Project Venus defines the automated pipeline governance system. It ensures that every code change undergoes strict linting, security scans, unit and integration tests, Docker image construction, and Kubernetes rollout execution. Delivery pipelines must be declarative, idempotent, and audit-logged.

---

## 2. Delivery Cycle Time & Pipeline Performance Metrics

### 2.1 Cycle Time Metric
Cycle Time ($CT$) measures the speed at which a code change transitions from initial commit to live production state:

$$CT = T_{production} - T_{commit}$$

*   *Standard Target*: The CI/CD pipeline must achieve $CT \le 15\text{ minutes}$ for standard service deployments, including all automated testing gates.

### 2.2 Pipeline Fail-Fast Ratio
To optimize developer cognitive cycles and pipeline compute costs, pipelines must validate cheaper checks (linting, static analysis) first. The pipeline efficiency score ($E_{pipe}$) is modeled as:

$$E_{pipe} = \sum_{s=1}^{S} \frac{F_s}{T_s}$$

Where:
*   $S$: Build pipeline stage index.
*   $F_s$: Historic probability of stage $s$ catching a failure.
*   $T_s$: Average execution time of stage $s$.
*   *Application*: Ordering static checks ($T_1 \approx 30\text{s}$, $F_1 \approx 0.6$) before integration tests ($T_3 \approx 8\text{m}$, $F_3 \approx 0.2$) maximizes the fail-fast ratio.

---

## 3. Pipeline Specifications & Automation

### 3.1 GitHub Actions Workflow Blueprint
This build configuration enforces testing, compilation, containerization, and publishing constraints.

```yaml
# .github/workflows/pipeline.yaml
name: Delivery Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.20'
          cache: true

      - name: Formatting Check
        run: go fmt ./... && git diff --exit-code

      - name: Run Tests
        run: go test -v -race -covermode=atomic -coverprofile=coverage.out ./...

  publish:
    needs: validate
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Google Artifact Registry
        uses: docker/login-action@v2
        with:
          registry: us-central1-docker.pkg.dev
          username: _json_key
          password: ${{ secrets.GCP_SA_KEY }}

      - name: Build and Push Image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: us-central1-docker.pkg.dev/project-venus-prod/app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 3.2 Deployment Status JSON Schema
Pipelines must report the result of execution runs according to this data structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PipelineDeploymentReport",
  "type": "object",
  "properties": {
    "commitHash": { "type": "string", "pattern": "^[a-f0-9]{40}$" },
    "pipelineStatus": { "type": "string", "enum": ["SUCCESS", "FAILED", "CANCELLED"] },
    "durationSeconds": { "type": "integer" },
    "coveragePercentage": { "type": "number", "minimum": 0.0, "maximum": 100.0 }
  },
  "required": ["commitHash", "pipelineStatus", "durationSeconds", "coveragePercentage"]
}
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that all code linters and formatting checks execute before building binaries.
*   [ ] Confirmed test steps run with race condition detectors (`-race`) active.
*   [ ] Verified that credentials and deployment tokens are fetched dynamically via OIDC instead of stored long-term API keys.
*   [ ] Checked that Docker build steps utilize remote cache actions to reduce execution time.
*   [ ] Confirmed that failed runs block code merges into protected master branches.
