# Developer Contribution Guide
**Document ID:** VENUS-STD-053
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Introduction
Welcome to Project Venus! This guide outlines the standard onboarding process, code checkout, local development setup, testing, and contribution protocols required for developers.

## 2. Developer Onboarding and Access Setup
To begin contributing:
1. Obtain access to the GitHub/GitLab organization from your Engineering Lead.
2. Configure your local Git client with a signed SSH key:
   ```bash
   git config --global user.name "First Last"
   git config --global user.email "yourname@projectvenus.org"
   git config --global commit.gpgsign true
   ```
3. Request credentials to the target AWS/GCP environment using the IAM request protocol.

## 3. Standard Local Development Workflow
Follow these steps to set up your local workspace:

### 3.1 Clone and Setup
```bash
# Clone the repository
git clone git@github.com:venus-org/core-platform.git
cd core-platform

# Initialize dependencies (Node.js example)
npm ci

# Initialize local environment variables
cp .env.example .env
```

### 3.2 Run and Test Locally
Ensure all pre-commit hooks are active:
```bash
# Install husky hooks (if using JS/TS)
npx husky install

# Run linters
npm run lint

# Run unit tests
npm run test:unit
```

## 4. Commit Message Standard
Project Venus strictly enforces the **Conventional Commits** specification. Commit messages must follow this structure:
```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 4.1 Allowed Types
* `feat`: A new user-facing feature.
* `fix`: A bug fix.
* `docs`: Documentation changes only.
* `style`: Code style changes (whitespace, formatting, missing semi-colons).
* `refactor`: Code changes that neither fix a bug nor add a feature.
* `test`: Adding missing tests or correcting existing tests.
* `chore`: Build system changes, package dependency updates, CI workflows.

### 4.2 Example Commits
* `feat(auth): add OAuth2 provider authentication`
* `fix(db): resolve deadlock during batch transaction inserts`
* `docs(readme): correct relative path for setup manual`

## 5. Cross-References
- [Branching Strategy GitFlow](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/BRANCHING_STRATEGY_GITFLOW.md)
- [Pull Request Template](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/PULL_REQUEST_TEMPLATE.md)
