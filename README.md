# Skills

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A catalog of modular agent skills for AI coding assistants, providing specialized context and guidance for software development tasks.

- [1. Details](#1-details)
  - [1.1. Prerequisites](#11-prerequisites)
  - [1.2. Installation](#12-installation)
  - [1.3. Usage](#13-usage)
- [2. Contribute](#2-contribute)
- [3. Troubleshoot](#3-troubleshoot)
  - [3.1. TODO](#31-todo)
- [4. References](#4-references)

## 1. Details

### 1.1. Prerequisites

- [Node.js](https://nodejs.org/)

  > JavaScript runtime required to install and run the Skills CLI.

  ```bash
  # For linux/amd64
  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt install -y nodejs
  ```

- [Skills CLI](https://skills.sh/docs/cli)

  > CLI tool for managing AI agent skills in development projects.

  ```bash
  npm install -g @agentskills/cli
  ```

### 1.2. Installation

- Install

  > Add skills to a project using the Skills CLI.

  ```bash
  # Initialize skills in your project
  skills init

  # Add a specific skill
  skills add cpp-unit-testing
  ```

- Manual

  > Copy skills directly to your project's `skills/` directory.

  ```bash
  cp -r path/to/skills/skills/cpp-unit-testing .github/skills/
  ```

### 1.3. Usage

- Manage

  > List, update, and validate skills in your project.

  ```bash
  # List available skills
  skills list

  # Update skills from the catalog
  skills update

  # Validate skill definitions
  skills validate
  ```

- Git Submodule

  > Use a git submodule for dynamic updates from the catalog.

  ```bash
  # Add this repository as a submodule
  git submodule add https://github.com/sentenz/skills skills-catalog

  # Update skills from the catalog
  git submodule update --remote
  ```

## 2. Contribute

[CONTRIBUTING.md](CONTRIBUTING.md) provides guidelines and instructions for contributing to the project.

- [Getting Started](CONTRIBUTING.md#1-getting-started)

  > Familiarize yourself with the Agent Skills Specification and existing skills before contributing.

- [Adding a New Skill](CONTRIBUTING.md#2-adding-a-new-skill)

  > Step-by-step instructions for creating and submitting a new skill to the catalog.

- [Skill Structure](CONTRIBUTING.md#3-skill-structure)

  > Template and format for `SKILL.md` files including metadata frontmatter and documentation sections.

- [Metadata Guidelines](CONTRIBUTING.md#4-metadata-guidelines)

  > Guidelines for versioning, activation triggers, language/path matching, and usage configuration.

- [Testing Your Skill](CONTRIBUTING.md#5-testing-your-skill)

  > Validation steps to verify skill frontmatter, links, activation triggers, and real-world behavior.

- [Submitting Your Changes](CONTRIBUTING.md#6-submitting-your-changes)

  > Instructions for forking, branching, committing, and opening a pull request.

- [Guidelines for Good Skills](CONTRIBUTING.md#7-guidelines-for-good-skills)

  > Best practices for writing focused, well-documented, and maintainable skills.

## 3. Troubleshoot

### 3.1. TODO

TODO

## 4. References

- [AGENTS.md](https://agents.md/) specification page.
- Agent Skills [Specification](https://agentskills.io/specification) page.
- [Skills CLI](https://skills.sh/docs/cli) documentation.
- Sentenz [Template C++](https://github.com/sentenz/template-cpp) repository.
- Sentenz [Percent](https://github.com/sentenz/percent) repository.
