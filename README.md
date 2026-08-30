# Skills

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A catalog of modular agent skills for AI coding assistants, providing specialized context and guidance for software development tasks.

- [1. Details](#1-details)
  - [1.1. Prerequisites](#11-prerequisites)
  - [1.2. Installation](#12-installation)
  - [1.3. Usage](#13-usage)
- [2. Contribution](#2-contribution)
- [3. Troubleshoot](#3-troubleshoot)
  - [3.1. Skill Invocation](#31-skill-invocation)
- [4. References](#4-references)

## 1. Details

### 1.1. Prerequisites

- [Node.js](https://nodejs.org/)
  > JavaScript runtime required to install and run the Skills CLI.

  ```bash
  # For Debian/Ubuntu (apt-based) on amd64
  sudo apt install -y nodejs
  ```

- [NPM](https://www.npmjs.com/get-npm)
  > NPM is required for managing dependencies and using the skills CLI for validation and integration.

  ```bash
  sudo apt install npm
  ```

- [Skills CLI](https://skills.sh/docs/cli)
  > CLI tool for managing AI agent skills in development projects.

  ```bash
  sudo npm install -g skills
  ```

### 1.2. Installation

- CLI
  > Add skills to a project using Vercel [Skills](https://skills.sh/) CLI.

  ```bash
  # Add a skill from the skill registry repository
  skills add <skill-repo-url>
  ```

- Tasks

  ```bash
  make agent-skills-add
  ```

### 1.3. Usage

Available skills can be activated by agents based on defined triggers and contextual cues, enabling AI coding assistants to invoke relevant skills for tasks.

- [C++ Skills](skills/README.md#11-c-skills)
  > C++ unit testing, mock testing, fuzz testing, benchmark testing, and API documentation skills.

- [Go Skills](skills/README.md#12-go-skills)
  > Go unit testing, fuzz testing, benchmark testing, and API documentation skills.

- [Terraform Skills](skills/README.md#13-terraform-skills)
  > Terraform and OpenTofu module design, testing, CI/CD, security, compliance, and state management skills.

- [Dependency Management Skills](skills/README.md#14-dependency-management-skills)
  > GitHub Dependabot configuration and management for version updates, security updates, grouping, and monorepos.

- [GitHub Actions Skills](skills/README.md#15-github-actions-skills)
  > GitHub Actions workflow efficiency auditing and security hardening guidance.

- [Threat Modeling Skills](skills/README.md#16-threat-modeling-skills)
  > Threat modeling for OT/ICS systems and Microsoft Threat Modeling Tool (`.tm7`) file generation.

- [Documentation Skills](skills/README.md#17-documentation-skills)
  > Architecture Decision Records (ADR) creation and maintenance skills.

- [UI and Design Skills](skills/README.md#18-ui-and-design-skills)
  > Material Design 3 implementation guidance for components, design tokens, theming, adaptive layouts, accessibility, and compliance auditing.

## 2. Contribution

[CONTRIBUTING.md](CONTRIBUTING.md) provides guidance and instructions for contributing to the project.

## 3. Troubleshoot

### 3.1. Skill Invocation

Instructions for troubleshooting skill invocation issues, including checking trigger conditions and ensuring skill compatibility.

- Implicit Invocation
  > Ensure that the agent's context and cues align with the skill's defined triggers for implicit invocation.

  ```plaintext
  .agents/skills/<skill-name>/SKILL.md
  ```

- Explicit Invocation
  > Verify that the correct command or API call is used to explicitly invoke the skill, and that the skill is properly registered in the agent's configuration.

  ```bash
  <agent> .agents/skills/<skill-name>/SKILL.md <task-description>
  ```

## 4. References

- [AGENTS.md](https://agents.md/) specification.
- Vercel [Skills](https://skills.sh/) page.
- Vercel [Skills](https://skills.sh/docs/cli) documentation.
- Agent [Skills](https://agentskills.io/specification) specification.
