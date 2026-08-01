# Repository Structure Standard
**Document ID:** VENUS-STD-051
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This document defines the standardized repository structure for all software assets under Project Venus. Consistency across repositories is critical for automated CI/CD pipelines, security scanning, developer onboarding, and long-term maintainability.

## 2. Directory Layout Specification
All Project Venus repositories must strictly adhere to the following directory layout:

```text
/ (Repository Root)
├── .github/                  # CI/CD and VCS configuration
│   ├── workflows/            # GitHub Actions workflow YAML files
│   └── pull_request_template.md
├── docs/                     # Project-level documentation (Markdown)
│   ├── architecture/         # C4 Model diagrams and ADRs
│   └── api/                  # OpenAPI specs and contract definitions
├── src/                      # Application source code
│   ├── cmd/                  # Main application entry points
│   ├── config/               # Application configuration schemas and initializers
│   ├── domain/               # Domain models and business logic (core)
│   ├── infrastructure/       # Database adapters, API clients, external integrations
│   └── interfaces/           # REST controllers, gRPC handlers, UI components
├── tests/                    # Global test suites
│   ├── unit/                 # Unit tests matching src/ package structure
│   ├── integration/          # Integration tests (DB, Cache, External API)
│   └── e2e/                  # End-to-End browser/API test suites (Playwright)
├── deployments/              # Infrastructure and deployment code
│   ├── docker/               # Dockerfiles and Compose configurations
│   ├── terraform/            # Infrastructure as Code (Terraform modules)
│   └── kubernetes/           # K8s manifests and Helm charts
├── scripts/                  # Internal build, database migration, and helper scripts
├── README.md                 # Project entry-point documentation
├── CHANGELOG.md              # Version history tracking
├── LICENSE                   # Software license definition
├── package.json / go.mod     # Package manager dependency configurations
└── sonar-project.properties  # Static analysis configurations
```

## 3. Directory Descriptions

| Directory | Purpose | Strict Enforcement Rules |
| :--- | :--- | :--- |
| `/docs` | All project architecture designs using C4 Mapping Guidelines. | No binary documents (e.g., DOCX). Use Markdown and SVG/Mermaid only. |
| `/src` | Core source codebase. | No test files should be packaged in production builds. |
| `/tests` | Dedicated automated test directories. | Must separate unit, integration, and E2E to allow selective execution. |
| `/deployments` | Infrastructure as Code (IaC) and containerization configurations. | Hardcoded secrets are strictly prohibited. Use environment placeholders. |
| `/scripts` | Operational automation scripts. | Must specify shebangs (`#!/usr/bin/env bash` or `python3`) and be executable. |

## 4. C4 Architecture Mapping Guidelines
The architecture documentation inside `/docs/architecture/` must be mapped using the C4 model:
1. **Level 1: System Context Diagram** - Defines the boundary of the system and its interactions with users and other systems.
2. **Level 2: Container Diagram** - Details the high-level technical architecture (web app, database, API service).
3. **Level 3: Component Diagram** - Details the internal components of a single container (controllers, repositories, services).
4. **Level 4: Code Diagram** - Optional class/module relationships (generally auto-generated from code).

## 5. Cross-References
- [Coding Standards and Linter Rules](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CODING_STANDARDS_LINTER_RULES.md)
- [Contribution Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CONTRIBUTION_GUIDE.md)
- [Branching Strategy GitFlow](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/BRANCHING_STRATEGY_GITFLOW.md)
