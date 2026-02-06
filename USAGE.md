# Usage Examples

This document provides examples of how to use the agent skills from this repository in your projects.

- [1. Basic Usage](#1-basic-usage)
- [2. Integration Methods](#2-integration-methods)
  - [2.1. Direct Copy](#21-direct-copy)
  - [2.2. Using Skills CLI](#22-using-skills-cli)
  - [2.3. Git Submodule](#23-git-submodule)
- [3. Customizing Skills](#3-customizing-skills)
- [4. Customizing AGENTS.md](#4-customizing-agentsmd)
- [5. Example Projects](#5-example-projects)

## 1. Basic Usage

Agent skills are designed to be used by AI coding agents (like GitHub Copilot, Cursor, or custom agents) to provide context-specific guidance for common development tasks.

**Key Benefits:**
- **Consistent Patterns**: Ensures uniform code style and structure across your project
- **Best Practices**: Embeds industry-standard patterns and principles
- **Automated Guidance**: AI agents automatically apply skills based on context
- **Reusable**: Share skills across multiple projects and teams

## 2. Integration Methods

### 2.1. Direct Copy

The simplest method is to copy skills directly to your project:

```bash
# Copy all skills
cp -r path/to/skills/.github/skills .github/

# Or copy specific skills only
mkdir -p .github/skills
cp -r path/to/skills/.github/skills/cpp-unit-testing .github/skills/
cp -r path/to/skills/.github/skills/cpp-api-documentation .github/skills/
```

### 2.2. Using Skills CLI

If the skills CLI is available, you can use it for better management:

```bash
# Install the skills CLI
npm install -g @agentskills/cli

# Initialize skills in your project
cd your-project
skills init

# Add specific skills
skills add cpp-unit-testing
skills add cpp-api-documentation

# List available skills in your project
skills list

# Update skills from the catalog
skills update

# Validate skill definitions
skills validate
```

### 2.3. Git Submodule

For dynamic updates, use a git submodule:

```bash
# Add this repository as a submodule
git submodule add https://github.com/sentenz/skills .github/skills-catalog

# Link specific skills
mkdir -p .github/skills
ln -s ../skills-catalog/.github/skills/cpp-unit-testing .github/skills/cpp-unit-testing

# Update skills from the catalog
git submodule update --remote
```

## 3. Customizing Skills

Skills can be customized for your specific project needs:

1. **Copy the skill** to your project's `.github/skills/` directory
2. **Modify the skill** to match your project's conventions
3. **Update metadata** (version, triggers, paths) as needed
4. **Commit the customized skill** to your repository

**Example: Customizing Unit Testing Paths**

```yaml
---
name: cpp-unit-testing
# ... other metadata ...
metadata:
  activation:
    match:
      paths: 
        - "tests/**/*_test.cpp"      # Original
        - "my_tests/**/*.test.cpp"   # Add custom path
```

## 4. Customizing AGENTS.md

The `AGENTS.md` template provides a starting point for project-specific AI agent instructions:

1. **Copy AGENTS.md** to your project root
2. **Fill in project-specific details**:
   - Tech stack and versions
   - Project directory structure
   - Task runner commands (make, npm, etc.)
   - Development workflows
   - Links to project skills

3. **Add project-specific guidance**:
   - Coding conventions
   - Architecture patterns
   - Testing strategies
   - Deployment procedures

**Example AGENTS.md for a Go Project:**

```markdown
# AGENTS.md

## 1. Tech Stack

### 1.1. Programming Language

- **Go**
  > Version: Go 1.22+

### 1.2. Testing

- Standard Go testing package
- See [Go Unit Testing](.github/skills/go-unit-testing/SKILL.md)

## 2. Project Layout

```
.
├── cmd/           # Main applications
├── pkg/           # Public libraries
├── internal/      # Private code
└── .github/
    └── skills/    # Agent skills
```

## 3. Task Runners

- `make test` - Run all tests
- `make lint` - Run linters
- `make build` - Build binaries

## 4. Agent Skills

Available skills for this project:
- [Go Unit Testing](.github/skills/go-unit-testing/SKILL.md)
- [Go API Documentation](.github/skills/go-api-documentation/SKILL.md)
```

## 5. Example Projects

### C++ Project with GoogleTest

```
my-cpp-project/
├── .github/
│   └── skills/
│       ├── cpp-unit-testing/      # From this repo
│       ├── cpp-mock-testing/      # From this repo
│       └── cpp-api-documentation/ # From this repo
├── src/
│   ├── module/
│   │   ├── header.hpp
│   │   └── header_test.cpp    # Tests use cpp-unit-testing skill patterns
├── AGENTS.md                   # Customized from template
└── README.md
```

**Agent Behavior:**
- When editing `*_test.cpp` files, the agent automatically uses the cpp-unit-testing skill
- When editing `*.hpp` files, the agent uses cpp-api-documentation skill
- Trigger phrases like "add unit test" or "document this API" activate skills

### Go Project

```
my-go-project/
├── .github/
│   └── skills/
│       ├── go-unit-testing/       # From this repo
│       ├── go-benchmark-testing/  # From this repo
│       └── go-api-documentation/  # From this repo
├── pkg/
│   └── mypackage/
│       ├── mypackage.go
│       └── mypackage_test.go      # Tests use go-unit-testing skill patterns
├── AGENTS.md                       # Customized from template
└── README.md
```

**Agent Behavior:**
- When editing `*_test.go` files, the agent uses go-unit-testing skill
- Trigger phrases like "add benchmark" activate go-benchmark-testing skill
- Documentation comments follow godoc conventions from go-api-documentation skill

### Multi-Language Project

```
my-mixed-project/
├── .github/
│   └── skills/
│       ├── cpp-unit-testing/       # C++ testing
│       ├── go-unit-testing/        # Go testing
│       ├── cpp-api-documentation/  # C++ docs
│       └── go-api-documentation/   # Go docs
├── backend/                         # Go code
│   └── pkg/
│       └── service/
├── engine/                          # C++ code
│   └── src/
│       └── core/
├── AGENTS.md
└── README.md
```

**Agent Behavior:**
- Agent selects appropriate skill based on file path and language
- C++ files in `engine/` use C++ skills
- Go files in `backend/` use Go skills
- Skills are language-aware through metadata matching

## Tips for Effective Usage

1. **Start Small**: Begin with one or two skills that address your biggest pain points
2. **Customize Gradually**: Use skills as-is initially, then customize as you learn what works
3. **Document Conventions**: Use AGENTS.md to document any project-specific variations
4. **Update Regularly**: Keep skills synchronized with your evolving best practices
5. **Share with Team**: Ensure all team members understand available skills and conventions
6. **Provide Feedback**: Contribute improvements back to the skills repository

## Getting Help

- Check the [main README](README.md) for skill catalog and descriptions
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for creating custom skills
- Review individual `SKILL.md` files for detailed patterns and templates
- Refer to [Agent Skills Specification](https://agentskills.io/specification) for format details
