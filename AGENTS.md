# AGENTS.md

Template for AI coding agent instructions and project configuration.

- [1. Overview](#1-overview)
- [2. Tech Stack](#2-tech-stack)
  - [2.1. Programming Language](#21-programming-language)
  - [2.2. Dependency Manager](#22-dependency-manager)
  - [2.3. Testing](#23-testing)
  - [2.4. Build System](#24-build-system)
  - [2.5. Code Quality](#25-code-quality)
  - [2.6. Security](#26-security)
- [3. Project Layout](#3-project-layout)
  - [3.1. Directory Structure](#31-directory-structure)
  - [3.2. Key Directories](#32-key-directories)
- [4. Task Runners](#4-task-runners)
  - [4.1. Available Commands](#41-available-commands)
- [5. Agent Skills](#5-agent-skills)
- [6. References](#6-references)

## 1. Overview

This file provides instructions and context for AI coding agents working with this project. It defines the tech stack, project structure, development workflows, and available agent skills.

## 2. Tech Stack

### 2.1. Programming Language

- **Language Name**
  > Brief description of the primary programming language used.
  >
  > Version: Specify version requirements

### 2.2. Dependency Manager

- **Manager Name**
  > Description of the dependency management system.
  >
  > Key commands:
  > - Command 1: Description
  > - Command 2: Description

### 2.3. Testing

- **Testing Framework**
  > Description of testing frameworks and approaches.
  >
  > Supports:
  > - Unit tests
  > - Integration tests
  > - Benchmark tests
  > - Fuzz tests
  > - Code coverage analysis

### 2.4. Build System

- **Build Tool**
  > Description of build system and automation tools.
  >
  > Used for: build automation, testing, linting, and deployment tasks

### 2.5. Code Quality

- **Linter**
  > Description of code quality tools.

- **Static Analysis**
  > Tools for detecting common mistakes and vulnerabilities.

### 2.6. Security

- **Vulnerability Scanner**
  > Tools for security scanning and vulnerability detection.

- **Policy Validation**
  > Tools for policy-as-code validation.

## 3. Project Layout

Standard project layout following community best practices for organizing code and resources.

### 3.1. Directory Structure

```plaintext
.
├── .github/            # GitHub workflows, actions, and configuration
│   ├── skills/         # Agent skills for AI coding assistants
│   └── workflows/      # GitHub Actions CI/CD workflows
├── src/                # Source code directory
├── tests/              # Test files and test data
├── scripts/            # Scripts for build, setup, and deployment
├── docs/               # Documentation files
├── README.md           # Project overview and getting started guide
└── AGENTS.md           # AI agent instructions and guidelines
```

### 3.2. Key Directories

- `src/`
  > Contains the main source code for the project.

- `.github/skills/`
  > Agent skills documentation following the [Agent Skills](https://agentskills.io/specification) specification for AI coding assistants.

- `tests/`
  > Contains test files and test data.

- `scripts/`
  > Automation scripts for bootstrapping, setup, and teardown of the development environment.

- `docs/`
  > Project documentation including architecture, design decisions, and API references.

## 4. Task Runners

Description of task runners used to automate common development tasks.

### 4.1. Available Commands

Run `make help` or equivalent command to see all available commands with descriptions.

Common commands:

- Setup & Installation
  > Commands for initializing and setting up the development environment.

- Building
  > Commands for compiling and building the project.

- Testing
  > Commands for running tests, generating coverage reports, and benchmarks.

- Code Quality
  > Commands for linting, formatting, and static analysis.

- Deployment
  > Commands for deploying the project.

## 5. Agent Skills

Agent skills are modular capabilities that AI agents can utilize to perform specific tasks within a project. Skills enhance the functionality of AI agents by providing them with specialized context knowledge and tools.

Skills are documented in individual `SKILL.md` files located in the [.github/skills/](.github/skills/) directory following the [Agent Skills](https://agentskills.io/specification) specification.

Available skills:

- [Unit Testing](.github/skills/unit-testing/SKILL.md)
  > Automates unit test creation using established testing patterns.

- [Mock Testing](.github/skills/mock-testing/SKILL.md)
  > Creates mock objects and stubs for testing.

- [Fuzz Testing](.github/skills/fuzz-testing/SKILL.md)
  > Implements fuzz testing for discovering edge cases.

- [Benchmark Testing](.github/skills/benchmark-testing/SKILL.md)
  > Measures and validates performance characteristics.

- [API Documentation](.github/skills/api-documentation/SKILL.md)
  > Generates and maintains API documentation.

## 6. References

- [AGENTS.md](https://agents.md/) specification page.
- Agent Skills [Specification](https://agentskills.io/specification) page.
- Project-specific documentation in [docs/](docs/) directory.
