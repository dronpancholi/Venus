# Mutation Testing Specification
**Document ID:** VENUS-STD-069
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Introduction
Mutation testing evaluates the quality of automated test suites by injecting minor faults ("mutants") into the source code and checking if existing tests fail ("kill") the mutant. If all tests pass, the mutant "survived," exposing gaps in assertion checks.

## 2. Mutation Score Formula
The system quality gate enforces a minimum Mutation Score of **75%** on core domain components, calculated as:

$$\text{Mutation Score} = \left( \frac{\text{Mutants Killed}}{\text{Total Mutants Created}} \right) \times 100$$

## 3. Mutation Testing Configuration

### 3.1 Stryker Mutator Configuration (`stryker.config.json`)
For Node.js and TypeScript services:
```json
{
  "$schema": "https://git.io/stryker-schema",
  "mutator": {
    "name": "typescript",
    "excludedMutations": ["BooleanLiteral", "StringLiteral"]
  },
  "packageManager": "npm",
  "reporters": ["html", "clear-text", "progress"],
  "testRunner": "jest",
  "coverageAnalysis": "perTest",
  "thresholds": {
    "high": 80,
    "low": 60,
    "break": 75
  }
}
```

### 3.2 Mutmut Configuration (`setup.cfg` / `tox.ini`)
For Python components, configure mutmut:
```ini
[mutmut]
paths_to_mutate=src/domain/
backup=false
runner=pytest
tests_dir=tests/unit/
```

## 4. Execution Command Reference
```bash
# Execute stryker locally
npx stryker run

# Execute mutmut locally
mutmut run
mutmut results
```

## 5. Cross-References
- [Unit Test Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/UNIT_TEST_SPECIFICATION.md)
- [Test Coverage Report](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TEST_COVERAGE_REPORT.md)
