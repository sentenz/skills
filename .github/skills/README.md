# `skills/`

Agent skills are modular capabilities that AI agents can utilize to perform specific tasks within a project. Skills enhance the functionality of AI agents by providing them with specialized context knowledge and tools.

- [1. Details](#1-details)
  - [1.1. Agent Skills](#11-agent-skills)
- [2. References](#2-references)

## 1. Details

### 1.1. Agent Skills

Skills are documented in individual `SKILL.md` files located in appropriate subdirectories following the [Agent Skills](https://agentskills.io/specification) specification, containing metadata and descriptions of their purpose, usage, and integration within the project.

#### C++ Skills

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

#### Go Skills

- [Go Unit Testing](go-unit-testing/SKILL.md)
  > Unit test creation for Go projects using the standard testing package with consistent software testing patterns.

- [Go Fuzz Testing](go-fuzz-testing/SKILL.md)
  > Fuzz test creation using Go's native fuzzing engine with coverage-guided testing.

- [Go Benchmark Testing](go-benchmark-testing/SKILL.md)
  > Benchmark test creation for performance measurement and optimization in Go projects.

- [Go API Documentation](go-api-documentation/SKILL.md)
  > API documentation creation using godoc conventions and best practices for Go projects.

## 2. References

- [AGENTS.md](https://agents.md/) page.
- Agent Skills [Specification](https://agentskills.io/specification) page.
