# Skills

Repository for [Agent Skills](https://agentskills.io/specification) (SKILL.md) and AGENTS.md template configurations for AI coding agents.

- [1. Overview](#1-overview)
- [2. Directory Structure](#2-directory-structure)
- [3. Agent Skills](#3-agent-skills)
  - [3.1. Available Skills](#31-available-skills)
    - [3.1.1. C++ Skills](#311-c-skills)
    - [3.1.2. Go Skills](#312-go-skills)
- [4. AGENTS.md Template](#4-agentsmd-template)
- [5. Integration](#5-integration)
  - [5.1. Skills CLI](#51-skills-cli)
  - [5.2. Usage in Projects](#52-usage-in-projects)
- [6. Usage Examples](#6-usage-examples)
- [7. Contributing](#7-contributing)
- [8. References](#8-references)

## 1. Overview

This repository provides reusable agent skills and configuration templates for AI coding agents. It follows the [Agent Skills specification](https://agentskills.io/specification) to enable modular, task-specific capabilities that AI agents can utilize across different projects.

## 2. Directory Structure

```plaintext
.
├── .github/
│   └── skills/                  # Agent skill definitions
│       ├── README.md            # Skills overview and catalog
│       ├── cpp-unit-testing/    # C++ unit testing skill
│       ├── cpp-mock-testing/    # C++ mock testing skill
│       ├── cpp-fuzz-testing/    # C++ fuzz testing skill
│       ├── cpp-benchmark-testing/  # C++ benchmark testing skill
│       ├── cpp-api-documentation/  # C++ API documentation skill
│       ├── go-unit-testing/     # Go unit testing skill
│       ├── go-fuzz-testing/     # Go fuzz testing skill
│       ├── go-benchmark-testing/  # Go benchmark testing skill
│       └── go-api-documentation/  # Go API documentation skill
├── AGENTS.md                    # Template for AI agent instructions
└── README.md                    # This file
```

## 3. Agent Skills

Agent skills are modular capabilities documented in individual `SKILL.md` files. Each skill provides:

- Metadata (name, version, activation triggers)
- Instructions for AI coding agents
- Patterns and best practices
- Templates and examples
- Workflow guidance

### 3.1. Available Skills

#### 3.1.1. C++ Skills

- **[C++ Unit Testing](skills/cpp-unit-testing/SKILL.md)**
  > Automates unit test creation using GoogleTest (GTest) framework with patterns like In-Got-Want, Table-Driven Testing, and AAA.

- **[C++ Mock Testing](skills/cpp-mock-testing/SKILL.md)**
  > Creates mock objects using Google Mock (GMock) for test isolation and behavior verification.

- **[C++ Fuzz Testing](skills/cpp-fuzz-testing/SKILL.md)**
  > Implements fuzz testing for discovering edge cases and vulnerabilities in C++ code.

- **[C++ Benchmark Testing](skills/cpp-benchmark-testing/SKILL.md)**
  > Measures and validates performance characteristics using benchmarking frameworks for C++ code.

- **[C++ API Documentation](skills/cpp-api-documentation/SKILL.md)**
  > Generates Doxygen-compatible documentation comments for C++ header files.

#### 3.1.2. Go Skills

- **[Go Unit Testing](skills/go-unit-testing/SKILL.md)**
  > Automates unit test creation for Go projects using the standard testing package with consistent software testing patterns.

- **[Go Fuzz Testing](skills/go-fuzz-testing/SKILL.md)**
  > Implements fuzz testing using Go's native fuzzing engine with coverage-guided testing.

- **[Go Benchmark Testing](skills/go-benchmark-testing/SKILL.md)**
  > Measures and validates performance characteristics for Go projects using benchmark testing.

- **[Go API Documentation](skills/go-api-documentation/SKILL.md)**
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

### 5.1. Skills CLI

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

### 5.2. Usage in Projects

1. Copy desired skill folders from `skills/` to your project's `skills/` directory
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
  - [sentenz/template-cpp](https://github.com/sentenz/template-cpp/tree/main/skills)
  - [sentenz/percent](https://github.com/sentenz/percent/tree/main/skills)
