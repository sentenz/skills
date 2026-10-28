# `skills/`

Agent skills are modular capabilities that AI agents can utilize to perform specific tasks within a project. Skills enhance the functionality of AI agents by providing them with specialized context knowledge and tools.

- [1. Agent Skills](#1-agent-skills)
  - [1.1. C++ Skills](#11-c-skills)
    - [1.1.1. Google C++ Style Guide](#111-google-c-style-guide)
    - [1.1.2. C++ Unit Testing](#112-c-unit-testing)
    - [1.1.3. C++ Mock Testing](#113-c-mock-testing)
    - [1.1.4. C++ Fuzz Testing](#114-c-fuzz-testing)
    - [1.1.5. C++ Benchmark Testing](#115-c-benchmark-testing)
    - [1.1.6. C++ API Documentation](#116-c-api-documentation)
  - [1.2. Go Skills](#12-go-skills)
    - [1.2.1. Google Go Style Guide](#121-google-go-style-guide)
    - [1.2.2. Go Unit Testing](#122-go-unit-testing)
    - [1.2.3. Go Fuzz Testing](#123-go-fuzz-testing)
    - [1.2.4. Go Benchmark Testing](#124-go-benchmark-testing)
    - [1.2.5. Go API Documentation](#125-go-api-documentation)
  - [1.3. Terraform Skills](#13-terraform-skills)
    - [1.3.1. Terraform](#131-terraform)
  - [1.4. Dependency Management Skills](#14-dependency-management-skills)
    - [1.4.1. Dependabot](#141-dependabot)
  - [1.5. GitHub Actions Skills](#15-github-actions-skills)
    - [1.5.1. GitHub Actions Efficiency](#151-github-actions-efficiency)
    - [1.5.2. GitHub Actions Hardening](#152-github-actions-hardening)
  - [1.6. Container Skills](#16-container-skills)
    - [1.6.1. Multi-Stage Dockerfile](#161-multi-stage-dockerfile)
  - [1.7. Threat Modeling Skills](#17-threat-modeling-skills)
    - [1.7.1. TM7 Threat Model](#171-tm7-threat-model)
    - [1.7.2. Threat Modeling ICS](#172-threat-modeling-ics)
  - [1.8. Documentation Skills](#18-documentation-skills)
    - [1.8.1. Architecture Decision Records (ADR)](#181-architecture-decision-records-adr)
    - [1.8.2. Technical Article](#182-technical-article)
  - [1.9. Design Skills](#19-design-skills)
    - [1.9.1. Material Design 3](#191-material-design-3)
  - [1.10. Python Skills](#110-python-skills)
    - [1.10.1. Google Python Style Guide](#1101-google-python-style-guide)
    - [1.10.2. Python Unit Testing](#1102-python-unit-testing)
    - [1.10.3. Python Mock Testing](#1103-python-mock-testing)
    - [1.10.4. Python Fuzz Testing](#1104-python-fuzz-testing)
    - [1.10.5. Python Benchmark Testing](#1105-python-benchmark-testing)
  - [1.11. Security Skills](#111-security-skills)
    - [1.11.1. Security Audit](#1111-security-audit)
- [2. References](#2-references)

## 1. Agent Skills

Skills are documented in individual `SKILL.md` files located in appropriate subdirectories following the [Agent Skills](https://agentskills.io/specification) specification, containing metadata and descriptions of their purpose, usage, and integration within the project.

### 1.1. C++ Skills

#### 1.1.1. Google C++ Style Guide

[Google C++ Style Guide](google-cpp-style-guide/SKILL.md)

External Agent Skill adapted from the MIT-licensed [TestDino Google Style Guides collection](https://github.com/testdino-hq/google-styleguides-skills) for headers, naming, formatting, classes, ownership, RAII, and smart pointers, preserving project conventions.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill google-cpp-style-guide
    ```

2. Invocation

    ```plaintext
    Review the C++ code in this repository using the google-cpp-style-guide skill.
    ```

#### 1.1.2. C++ Unit Testing

[C++ Unit Testing](cpp-unit-testing/SKILL.md)

Unit test creation using GoogleTest (GTest) framework with In-Got-Want, Table-Driven Testing, and AAA patterns.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill cpp-unit-testing
    ```

2. Invocation

    ```plaintext
    Use the cpp-unit-testing skill to add GoogleTest unit tests for the C++ code in this repository.
    ```

#### 1.1.3. C++ Mock Testing

[C++ Mock Testing](cpp-mock-testing/SKILL.md)

Mock test creation using Google Mock (GMock) for test isolation and behavior verification.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill cpp-mock-testing
    ```

2. Invocation

    ```plaintext
    Use the cpp-mock-testing skill to test the C++ interfaces in this repository with Google Mock.
    ```

#### 1.1.4. C++ Fuzz Testing

[C++ Fuzz Testing](cpp-fuzz-testing/SKILL.md)

Fuzz test creation for discovering edge cases and vulnerabilities.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill cpp-fuzz-testing
    ```

2. Invocation

    ```plaintext
    Use the cpp-fuzz-testing skill to add Google FuzzTest tests for the C++ input parsers in this repository.
    ```

#### 1.1.5. C++ Benchmark Testing

[C++ Benchmark Testing](cpp-benchmark-testing/SKILL.md)

Benchmark test creation for performance measurement and optimization.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill cpp-benchmark-testing
    ```

2. Invocation

    ```plaintext
    Use the cpp-benchmark-testing skill to add Google Benchmark benchmarks for the C++ code in this repository.
    ```

#### 1.1.6. C++ API Documentation

[C++ API Documentation](cpp-api-documentation/SKILL.md)

API documentation creation using Doxygen-compatible comments for C++ header files.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill cpp-api-documentation
    ```

2. Invocation

    ```plaintext
    Use the cpp-api-documentation skill to add Doxygen comments to the existing C++ headers in this repository.
    ```

### 1.2. Go Skills

#### 1.2.1. Google Go Style Guide

[Google Go Style Guide](google-go-style-guide/SKILL.md)

External Agent Skill adapted from the MIT-licensed [TestDino Google Style Guides collection](https://github.com/testdino-hq/google-styleguides-skills) for gofmt formatting, naming, errors, interfaces, concurrency, and package organization, preserving project conventions.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill google-go-style-guide
    ```

2. Invocation

    ```plaintext
    Review the Go code in this repository using the google-go-style-guide skill.
    ```

#### 1.2.2. Go Unit Testing

[Go Unit Testing](go-unit-testing/SKILL.md)

Unit test creation for Go projects using the standard testing package with consistent software testing patterns.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill go-unit-testing
    ```

2. Invocation

    ```plaintext
    Use the go-unit-testing skill to add table-driven unit tests for the Go packages in this repository.
    ```

#### 1.2.3. Go Fuzz Testing

[Go Fuzz Testing](go-fuzz-testing/SKILL.md)

Fuzz test creation using Go's native fuzzing engine with coverage-guided testing.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill go-fuzz-testing
    ```

2. Invocation

    ```plaintext
    Use the go-fuzz-testing skill to add native Go fuzz tests for the input parsers in this repository.
    ```

#### 1.2.4. Go Benchmark Testing

[Go Benchmark Testing](go-benchmark-testing/SKILL.md)

 Benchmark test creation for performance measurement and optimization in Go projects.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill go-benchmark-testing
    ```

2. Invocation

    ```plaintext
    Use the go-benchmark-testing skill to add benchmarks for the Go packages in this repository.
    ```

#### 1.2.5. Go API Documentation

[Go API Documentation](go-api-documentation/SKILL.md)

External Agent Skill for API documentation creation using godoc conventions and best practices for Go projects.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill go-api-documentation
    ```

2. Invocation

    ```plaintext
    Use the go-api-documentation skill to document the exported Go APIs in this repository.
    ```

### 1.3. Terraform Skills

#### 1.3.1. Terraform

[Terraform](terraform/SKILL.md)

 External Agent Skill for [Terraform and OpenTofu](https://github.com/antonbabenko/terraform-skill) guidance for module design, testing, CI/CD, security, compliance, and state management.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill terraform
    ```

2. Invocation

    ```plaintext
    Use the terraform skill to review the Terraform modules in this repository and recommend improvements.
    ```

### 1.4. Dependency Management Skills

#### 1.4.1. Dependabot

[Dependabot](dependabot/SKILL.md)

External Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for [Dependabot](https://github.com/github/awesome-copilot/tree/main/skills/dependabot) configuration and management, including version updates, security updates, grouping, monorepos, and pull requests.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill dependabot
    ```

2. Invocation

    ```plaintext
    Use the dependabot skill to configure dependency updates for this repository.
    ```

### 1.5. GitHub Actions Skills

#### 1.5.1. GitHub Actions Efficiency

[GitHub Actions Efficiency](github-actions-efficiency/SKILL.md)

External MIT-licensed Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for auditing [GitHub Actions efficiency](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-efficiency), reducing CI runtime, redundant workflow execution, and cost while preserving required validation.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill github-actions-efficiency
    ```

2. Invocation

    ```plaintext
    Use the github-actions-efficiency skill to audit .github/workflows for redundant runs and unnecessary CI costs.
    ```

#### 1.5.2. GitHub Actions Hardening

[GitHub Actions Hardening](github-actions-hardening/SKILL.md)

External MIT-licensed Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for reviewing and [hardening GitHub Actions workflows](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-hardening), including trigger trust, script injection, token permissions, action pinning, secrets, OIDC, and runner exposure.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill github-actions-hardening
    ```

2. Invocation

    ```plaintext
    Use the github-actions-hardening skill to review .github/workflows for security risks and recommend fixes.
    ```

### 1.6. Container Skills

#### 1.6.1. Multi-Stage Dockerfile

[Multi-Stage Dockerfile](multi-stage-dockerfile/SKILL.md)

External Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for creating optimized [multi-stage Dockerfiles](https://github.com/github/awesome-copilot/tree/main/skills/multi-stage-dockerfile) with smaller runtime images, improved caching, reproducible builds, and security hardening.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill multi-stage-dockerfile
    ```

2. Invocation

    ```plaintext
    Use the multi-stage-dockerfile skill to create an optimized multi-stage Dockerfile for this application.
    ```

### 1.7. Threat Modeling Skills

#### 1.7.1. TM7 Threat Model

[TM7 Threat Model](tm7-threat-model/SKILL.md)

External Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for generating valid [Microsoft Threat Modeling Tool (TMT)](https://github.com/github/awesome-copilot/tree/main/skills/tm7-threat-model) v7.3+ files with diagrams and STRIDE threats.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill tm7-threat-model
    ```

2. Invocation

    ```plaintext
    Use the tm7-threat-model skill to create a STRIDE threat model for this application as a Microsoft TMT .tm7 file.
    ```

#### 1.7.2. Threat Modeling ICS

- [Threat Modeling ICS](threat-modeling-ics/SKILL.md)

Threat modeling for OT/ICS systems using Microsoft TMT, STRIDE, MITRE ATT&CK for ICS, CWE, and CVSS v4.0.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill threat-modeling-ics
    ```

2. Invocation

    ```plaintext
    Use the threat-modeling-ics skill to create an OT/ICS threat model from the supplied architecture and asset inventory.
    ```

### 1.8. Documentation Skills

#### 1.8.1. Architecture Decision Records (ADR)

- [Architecture Decision Records (ADR)](adr/SKILL.md)

Creates and maintains Architecture Decision Records following a structured format with State, Context, Decision, Considered, Consequences, Implementation, and References sections.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill adr
    ```

2. Invocation

    ```plaintext
    Use the adr skill to document the decision to use PostgreSQL for this application, including alternatives and consequences.
    ```

#### 1.8.2. Technical Article

- [Technical Article](technical-article/SKILL.md)

Creates, revises, and reviews convention-style technical articles using formal language, numbered Markdown structure, taxonomies, examples, and source-qualified references.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill technical-article
    ```

2. Invocation

    ```plaintext
    Use the technical-article skill to write a technical article explaining this repository's architecture.
    ```

### 1.9. Design Skills

#### 1.9.1. Material Design 3

- [Material Design 3](material-3/SKILL.md)

External Agent Skill from the MIT-licensed [hamen/material-3-skill](https://github.com/hamen/material-3-skill) for Material Design 3 implementation across Jetpack Compose, Flutter, and limited web, including design tokens, 30+ components, theming, adaptive layout, M3 Expressive guidance, accessibility, and compliance auditing.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill material-3
    ```

2. Invocation

    ```plaintext
    Use the material-3 skill to review this application's UI for Material Design 3 compliance and recommend improvements.
    ```

### 1.10. Python Skills

#### 1.10.1. Google Python Style Guide

- [Google Python Style Guide](google-python-style-guide/SKILL.md)
  > External Agent Skill adapted from the MIT-licensed [TestDino Google Style Guides collection](https://github.com/testdino-hq/google-styleguides-skills) for type annotations, Google-style docstrings, imports, naming, comprehensions, and exception handling, preserving project conventions.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill google-python-style-guide
    ```

2. Invocation

    ```plaintext
    Review the Python code in this repository using the google-python-style-guide skill.
    ```

#### 1.10.2. Python Unit Testing

- [Python Unit Testing](python-unit-testing/SKILL.md)
  > Unit and regression test creation with pytest or unittest using FIRST, In-Got-Want, table-driven testing, AAA, fixtures, and branch coverage.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill python-unit-testing
    ```

2. Invocation

    ```plaintext
    Use the python-unit-testing skill to add pytest unit tests for the Python modules in this repository.
    ```

#### 1.10.3. Python Mock Testing

- [Python Mock Testing](python-mock-testing/SKILL.md)
  > Dependency isolation and interaction verification using unittest.mock, autospec, async mocks, and pytest monkeypatch.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill python-mock-testing
    ```

2. Invocation

    ```plaintext
    Use the python-mock-testing skill to isolate external dependencies in this repository's Python tests.
    ```

#### 1.10.4. Python Fuzz Testing

- [Python Fuzz Testing](python-fuzz-testing/SKILL.md)
  > Property-based tests with Hypothesis and coverage-guided fuzz targets with Atheris, including bounded campaigns and reproducible regressions.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill python-fuzz-testing
    ```

2. Invocation

    ```plaintext
    Use the python-fuzz-testing skill to add Hypothesis property-based tests for this repository's Python input parsers.
    ```

#### 1.10.5. Python Benchmark Testing

[Python Benchmark Testing](python-benchmark-testing/SKILL.md)

Performance measurement with pytest-benchmark and pyperf, including baseline comparisons, mutable workloads, and separate profiling.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill python-benchmark-testing
    ```

2. Invocation

    ```plaintext
    Use the python-benchmark-testing skill to add pytest-benchmark benchmarks for this repository's Python code.
    ```

### 1.11. Security Skills

#### 1.11.1. Security Audit

[Security Audit](security-audit/SKILL.md)

External MIT-licensed Agent Skill from [Cloudflare](https://github.com/cloudflare/security-audit-skill) for source-grounded vulnerability review, coverage planning, independent validation, and structured reporting. The skill includes the complete six-phase workflow, domain references, report schema, and zero-dependency validators and tests. The imported revision and local adaptations are recorded in the skill's upstream source section.

1. Installation

    ```bash
    npx skills add sentenz/skills --skill security-audit
    ```

    > [!NOTE]
    > Use a coding agent with tool use and parallel sub-agents, plus Node.js for the validators. Executing target code requires an OS-enforced sandbox with external networking disabled, an allowlisted environment, resource limits, and writes restricted to assigned scratch paths. When those controls are unavailable, retain blocked leads as needing validation and provide a safe validation plan.

2. Invocation

    ```plaintext
    Security audit this codebase
    ```

    ```plaintext
    Find security vulnerabilities in ./src
    ```

    ```plaintext
    Do a security review, output to ~/logs/audits/
    ```

    > [!NOTE]
    > Security questions and focused reviews use guidance mode. Explicit codebase audits, pen tests, full reviews, or requested report artifacts use the complete workflow. Full audits default to `~/security-audit-skill/<repo-name>/run-<N>`. An output directory inside the target requires explicit selection and verification that version control ignores it.
    >
    > Full audits produce `run-metadata.json`, `architecture.md`, `coverage-ledger.json`, `findings.json`, `REPORT.md`, `FINDINGS-DETAIL.md`, and `NEEDS-VALIDATION.md`. Findings distinguish `confirmed`, `needs_validation`, and `rejected`; only confirmed findings receive severity. The audit recommends fixes without modifying target source.

3. Task

    ```bash
    make security-audit-test
    ```

## 2. References

- Agent [Instructions (AGENTS.md)](https://agents.md/) page.
- Agent [Skills (SKILL.md)](https://agentskills.io/specification) specification.
