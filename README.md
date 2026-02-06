# Skills

Repository for [Agent Skills](https://agentskills.io/specification) (SKILL.md) and AGENTS.md template configurations for AI coding agents.

- [1. Overview](#1-overview)
- [2. Directory Structure](#2-directory-structure)
- [3. Agent Skills](#3-agent-skills)
- [4. AGENTS.md Template](#4-agentsmd-template)
- [5. Integration](#5-integration)
- [6. Usage Examples](#6-usage-examples)
- [7. Contributing](#7-contributing)
- [8. References](#8-references)

## 1. Overview

This repository provides reusable agent skills and configuration templates for AI coding agents. It follows the [Agent Skills specification](https://agentskills.io/specification) to enable modular, task-specific capabilities that AI agents can utilize across different projects.

## 2. Directory Structure

```plaintext
.
├── .github/
│   └── skills/            # Agent skill definitions
│       ├── README.md      # Skills overview and catalog
│       ├── unit-testing/  # Unit testing skill
│       ├── mock-testing/  # Mock testing skill
│       ├── fuzz-testing/  # Fuzz testing skill
│       ├── benchmark-testing/  # Benchmark testing skill
│       └── api-documentation/  # API documentation skill
├── AGENTS.md              # Template for AI agent instructions
└── README.md              # This file
```

## 3. Agent Skills

Agent skills are modular capabilities documented in individual `SKILL.md` files. Each skill provides:

- Metadata (name, version, activation triggers)
- Instructions for AI coding agents
- Patterns and best practices
- Templates and examples
- Workflow guidance

### Available Skills

#### C++ Skills

- **[Unit Testing](.github/skills/unit-testing/SKILL.md)**
  > Automates unit test creation using GoogleTest (GTest) framework with patterns like In-Got-Want, Table-Driven Testing, and AAA.

- **[Mock Testing](.github/skills/mock-testing/SKILL.md)**
  > Creates mock objects using Google Mock (GMock) for test isolation and behavior verification.

- **[Fuzz Testing](.github/skills/fuzz-testing/SKILL.md)**
  > Implements fuzz testing for discovering edge cases and vulnerabilities in C++ code.

- **[Benchmark Testing](.github/skills/benchmark-testing/SKILL.md)**
  > Measures and validates performance characteristics using benchmarking frameworks for C++ code.

- **[API Documentation](.github/skills/api-documentation/SKILL.md)**
  > Generates Doxygen-compatible documentation comments for C++ header files.

#### Go Skills

- **[Go Unit Testing](.github/skills/go-unit-testing/SKILL.md)**
  > Automates unit test creation for Go projects using the standard testing package with consistent software testing patterns.

- **[Go Fuzz Testing](.github/skills/go-fuzz-testing/SKILL.md)**
  > Implements fuzz testing using Go's native fuzzing engine with coverage-guided testing.

- **[Go Benchmark Testing](.github/skills/go-benchmark-testing/SKILL.md)**
  > Measures and validates performance characteristics for Go projects using benchmark testing.

- **[Go API Documentation](.github/skills/go-api-documentation/SKILL.md)**
  > Generates API documentation using godoc conventions and best practices for Go projects.

## 4. AGENTS.md Template

The [AGENTS.md](AGENTS.md) file provides a template for project-specific AI agent instructions. It includes:

- Tech stack overview
- Project layout and structure
- Task runner commands
- Development workflows
- Links to available agent skills

Projects can customize this template to provide context-specific guidance for AI coding agents working in their repositories.

## 5. Integration

### Skills CLI

Skills can be integrated using the [skills CLI](https://skills.sh/docs/cli):

```bash
# Install skills CLI
npm install -g @agentskills/cli

# Initialize skills in a project
skills init

# List available skills
skills list

# Add a skill to a project
skills add unit-testing

# Validate skill definitions
skills validate
```

### Usage in Projects

1. Copy desired skill folders from `.github/skills/` to your project's `.github/skills/` directory
2. Customize the `AGENTS.md` template for your project
3. Reference skills in AI agent configurations
4. AI agents will automatically discover and use skills based on activation triggers

See [USAGE.md](USAGE.md) for detailed examples and integration methods.

## 6. Usage Examples

Detailed usage examples and integration methods are available in [USAGE.md](USAGE.md), including:

- Direct copy integration
- Skills CLI usage
- Git submodule approach
- Customizing skills for your project
- Customizing AGENTS.md template
- Example project structures for C++, Go, and multi-language projects

## 7. Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Adding new skills
- Improving existing skills
- Skill structure and metadata
- Testing and validation
- Submitting pull requests

## 8. References

- [AGENTS.md](https://agents.md/) specification page
- Agent Skills [Specification](https://agentskills.io/specification) page
- [Skills CLI documentation](https://skills.sh/docs/cli)
- Source repositories:
  - [sentenz/template-cpp](https://github.com/sentenz/template-cpp/tree/main/.github/skills)
  - [sentenz/percent](https://github.com/sentenz/percent/tree/main/.github/skills)