# PART 02 — Software Engineering Principles
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Software Engineering Principles are the operational rules derived from Engineering Philosophy (Part 01). Where philosophy defines *why*, principles define *what we always do* and *what we never do*. These are non-negotiable standards applied to every line of code, every pull request, and every production system in the VENUS stack.

---

## 2. Foundational Principles

### 2.1 SOLID Principles (Institutional Grade)

| Principle | Definition | VENUS Application |
|---|---|---|
| **Single Responsibility** | A module has exactly one reason to change | One bounded context per service; one concern per class |
| **Open/Closed** | Open for extension, closed for modification | Use strategy, plugin, and decorator patterns over modification |
| **Liskov Substitution** | Subtypes must be substitutable for base types | Never override behavior that callers depend on |
| **Interface Segregation** | Clients should not depend on interfaces they don't use | Granular ports in hexagonal architecture |
| **Dependency Inversion** | Depend on abstractions, not concretions | All infrastructure accessed through domain-defined interfaces |

### 2.2 DRY — Don't Repeat Yourself
Every piece of knowledge must have a single, unambiguous, authoritative representation in the system. Violation creates divergence debt. When you copy-paste logic, you create two sources of truth; the second will diverge.

*Exception*: Avoid DRY across bounded contexts. Duplication between contexts is healthier than coupling between them.

### 2.3 YAGNI — You Aren't Gonna Need It
Do not implement features, abstractions, or generalizations before they are required. Build what the system needs today. Refactor when requirements demand it. Speculative generality is technical debt disguised as foresight.

### 2.4 KISS — Keep It Simple, Stupid
The simplest solution that meets the requirements is always preferred. Complexity must be justified. If you cannot explain your design to a senior engineer in three minutes, it is too complex.

### 2.5 Law of Demeter
A module should only know about its immediate collaborators. `a.getB().getC().doThing()` is a symptom of a broken encapsulation boundary. Objects should talk to friends, not strangers.

### 2.6 Principle of Least Surprise
Every function, method, endpoint, and system should behave in the way that a reasonable engineer would expect. Surprising behavior is a defect, even if it is technically correct.

### 2.7 Fail Fast
Detect and report errors as early as possible. Validate inputs at boundaries. Assert invariants. A system that fails fast produces clear error messages. A system that fails slowly produces corrupted state.

---

## 3. Code Quality Standards

### 3.1 Cognitive Complexity Budget
Every function has a cognitive complexity budget. The maximum allowed cyclomatic complexity per function is **10**. Functions exceeding this budget must be decomposed.

### 3.2 Function Length
- Maximum lines per function: **40**
- Maximum parameters per function: **5** (use parameter objects for more)
- Maximum nesting depth: **3 levels**

### 3.3 Naming Conventions
| Element | Convention | Example |
|---|---|---|
| Variables | Descriptive, intentional | `userAccountBalance`, not `x` or `val` |
| Functions | Verb + noun | `calculateInvoiceTotal()`, `validateUserInput()` |
| Boolean Variables | Is/Has/Can/Should prefix | `isAuthenticated`, `hasPermission` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRY_ATTEMPTS` |
| Classes/Interfaces | PascalCase noun | `InvoiceProcessor`, `UserRepository` |

### 3.4 No Magic Numbers or Strings
Every literal must be named as a constant. `if (status === 3)` is forbidden. `if (status === OrderStatus.FULFILLED)` is required.

---

## 4. Engineering Process Principles

### 4.1 Definition of Done (DoD)
A task is only "done" when:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code coverage meets threshold (≥ 85%)
- [ ] Static analysis passes with zero critical issues
- [ ] Code review approved by at least one senior engineer
- [ ] Documentation updated
- [ ] Performance impact assessed
- [ ] Security implications reviewed

### 4.2 Boy Scout Rule
Always leave the code in a better state than you found it. Every PR should fix at least one thing beyond its stated scope — a naming improvement, an unused import, a missing test. This is how codebases improve over time without dedicated refactoring sprints.

### 4.3 Zero-Tolerance Broken Windows
One broken window (a failing test, an unhandled exception, a TODO left in production) invites more. Fix broken windows immediately. Do not accumulate them.

### 4.4 Review Culture
- Code reviews are about the code, not the author
- Comments must be constructive and actionable
- Reviewers are responsible for bugs they approve
- Nitpicks must be labeled as such
- No PR merges without addressing all non-nitpick comments

---

## 5. The Ten Commandments of USEDPOS Engineering

1. Thou shalt not ship code that thou hast not tested
2. Thou shalt not hardcode secrets, credentials, or environment-specific values
3. Thou shalt not ignore or swallow exceptions
4. Thou shalt not write a function longer than 40 lines
5. Thou shalt not merge a PR with failing tests
6. Thou shalt not deploy to production without observability
7. Thou shalt not create a database without a migration plan
8. Thou shalt not expose an API without documentation
9. Thou shalt not copy logic across bounded contexts
10. Thou shalt not optimize before profiling
