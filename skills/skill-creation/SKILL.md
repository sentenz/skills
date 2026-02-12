---
name: skill-creation
description: Automates Agent Skill (SKILL.md) creation following the Agent Skills specification and repository conventions. Use when creating new skills, documenting AI agent capabilities, or when the user mentions adding skills, creating SKILL.md, or skill development.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "create skill"
      - "add skill"
      - "new skill"
      - "skill creation"
      - "SKILL.md"
      - "agent skill"
    match:
      languages: ["markdown"]
      paths: ["skills/**/SKILL.md", "**/SKILL.md"]
      prompt_regex: "(?i)(create skill|add skill|new skill|skill creation|SKILL\\.md|agent skill)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Skill Creation

Instructions for AI coding agents on creating Agent Skills (SKILL.md) following the Agent Skills specification and repository conventions.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
  - [3.1. Skill Structure](#31-skill-structure)
  - [3.2. Metadata Guidelines](#32-metadata-guidelines)
  - [3.3. Content Organization](#33-content-organization)
- [4. Workflow](#4-workflow)
- [5. Style Guide](#5-style-guide)
- [6. Template](#6-template)
  - [6.1. Full SKILL.md Template](#61-full-skillmd-template)
  - [6.2. Metadata Template](#62-metadata-template)
  - [6.3. Section Templates](#63-section-templates)
- [7. References](#7-references)

## 1. Benefits

- Consistency
  > Ensures all skills follow the Agent Skills specification and maintain uniform structure across the repository.

- Discoverability
  > Well-defined activation triggers and metadata enable AI agents to automatically discover and use skills.

- Maintainability
  > Clear documentation structure makes skills easy to update and extend as requirements evolve.

- Reusability
  > Modular skill design allows skills to be shared across projects and adapted to different contexts.

## 2. Principles

- Specific and Focused
  > Each skill should address a specific task or domain, avoiding scope creep and maintaining clear purpose.

- Well-Documented
  > Provide clear instructions, templates, and examples that AI agents can follow without ambiguity.

- Practical
  > Include real-world patterns, best practices, and concrete examples that agents can apply immediately.

- Language-Specific
  > Target specific programming languages, frameworks, or tools when appropriate for precision.

- Tested
  > Verify the skill works as expected by testing activation triggers and validating content accuracy.

## 3. Patterns

### 3.1. Skill Structure

Each `SKILL.md` file follows a consistent structure:

- YAML Frontmatter
  > Contains metadata including name, description, version, activation rules, and usage settings.

- Title and Introduction
  > Clear title matching the skill name and brief description of the skill's purpose.

- Table of Contents
  > Navigable links to all major sections for easy reference.

- Content Sections
  > Standard sections: Benefits, Principles, Patterns, Workflow, Style Guide, Template, References.

### 3.2. Metadata Guidelines

- Version
  > Use semantic versioning (MAJOR.MINOR.PATCH) to track skill evolution.

- Activation
  > Define appropriate triggers, language matches, path patterns, and regex for automatic activation.

- Usage
  > Specify whether the skill should load on prompt and autodispatch behavior.

### 3.3. Content Organization

- Benefits
  > List key advantages of using the skill with clear explanations.

- Principles
  > Core guidelines that govern skill application.

- Patterns
  > Common approaches, best practices, and design patterns.

- Workflow
  > Step-by-step process for applying the skill in practice.

- Style Guide
  > Coding conventions, formatting rules, and style preferences.

- Template
  > Concrete code examples, file templates, and boilerplate.

- References
  > Links to relevant documentation, specifications, and resources.

## 4. Workflow

1. Identify Need

    Determine the specific capability or task that requires a new skill.

2. Create Directory

    ```bash
    mkdir -p skills/<skill-name>
    ```

3. Create SKILL.md

    Use the [template](#6-template) to create the skill file:

    ```bash
    touch skills/<skill-name>/SKILL.md
    ```

4. Define Metadata

    Set appropriate name, description, version, and activation rules in YAML frontmatter.

5. Write Content

    Fill in all required sections following the structure and guidelines.

6. Update Catalog

    Add the new skill to:
    - `skills/README.md` in the appropriate category
    - Main `README.md` in the skills catalog
    - `.agentskills.yml` configuration file

7. Validate

    Check YAML frontmatter formatting and verify all links work.

8. Test

    Test activation triggers and ensure the skill activates in appropriate contexts.

## 5. Style Guide

- Markdown Format
  > Use standard Markdown syntax for all content with YAML frontmatter for metadata.

- YAML Frontmatter
  > Must be properly formatted with valid YAML syntax enclosed in `---` delimiters.

- Naming Convention
  > Use lowercase kebab-case for skill names (e.g., `cpp-unit-testing`, `skill-creation`).

- Description
  > Write clear, concise descriptions that explain what the skill does and when to use it.

- Activation Triggers
  > Choose specific, non-overlapping trigger phrases that accurately represent the skill's purpose.

- Language Matching
  > Specify programming languages as lowercase strings (e.g., `cpp`, `go`, `python`, `markdown`).

- Path Patterns
  > Use glob patterns for file path matching (e.g., `src/**/*_test.cpp`).

- Regular Expressions
  > Use case-insensitive regex patterns with `(?i)` flag for prompt matching.

- Section Headers
  > Use consistent header levels and numbering (e.g., `## 1. Benefits`, `### 1.1. Subsection`).

- Code Blocks
  > Always specify the language for syntax highlighting (e.g., ` ```cpp`, ` ```bash`).

- Links
  > Use relative links for internal references and absolute URLs for external resources.

- Lists
  > Use blockquotes (`>`) for descriptions under bullet points for visual clarity.

## 6. Template

Use these templates when creating new skills. Replace placeholders with actual values.

### 6.1. Full SKILL.md Template

```markdown
---
name: skill-name
description: Brief description of what this skill does and when to use it. Include activation context and user mentions.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "trigger phrase 1"
      - "trigger phrase 2"
      - "trigger phrase 3"
    match:
      languages: ["language1", "language2"]
      paths: ["path/pattern/**/*.ext"]
      prompt_regex: "(?i)(regex|pattern|match)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Skill Name

Brief description of the skill's purpose and what AI agents can accomplish using it.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
- [4. Workflow](#4-workflow)
- [5. Style Guide](#5-style-guide)
- [6. Template](#6-template)
- [7. References](#7-references)

## 1. Benefits

- Benefit 1
  > Explanation of the first key benefit.

- Benefit 2
  > Explanation of the second key benefit.

- Benefit 3
  > Explanation of the third key benefit.

## 2. Principles

- Principle 1
  > Core principle that guides the use of this skill.

- Principle 2
  > Another important principle to follow.

## 3. Patterns

### 3.1. Pattern Name

Description of a common pattern or best practice.

- Element 1
  > Details about this pattern element.

- Element 2
  > Details about this pattern element.

### 3.2. Another Pattern

Description of another pattern relevant to this skill.

## 4. Workflow

1. Step 1

    Description and details for the first step.

2. Step 2

    Description and details for the second step.

3. Step 3

    Description and details for the third step.

## 5. Style Guide

- Style Element 1
  > Explanation of style convention or guideline.

- Style Element 2
  > Explanation of another style convention.

- Style Element 3
  > Explanation of another style convention.

## 6. Template

Provide templates and code examples here.

### 6.1. Template Name

```language
// Template code or example
```

### 6.2. Another Template

```language
// Another template code or example
```

## 7. References

- [Documentation Name](https://example.com) - Brief description.
- [Specification](https://agentskills.io/specification) - Agent Skills specification.
```

### 6.2. Metadata Template

```yaml
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
```

#### Version Guidelines

Use semantic versioning:

- **MAJOR** (1.0.0): Breaking changes to skill structure or behavior
- **MINOR** (0.1.0): New features or significant improvements
- **PATCH** (0.0.1): Bug fixes or minor improvements

#### Activation Guidelines

- **implicit**: Set to `true` for skills that should activate automatically
- **priority**: Higher numbers = higher priority (1-10 scale, use 1 for most skills)
- **triggers**: Key phrases that should activate this skill (3-10 phrases recommended)
- **match.languages**: Programming languages this skill applies to
- **match.paths**: File path patterns where this skill is relevant
- **match.prompt_regex**: Regular expression for matching user prompts

#### Usage Guidelines

- **load_on_prompt**: Whether to load skill immediately when activated (typically `true`)
- **autodispatch**: Whether to automatically apply the skill (typically `true`)

### 6.3. Section Templates

#### Benefits Section Template

```markdown
## 1. Benefits

- Benefit Name
  > Clear explanation of this benefit and why it matters.

- Another Benefit
  > Clear explanation of this benefit and its value.
```

#### Principles Section Template

```markdown
## 2. Principles

- Principle Name
  > Core principle that guides skill application.

- Another Principle
  > Another important guiding principle.
```

#### Patterns Section Template

```markdown
## 3. Patterns

### 3.1. Pattern Name

Description of the pattern and when to use it.

- Element 1
  > Details about this element.

- Element 2
  > Details about this element.
```

#### Workflow Section Template

```markdown
## 4. Workflow

1. Step Name

    Detailed description of this step with examples or commands.

2. Next Step

    Detailed description of the next step.

3. Final Step

    Detailed description of the final step.
```

#### Style Guide Section Template

```markdown
## 5. Style Guide

- Style Guideline 1
  > Explanation and examples.

- Style Guideline 2
  > Explanation and examples.
```

#### Template Section Template

    ## 6. Template

    ### 6.1. Template Name

    ```language
    // Code template with placeholders
    // Replace <placeholder> with actual values
    ```

    ### 6.2. Another Template

    ```language
    // Another code template
    ```

#### References Section Template

```markdown
## 7. References

- [Resource Name](https://example.com) - Brief description.
- [Another Resource](https://example.com) - Brief description.
- Agent Skills [Specification](https://agentskills.io/specification) page.
```

## 7. References

- Agent Skills [Specification](https://agentskills.io/specification) page.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Repository contribution guidelines.
- [AGENTS.md](https://agents.md/) specification page.
- Existing skills in [skills/](../) directory for reference examples.
