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
  # For Debian/Ubuntu (apt-based) on amd64
  sudo apt install -y nodejs
  ```

- [Skills CLI](https://skills.sh/docs/cli)
  > CLI tool for managing AI agent skills in development projects.

  ```bash
  npm install -g skills
  ```

### 1.2. Installation

- Install
  > Add skills to a project using the Skills CLI.

  ```bash
  # Initialize skills in your project
  skills init

  # Add a specific skill
  skills add sentenz/skills
  ```

### 1.3. Usage

Available skills can be activated by agents based on defined triggers and contextual cues, enabling AI coding assistants to invoke relevant skills for tasks.

- [C++ Skills](skills/README.md#11-c-skills)
  > C++ unit testing, mock testing, fuzz testing, benchmark testing, and API documentation skills.

- [Go Skills](skills/README.md#12-go-skills)
  > Go unit testing, fuzz testing, benchmark testing, and API documentation skills.

- [Threat Modeling Skills](skills/README.md#13-threat-modeling-skills)
  > Threat modeling for OT/ICS systems.

- [Documentation Skills](skills/README.md#14-documentation-skills)
  > Architecture Decision Records (ADR) creation and maintenance skills.

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

- [AGENTS.md](https://agents.md/) page.
- Vercel [Skills](https://skills.sh/) page.
- Vercel [Skills Documentation](https://skills.sh/docs/cli) page.
- Agent Skills [Specification](https://agentskills.io/specification) page.
