# `skills/`

Agent skills are modular capabilities that AI agents can utilize to perform specific tasks within a project. Skills enhance the functionality of AI agents by providing them with specialized context knowledge and tools.

- [1. Agent Skills](#1-agent-skills)
  - [1.1. C++ Skills](#11-c-skills)
  - [1.2. Go Skills](#12-go-skills)
  - [1.3. Terraform Skills](#13-terraform-skills)
  - [1.4. Threat Modeling Skills](#14-threat-modeling-skills)
  - [1.5. Documentation Skills](#15-documentation-skills)
- [2. References](#2-references)

## 1. Agent Skills

Skills are documented in individual `SKILL.md` files located in appropriate subdirectories following the [Agent Skills](https://agentskills.io/specification) specification, containing metadata and descriptions of their purpose, usage, and integration within the project.

### 1.1. C++ Skills

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

### 1.4. Threat Modeling Skills

- [TM7 Threat Model](tm7-threat-model/SKILL.md)
  > External Agent Skill from [GitHub Awesome-Copilot](https://github.com/github/awesome-copilot) for generating valid [Microsoft Threat Modeling Tool (TMT)](https://github.com/github/awesome-copilot/tree/main/skills/tm7-threat-model) v7.3+ files with diagrams and STRIDE threats.

- [Threat Modeling ICS](threat-modeling-ics/SKILL.md)
  > Threat modeling for OT/ICS systems using Microsoft TMT, STRIDE, MITRE ATT&CK for ICS, CWE, and CVSS v4.0.

### 1.5. Documentation Skills

- [Architecture Decision Records (ADR)](adr/SKILL.md)
  > Creates and maintains Architecture Decision Records following a structured format with State, Context, Decision, Considered, Consequences, Implementation, and References sections.

- [Technical Article](technical-article/SKILL.md)
  > Creates, revises, and reviews convention-style technical articles using formal language, numbered Markdown structure, taxonomies, examples, and source-qualified references.

## 2. References

- [AGENTS.md](https://agents.md/) page.
- Agent Skills [Specification](https://agentskills.io/specification) page.
