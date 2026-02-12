---
name: skill-creation
description: Automates the creation of Agent Skills (SKILL.md) by codifying CONTRIBUTING.md guidelines into a discoverable, reusable skill. Use when creating new skills, modifying skill structures, or when the user mentions adding a new skill, creating SKILL.md, or skill documentation.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "create skill"
      - "new skill"
      - "add skill"
      - "skill.md"
      - "skill creation"
      - "skill documentation"
      - "agent skill"
    match:
      languages: ["markdown"]
      paths: ["skills/**/*SKILL.md", "**/SKILL.md"]
      prompt_regex: "(?i)(create skill|new skill|add skill|skill\\.md|skill creation|skill documentation|agent skill)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Skill Creation

Instructions for AI coding agents on automating the creation of Agent Skills (SKILL.md) files following the Agent Skills specification and repository guidelines.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. Specific and Focused](#21-specific-and-focused)
  - [2.2. Well-Documented](#22-well-documented)
  - [2.3. Practical](#23-practical)
  - [2.4. Language-Specific](#24-language-specific)
  - [2.5. Maintainable](#25-maintainable)
  - [2.6. Tested](#26-tested)
- [3. Patterns](#3-patterns)
  - [3.1. Skill Structure](#31-skill-structure)
  - [3.2. Metadata Guidelines](#32-metadata-guidelines)
  - [3.3. Content Organization](#33-content-organization)
- [4. Workflow](#4-workflow)
- [5. Style Guide](#5-style-guide)
- [6. Template](#6-template)
  - [6.1. SKILL.md Template](#61-skillmd-template)
- [7. References](#7-references)

## 1. Benefits

- Consistency
  > Ensures uniform structure across all skills using standardized templates and patterns that follow the Agent Skills specification.

- Discoverability
  > Proper metadata and activation triggers make skills easily discoverable by AI agents based on context, language, and user intent.

- Reusability
  > Well-structured skills can be shared across projects and teams, reducing duplication and accelerating AI agent capabilities.

- Maintainability
  > Clear organization and documentation make skills easy to update, extend, and improve over time.

- Quality
  > Following established guidelines ensures skills are well-tested, practical, and provide real value to AI agents.

## 2. Principles

### 2.1. Specific and Focused

Each skill should address a specific task or domain rather than being overly broad.

- Single Responsibility
  > Focus on one primary capability or workflow (e.g., unit testing, API documentation, benchmarking).

- Clear Purpose
  > The skill's purpose should be immediately evident from the name and description.

### 2.2. Well-Documented

Provide clear instructions, templates, and examples that AI agents can follow.

- Comprehensive Instructions
  > Include all necessary information for the agent to successfully complete the task.

- Examples
  > Provide concrete examples and templates that demonstrate proper usage.

### 2.3. Practical

Include real-world patterns and best practices that work in production environments.

- Battle-Tested Patterns
  > Use proven approaches that have been validated in real projects.

- Actionable Guidance
  > Provide specific, actionable steps rather than abstract concepts.

### 2.4. Language-Specific

Target specific programming languages or frameworks when appropriate.

- Language Conventions
  > Follow the idioms and conventions of the target programming language.

- Framework Integration
  > Integrate with the standard tools and frameworks for that language ecosystem.

### 2.5. Maintainable

Use clear structure and organization that's easy to update and extend.

- Modular Organization
  > Separate different aspects of the skill into distinct sections.

- Version Control
  > Use semantic versioning to track changes and breaking updates.

### 2.6. Tested

Verify the skill works as expected in real scenarios.

- Validation
  > Test that the YAML frontmatter is properly formatted and metadata is correct.

- Real-World Testing
  > Apply the skill in actual project contexts to ensure it produces correct results.

## 3. Patterns

### 3.1. Skill Structure

Each SKILL.md file follows a consistent structure with YAML frontmatter and markdown content.

- YAML Frontmatter
  > Contains metadata including name, description, version, activation rules, and usage settings.

- Markdown Content
  > Organized into standard sections: Benefits, Principles, Patterns, Workflow, Style Guide, Template, and References.

### 3.2. Metadata Guidelines

Metadata controls how and when the skill is activated by AI agents.

- Version
  > Use semantic versioning (MAJOR.MINOR.PATCH) to indicate the maturity and compatibility of the skill.

- Activation
  > Configure implicit activation, priority, triggers, and matching rules for languages, paths, and prompts.

- Usage
  > Set load_on_prompt and autodispatch flags to control skill loading behavior.

### 3.3. Content Organization

Content should be organized to maximize clarity and usability.

- Progressive Detail
  > Start with high-level concepts and progressively add detail.

- Actionable Sections
  > Each section should provide concrete guidance that agents can follow.

- Templates and Examples
  > Include ready-to-use templates that agents can customize for specific use cases.

## 4. Workflow

1. Identify Skill Need

    Determine what specific task or capability needs to be automated (e.g., testing, documentation, code generation).

2. Create Skill Directory

    Create a new directory in `skills/` with a descriptive, kebab-case name:

    ```bash
    mkdir -p skills/your-skill-name
    ```

3. Create SKILL.md File

    Create the `SKILL.md` file in the skill directory:

    ```bash
    touch skills/your-skill-name/SKILL.md
    ```

4. Add YAML Frontmatter

    Add the YAML frontmatter with appropriate metadata:
    - Choose a descriptive name matching the directory name
    - Write a clear description explaining what the skill does and when to use it
    - Set version to "1.0.0" for new skills
    - Configure activation triggers, language matches, and path patterns
    - Set usage flags appropriately

5. Add Content Sections

    Structure the skill content following the template:
    - **Benefits**: List key benefits of using this skill
    - **Principles**: Core principles guiding the skill's use
    - **Patterns**: Common patterns and best practices
    - **Workflow**: Step-by-step workflow for applying the skill
    - **Style Guide**: Style conventions and guidelines
    - **Template**: Provide templates and code examples
    - **References**: Links to relevant documentation

6. Update Catalogs

    Update the skills catalog in multiple files:
    - Update `skills/README.md` to include the new skill with description
    - Update main `README.md` to list the skill in the appropriate category
    - Update `.agentskills.yml` to register the skill in the catalog

7. Validate Skill

    Validate the skill structure and content:
    - Check YAML frontmatter is properly formatted
    - Verify all links work correctly
    - Test activation triggers are appropriate
    - Ensure language/path patterns are accurate

8. Test in Context

    Test the skill in a real project context:
    - Verify it activates correctly based on triggers
    - Ensure the guidance produces correct results
    - Validate templates work as expected

## 5. Style Guide

- File Naming
  > Use `SKILL.md` (all caps) as the filename in each skill directory.

- Directory Naming
  > Use kebab-case for skill directory names (e.g., `cpp-unit-testing`, `skill-creation`).

- YAML Format
  > Use proper YAML syntax with 2-space indentation. Ensure the frontmatter is enclosed in `---` delimiters.

- Markdown Headers
  > Use numbered sections in the table of contents and section headers for consistent navigation.

- Code Blocks
  > Use fenced code blocks with appropriate language identifiers for syntax highlighting.

- Lists and Quotes
  > Use blockquotes (`>`) for descriptions under list items to maintain consistent formatting.

- Links
  > Use markdown links for all references. Prefer relative paths for internal links within the repository.

- Semantic Versioning
  > Follow semantic versioning for the version field:
  - **MAJOR**: Breaking changes to skill structure or behavior
  - **MINOR**: New features or significant improvements
  - **PATCH**: Bug fixes or minor improvements

## 6. Template

### 6.1. SKILL.md Template

```markdown
---
name: skill-name
description: Brief description of what this skill does and when to use it. Include trigger keywords and use cases.
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
      paths: ["path/pattern/**/*.ext", "another/path/**/*"]
      prompt_regex: "(?i)(regex|pattern|for|matching)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Skill Name

Brief description of the skill's purpose and what it helps AI agents accomplish.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
- [4. Workflow](#4-workflow)
- [5. Style Guide](#5-style-guide)
- [6. Template](#6-template)
- [7. References](#7-references)

## 1. Benefits

List the key benefits of using this skill:

- Benefit 1
  > Description of the benefit and its value.

- Benefit 2
  > Description of the benefit and its value.

- Benefit 3
  > Description of the benefit and its value.

## 2. Principles

Core principles that guide the use of this skill:

### 2.1. Principle Name

Description of the principle.

- Aspect 1
  > Details about this aspect of the principle.

- Aspect 2
  > Details about this aspect of the principle.

### 2.2. Another Principle

Description of another principle with similar structure.

## 3. Patterns

Common patterns and best practices:

### 3.1. Pattern Name

Description of the pattern.

- Pattern Detail 1
  > Explanation of this pattern detail.

- Pattern Detail 2
  > Explanation of this pattern detail.

### 3.2. Another Pattern

Description of another pattern with similar structure.

## 4. Workflow

Step-by-step workflow for applying this skill:

1. Step Name

    Description of what to do in this step.

2. Another Step

    Description of the next step.

3. Validation Step

    How to validate the results.

## 5. Style Guide

Style conventions and guidelines specific to this skill:

- Convention 1
  > Description of the style convention.

- Convention 2
  > Description of another convention.

- Tool or Framework
  > Specific tool or framework to use with links to documentation.

## 6. Template

Provide templates and code examples that agents can use:

### 6.1. Template Name

```language
// Template code with placeholders
<placeholder_name>

// Example usage
actual_code_example
```

### 6.2. Another Template

Additional templates as needed.

## 7. References

Links to relevant documentation and resources:

- [Documentation Name](https://example.com) - brief description.
- [Another Reference](https://example.com) - brief description.
```

## 7. References

- Agent Skills [Specification](https://agentskills.io/specification) page.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) guidelines for this repository.
- [AGENTS.md](https://agents.md/) specification page.
- Existing skills in [skills/](../) directory for examples.
