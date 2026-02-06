# Contributing to Skills

Thank you for your interest in contributing to the Agent Skills repository! This guide will help you add new skills or improve existing ones.

- [1. Getting Started](#1-getting-started)
- [2. Adding a New Skill](#2-adding-a-new-skill)
- [3. Skill Structure](#3-skill-structure)
- [4. Metadata Guidelines](#4-metadata-guidelines)
  - [4.1. Version](#41-version)
  - [4.2. Activation](#42-activation)
  - [4.3. Usage](#43-usage)
- [5. Testing Your Skill](#5-testing-your-skill)
- [6. Submitting Your Changes](#6-submitting-your-changes)
- [7. Guidelines for Good Skills](#7-guidelines-for-good-skills)

## 1. Getting Started

Before contributing, familiarize yourself with:

- [Agent Skills Specification](https://agentskills.io/specification)
- Existing skills in [skills/](skills/)
- The [README.md](README.md) for repository structure

## 2. Adding a New Skill

To add a new skill:

1. **Create a directory** for your skill in `skills/`:

   ```bash
   mkdir -p skills/your-skill-name
   ```

2. **Create a SKILL.md file** in your skill directory:

   ```bash
   touch skills/your-skill-name/SKILL.md
   ```

3. **Follow the skill template structure** (see below)

4. **Update the skills README** at `skills/README.md` to include your new skill

5. **Update the main README.md** to list your skill in the catalog

## 3. Skill Structure

Each `SKILL.md` file should follow this structure:

```markdown
---
name: skill-name
description: Brief description of what this skill does and when to use it.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "trigger phrase 1"
      - "trigger phrase 2"
    match:
      languages: ["language1", "language2"]
      paths: ["path/pattern/**/*.ext"]
      prompt_regex: "(?i)(regex|pattern)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Skill Name

Brief description of the skill's purpose.

## Table of Contents

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
- [4. Workflow](#4-workflow)
- [5. Style Guide](#5-style-guide)
- [6. Template](#6-template)
- [7. References](#7-references)

## 1. Benefits

List the key benefits of using this skill.

## 2. Principles

Core principles that guide the use of this skill.

## 3. Patterns

Common patterns and best practices.

## 4. Workflow

Step-by-step workflow for applying this skill.

## 5. Style Guide

Style conventions and guidelines.

## 6. Template

Provide templates and code examples.

## 7. References

Links to relevant documentation and resources.
```

## 4. Metadata Guidelines

### 4.1. Version

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to the skill structure or behavior
- **MINOR**: New features or significant improvements
- **PATCH**: Bug fixes or minor improvements

### 4.2. Activation

- **implicit**: Set to `true` for skills that should activate automatically
- **priority**: Higher numbers = higher priority (1-10 scale)
- **triggers**: Key phrases that should activate this skill
- **match.languages**: Programming languages this skill applies to
- **match.paths**: File path patterns where this skill is relevant
- **match.prompt_regex**: Regular expression for matching user prompts

### 4.3. Usage

- **load_on_prompt**: Whether to load skill immediately when activated
- **autodispatch**: Whether to automatically apply the skill

## 5. Testing Your Skill

Before submitting:

1. **Validate the YAML frontmatter** is properly formatted
2. **Check that all links** in the skill documentation work
3. **Test the skill** in a real project context if possible
4. **Verify activation triggers** are appropriate and not too broad
5. **Ensure language/path patterns** are accurate

You can use the skills CLI to validate:

```bash
# Install skills CLI (if available)
npm install -g @agentskills/cli

# Validate your skill
skills validate skills/your-skill-name/SKILL.md
```

## 6. Submitting Your Changes

1. **Fork the repository**
2. **Create a feature branch**:

   ```bash
   git checkout -b feature/add-your-skill-name
   ```

3. **Make your changes** following the guidelines above
4. **Commit with descriptive messages**:

   ```bash
   git commit -m "Add skill for [skill name]"
   ```

5. **Push to your fork**:

   ```bash
   git push origin feature/add-your-skill-name
   ```

6. **Open a Pull Request** with:
   - Clear description of the skill
   - Use cases and examples
   - Any dependencies or prerequisites

## 7. Guidelines for Good Skills

- **Specific and Focused**: Each skill should address a specific task or domain
- **Well-Documented**: Provide clear instructions, templates, and examples
- **Practical**: Include real-world patterns and best practices
- **Language-Specific**: Target specific programming languages or frameworks when appropriate
- **Maintainable**: Use clear structure and organization that's easy to update
- **Tested**: Verify the skill works as expected in real scenarios

Thank you for contributing to making AI coding agents more capable and effective!
