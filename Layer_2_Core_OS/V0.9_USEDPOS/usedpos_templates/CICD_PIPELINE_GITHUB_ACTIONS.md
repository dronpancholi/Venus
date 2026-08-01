# CI/CD Pipeline GitHub Actions Specification
**Document ID:** VENUS-STD-091
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This specification details the unified GitHub Actions CI/CD configuration standard used by all Project Venus repositories to automate compilation, testing, static analysis, image packaging, and deployments.

## 2. Pipeline Configuration Template (`pipeline.yaml`)
Put this configuration in `.github/workflows/pipeline.yaml`:

```yaml
name: Core Platform CI/CD Pipeline

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  id-token: write

jobs:
  # Quality Assurance phase
  qa_validation:
    name: Lint & Test Verification
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Codebase
        uses: actions/checkout@v4

      - name: Initialize Node.js Environment
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Project Dependencies
        run: npm ci

      - name: Run Linters (ESLint / Prettier)
        run: npm run lint

      - name: Execute Unit and Integration Tests
        run: npm run test:coverage

      - name: Execute SonarQube Scanner Analysis
        uses: sonarsource/sonarqube-scan-action@v2
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: https://sonarqube.venus.internal

  # Dockerize and Package phase
  docker_packaging:
    name: Container Build & Push
    needs: qa_validation
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Codebase
        uses: actions/checkout@v4

      - name: Authenticate with Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'venus-ci-builder@project-venus.iam.gserviceaccount.com'

      - name: Configure Docker credentials
        run: gcloud auth configure-docker gcr.io --quiet

      - name: Compile and Push Container Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: gcr.io/project-venus/core-service:${{ github.sha }}

  # Deployment phase
  cd_deployment:
    name: Cluster Deployment
    needs: docker_packaging
    runs-on: ubuntu-latest
    steps:
      - name: Authenticate with Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'venus-ci-builder@project-venus.iam.gserviceaccount.com'

      - name: Configure GKE Credentials
        uses: google-github-actions/get-gke-credentials@v2
        with:
          cluster_name: venus-prod-cluster
          location: us-central1

      - name: Update deployment manifest
        run: |
          sed -i "s|image: gcr.io/project-venus/core-service:.*|image: gcr.io/project-venus/core-service:${{ github.sha }}|g" deployments/kubernetes/deployment.yaml

      - name: Deploy Manifest to K8s
        run: |
          kubectl apply -f deployments/kubernetes/deployment.yaml
          kubectl rollout status deployment/venus-core-service -n venus-prod
```

## 3. Cross-References
- [Coding Standards and Linter Rules](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CODING_STANDARDS_LINTER_RULES.md)
- [Kubernetes Deployment Manifest](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_DEPLOYMENT_MANIFEST.md)
