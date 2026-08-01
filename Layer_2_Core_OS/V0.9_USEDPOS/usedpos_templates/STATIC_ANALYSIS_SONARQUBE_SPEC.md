# Static Analysis SonarQube Specification
**Document ID:** VENUS-STD-058
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This specification details the SonarQube Quality Gate rules and parameters applied to all Project Venus repositories to enforce automated static code analysis checks during CI/CD execution.

## 2. Quality Gate Thresholds
Every pipeline run must evaluate the code base against the Quality Gate thresholds. Failing any parameter fails the CI job.

| Metric | Target Threshold | Description |
| :--- | :--- | :--- |
| **New Bugs** | 0 | Zero new bugs introduced in the Pull Request changes. |
| **New Vulnerabilities** | 0 | Zero security vulnerabilities introduced in the PR. |
| **Security Hotspots Reviewed** | 100% | All security hotspots identified in new code must be reviewed and resolved. |
| **Technical Debt Ratio** | < 5.0% | Tech debt must not exceed 5% of total development scope. |
| **Coverage on New Code** | >= 80.0% | Statement coverage of the modified/added lines. |
| **Duplicated Lines on New Code**| < 3.0% | Copy-paste code duplicate percentage. |

## 3. Configuration Specification (`sonar-project.properties`)
Put this file in the root of each repository to configure the SonarQube Scanner:

```properties
# Metadata
sonar.projectKey=venus-platform-core
sonar.projectName=Project Venus Core Platform
sonar.projectVersion=1.0.0

# Paths
sonar.sources=src
sonar.tests=tests
sonar.exclusions=src/interfaces/ui/assets/**,node_modules/**,dist/**,deployments/**
sonar.test.inclusions=tests/**/*.test.ts,tests/**/*.spec.ts

# Coverage reports paths
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.typescript.tsconfigPath=tsconfig.json

# Quality Gate Settings (Override defaults if required)
sonar.qualitygate.wait=true
```

## 4. CI Pipeline Command Reference
To execute SonarQube scan locally or in CI runner:
```bash
sonar-scanner \
  -Dsonar.host.url=https://sonarqube.venus.internal \
  -Dsonar.token=${{ secrets.SONAR_TOKEN }}
```

## 5. Cross-References
- [Coding Standards and Linter Rules](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CODING_STANDARDS_LINTER_RULES.md)
- [Tech Debt Register](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TECH_DEBT_REGISTER.md)
