# `skills/`

Agent skills are modular capabilities that AI agents can utilize to perform specific tasks within a project. Skills enhance the functionality of AI agents by providing them with specialized context knowledge and tools.

- [1. Agent Skills](#1-agent-skills)
  - [1.1. C++ Skills](#11-c-skills)
  - [1.2. Go Skills](#12-go-skills)
  - [1.3. Terraform Skills](#13-terraform-skills)
  - [1.4. Dependency Management Skills](#14-dependency-management-skills)
  - [1.5. GitHub Actions Skills](#15-github-actions-skills)
  - [1.6. Container Skills](#16-container-skills)
  - [1.7. Threat Modeling Skills](#17-threat-modeling-skills)
  - [1.8. Documentation Skills](#18-documentation-skills)
  - [1.9. UI and Design Skills](#19-ui-and-design-skills)
  - [1.10. Python Skills](#110-python-skills)
  - [1.11. Security Skills](#111-security-skills)
- [2. References](#2-references)

## 1. Agent Skills

Skills are documented in individual `SKILL.md` files located in appropriate subdirectories following the [Agent Skills](https://agentskills.io/specification) specification, containing metadata and descriptions of their purpose, usage, and integration within the project.

### 1.1. C++ Skills

- [Google C++ Style Guide](google-cpp-style-guide/SKILL.md)
  > External Agent Skill adapted from the MIT-licensed [TestDino Google Style Guides collection](https://github.com/testdino-hq/google-styleguides-skills) for headers, naming, formatting, classes, ownership, RAII, and smart pointers, preserving project conventions.

- [C++ Unit Testing](cpp-unit-testing/SKILL.md)
  > Unit test creation using GoogleTest (GTest) framework with In-Got-Want, Table-Driven Testing, and AAA patterns.

- [C++ Mock Testing](cpp-mock-testing/SKILL.md)
  > Mock test creation using Google Mock (GMock) for test isolation and behavior verification.

- [C++ Fuzz Testing](cpp-fuzz-testing/SKILL.md)
  > Fuzz test creation for discovering edge cases and vulnerabilities.

- [C++ Benchmark Testing](cpp-benchmark-testing/SKILL.md)
  > Benchmark test creation for performance measurement and optimization.

- [C++ API Documentation](cpp-api-documentation/SKILL.md)
  > API documentation creation using Doxygen-compatible comments for C++ header files.

### 1.2. Go Skills

- [Google Go Style Guide](google-go-style-guide/SKILL.md)
  > External Agent Skill adapted from the MIT-licensed [TestDino Google Style Guides collection](https://github.com/testdino-hq/google-styleguides-skills) for gofmt formatting, naming, errors, interfaces, concurrency, and package organization, preserving project conventions.

- [Go Unit Testing](go-unit-testing/SKILL.md)
  > Unit test creation for Go projects using the standard testing package with consistent software testing patterns.

- [Go Fuzz Testing](go-fuzz-testing/SKILL.md)
  > Fuzz test creation using Go's native fuzzing engine with coverage-guided testing.

- [Go Benchmark Testing](go-benchmark-testing/SKILL.md)
  > Benchmark test creation for performance measurement and optimization in Go projects.

- [Go API Documentation](go-api-documentation/SKILL.md)
  > API documentation creation using godoc conventions and best practices for Go projects.

### 1.3. Terraform Skills

- [Terraform](terraform/SKILL.md)
  > External Agent Skill for [Terraform and OpenTofu](https://github.com/antonbabenko/terraform-skill) guidance for module design, testing, CI/CD, security, compliance, and state management.

### 1.4. Dependency Management Skills

- [Dependabot](dependabot/SKILL.md)
  > External Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for [Dependabot](https://github.com/github/awesome-copilot/tree/main/skills/dependabot) configuration and management, including version updates, security updates, grouping, monorepos, and pull requests.

### 1.5. GitHub Actions Skills

- [GitHub Actions Efficiency](github-actions-efficiency/SKILL.md)
  > External MIT-licensed Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for auditing [GitHub Actions efficiency](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-efficiency), reducing CI runtime, redundant workflow execution, and cost while preserving required validation.

- [GitHub Actions Hardening](github-actions-hardening/SKILL.md)
  > External MIT-licensed Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for reviewing and [hardening GitHub Actions workflows](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-hardening), including trigger trust, script injection, token permissions, action pinning, secrets, OIDC, and runner exposure.

### 1.6. Container Skills

- [Multi-Stage Dockerfile](multi-stage-dockerfile/SKILL.md)
  > External Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for creating optimized [multi-stage Dockerfiles](https://github.com/github/awesome-copilot/tree/main/skills/multi-stage-dockerfile) with smaller runtime images, improved caching, reproducible builds, and security hardening.

### 1.7. Threat Modeling Skills

- [TM7 Threat Model](tm7-threat-model/SKILL.md)
  > External Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for generating valid [Microsoft Threat Modeling Tool (TMT)](https://github.com/github/awesome-copilot/tree/main/skills/tm7-threat-model) v7.3+ files with diagrams and STRIDE threats.

- [Threat Modeling ICS](threat-modeling-ics/SKILL.md)
  > Threat modeling for OT/ICS systems using Microsoft TMT, STRIDE, MITRE ATT&CK for ICS, CWE, and CVSS v4.0.

### 1.8. Documentation Skills

- [Architecture Decision Records (ADR)](adr/SKILL.md)
  > Creates and maintains Architecture Decision Records following a structured format with State, Context, Decision, Considered, Consequences, Implementation, and References sections.

- [Technical Article](technical-article/SKILL.md)
  > Creates, revises, and reviews convention-style technical articles using formal language, numbered Markdown structure, taxonomies, examples, and source-qualified references.

### 1.9. UI and Design Skills

- [Material Design 3](material-3/SKILL.md)
  > External Agent Skill from the MIT-licensed [hamen/material-3-skill](https://github.com/hamen/material-3-skill) for Material Design 3 implementation across Jetpack Compose, Flutter, and limited web, including design tokens, 30+ components, theming, adaptive layout, M3 Expressive guidance, accessibility, and compliance auditing.

### 1.10. Python Skills

- [Google Python Style Guide](google-python-style-guide/SKILL.md)
  > External Agent Skill adapted from the MIT-licensed [TestDino Google Style Guides collection](https://github.com/testdino-hq/google-styleguides-skills) for type annotations, Google-style docstrings, imports, naming, comprehensions, and exception handling, preserving project conventions.

- [Python Unit Testing](python-unit-testing/SKILL.md)
  > Unit and regression test creation with pytest or unittest using FIRST, In-Got-Want, table-driven testing, AAA, fixtures, and branch coverage.

- [Python Mock Testing](python-mock-testing/SKILL.md)
  > Dependency isolation and interaction verification using unittest.mock, autospec, async mocks, and pytest monkeypatch.

- [Python Fuzz Testing](python-fuzz-testing/SKILL.md)
  > Property-based tests with Hypothesis and coverage-guided fuzz targets with Atheris, including bounded campaigns and reproducible regressions.

- [Python Benchmark Testing](python-benchmark-testing/SKILL.md)
  > Performance measurement with pytest-benchmark and pyperf, including baseline comparisons, mutable workloads, and separate profiling.

### 1.11. Security Skills

- [Security Audit](security-audit/SKILL.md)
  > External MIT-licensed Agent Skill from [Cloudflare](https://github.com/cloudflare/security-audit-skill) for source-grounded vulnerability review, coverage planning, independent validation, and structured reporting. Includes the complete six-phase workflow, domain references, report schema, and zero-dependency validators and tests. The imported revision and local adaptations are recorded in the skill's upstream source section.

Install the skill from this repository:

```bash
npx skills add sentenz/skills --skill security-audit
```

Use a coding agent with tool use and parallel sub-agents, plus Node.js for the validators. Executing target code requires an OS-enforced sandbox with external networking disabled, an allowlisted environment, resource limits, and writes restricted to assigned scratch paths. When those controls are unavailable, retain blocked leads as needing validation and provide a safe validation plan.

Invocation examples:

```plaintext
security audit this codebase
```

```plaintext
find security vulnerabilities in ./src
```

```plaintext
do a security review, output to ~/logs/audits/
```

Security questions and focused reviews use guidance mode. Explicit codebase audits, pen tests, full reviews, or requested report artifacts use the complete workflow. Full audits default to `~/security-audit-skill/<repo-name>/run-<N>`; an output directory inside the target requires explicit selection and verification that version control ignores it.

Full audits produce `run-metadata.json`, `architecture.md`, `coverage-ledger.json`, `findings.json`, `REPORT.md`, `FINDINGS-DETAIL.md`, and `NEEDS-VALIDATION.md`. Findings distinguish `confirmed`, `needs_validation`, and `rejected`; only confirmed findings receive severity. The audit recommends fixes without modifying target source.

Run the bundled validator tests from the repository root:

```bash
make security-audit-test
```

## 2. References

- Agent [Instructions (AGENTS.md)](https://agents.md/) page.
- Agent [Skills (SKILL.md)](https://agentskills.io/specification) specification.
