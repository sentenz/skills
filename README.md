# Skills

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A catalog of modular agent skills for AI coding assistants, providing specialized context and guidance for software development tasks.

- [1. Details](#1-details)
  - [1.1. Prerequisites](#11-prerequisites)
  - [1.2. Installation](#12-installation)
  - [1.3. Usage](#13-usage)
- [2. Contribute](#2-contribute)
- [3. References](#3-references)

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

## 3. References

- [AGENTS.md](https://agents.md/) specification.
- Vercel [Skills](https://skills.sh/) page.
- Vercel [Skills](https://skills.sh/docs/cli) documentation.
- Agent [Skills](https://agentskills.io/specification) specification.
