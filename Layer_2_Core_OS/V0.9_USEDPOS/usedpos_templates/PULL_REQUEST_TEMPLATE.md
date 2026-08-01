# Pull Request Template
<!-- Provide a general summary of your changes in the Title above using Conventional Commits naming standard -->

## Description
<!-- Describe your changes in detail. Why is this change required? What problem does it solve? -->
<!-- If it fixes an open issue, please link to the issue here: Closes #123 -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] CI/CD or Infrastructure modification

## Performance Impact Analysis (Amdahl's Law)
- [ ] No impact expected
- [ ] Performance optimization included (Complete metrics below)

*Metrics Detail:*
*   Estimated percentage of application path affected ($p$): ______ %
*   Estimated local speedup factor ($s$): ______ x
*   Calculated overall system speedup ($S = 1 / ((1 - p) + p / s)$): ______ x

## Quality Assurance Checklist
- [ ] My code follows the [Coding Standards and Linter Rules](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CODING_STANDARDS_LINTER_RULES.md).
- [ ] I have performed a self-review of my own code.
- [ ] I have commented my code, particularly in hard-to-understand areas.
- [ ] I have added unit tests that prove my fix is effective or that my feature works.
- [ ] New and existing unit tests pass locally with my changes.
- [ ] I have verified that static analysis (SonarQube) passes with zero blocker issues.
- [ ] All database migration scripts have rollback operations included and tested.

## Security Controls Checklist
- [ ] No hardcoded secrets or credentials are introduced in this PR.
- [ ] Inputs are sanitized and validated against SQL Injection / Cross-Site Scripting (XSS).
- [ ] Dependency vulnerabilities checked (`npm audit` / `pip-audit` / `govulncheck` clean).

## Screenshots / API Payloads (if applicable)
<!-- Add screenshots of UI changes or JSON payloads of API request/response modifications -->
