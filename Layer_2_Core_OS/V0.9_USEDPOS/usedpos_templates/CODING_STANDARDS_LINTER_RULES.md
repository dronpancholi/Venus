# Coding Standards and Linter Rules
**Document ID:** VENUS-STD-052
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Purpose
This document enforces consistent programming practices, architectural style, and automated quality gates for TypeScript, Python, Go, and Terraform within the Project Venus ecosystem.

## 2. Multi-Language Quality Metrics
To ensure high-performance, robust, and clean code, all projects must meet the following metrics:

| Metric | Target Threshold | Tooling Enforcement |
| :--- | :--- | :--- |
| **Cognitive Complexity** | Max 15 per function/method | SonarQube, ESLint |
| **Cyclomatic Complexity** | Max 10 per function/method | SonarQube, Ruff, GoCyclo |
| **Line Length Limit** | Max 120 characters | Prettier, Ruff, GoFmt |
| **Test Coverage** | Min 80% statement coverage | Istanbul/Jest, PyTest-Cov, Go Test |

### 2.1 Amdahl's Law for Performance Optimization
When optimizing code paths, developers must prioritize refactoring efforts based on Amdahl's Law:

$$S_{\text{latency}}(s) = \frac{1}{(1 - p) + \frac{p}{s}}$$

Where:
- $S_{\text{latency}}$ is the theoretical speedup of the entire task.
- $p$ is the proportion of execution time that the part benefiting from the improvement originally occupied.
- $s$ is the speedup factor of the part that has been improved.

*Example Calculation:* If a database query represents $60\%$ ($p = 0.6$) of a request's total duration, and we optimize that query to run 3x faster ($s = 3$):

$$S = \frac{1}{(1 - 0.6) + \frac{0.6}{3}} = \frac{1}{0.4 + 0.2} = 1.67\text{x Speedup}$$

Do not spend optimization efforts on code blocks where $p < 0.1$ unless critical for resource bottlenecks.

## 3. Configuration Specifications

### 3.1 ESLint Configuration (TypeScript/Node)
Create `.eslintrc.json` in the root of TypeScript repositories:
```json
{
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "plugins": ["@typescript-eslint", "import"],
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "complexity": ["error", 10],
    "max-lines-per-function": ["warn", 50]
  }
}
```

### 3.2 Ruff Configuration (Python)
Create `pyproject.toml` in the root of Python repositories:
```toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "C90"]
ignore = []

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

### 3.3 Go Configuration
Go files must be formatted with native `gofmt -s` and linted with `golangci-lint` configured as follows in `.golangci.yml`:
```yaml
linters-settings:
  gocognit:
    min-complexity: 15
  gocyclo:
    min-complexity: 10
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gocognit
    - gocyclo
```

### 3.4 Terraform Configuration
All Terraform modules must pass formatting check: `terraform fmt -check` and validation: `tflint`.

## 4. Cross-References
- [Repository Structure Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/REPOSITORY_STRUCTURE_STANDARD.md)
- [Pull Request Template](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/PULL_REQUEST_TEMPLATE.md)
