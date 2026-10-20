---
name: google-go-style-guide
description: Apply Google Go style guidance when writing, reviewing, or refactoring Go code, auditing naming, formatting, errors, interfaces, concurrency, or package organization. Use for Google Go style requests; preserve repository conventions and delegate testing and API documentation to their dedicated skills.
---

# Google Go Style Guide

> Apply this third-party adaptation of Google style guidance within the target project's conventions. Code blocks illustrate individual rules; supply project-specific types and imports before running them.

## Workflow

1. Inspect repository instructions, nearby code, formatter and linter settings, and the supported language version before proposing edits. Give explicit project requirements precedence and explain any conflict with Google guidance.
2. Read [the companion guide](references/go.md) for the relevant topic. Keep changes scoped to the requested files and preserve behavior and public APIs unless a change is explicitly requested.
3. Separate automatic formatting from rules requiring judgment. Use existing project tools; do not introduce dependencies or rewrite tool configuration solely to enforce this skill.
4. For reviews, report file and line, the applicable rule, and a concrete correction. Distinguish project-specific choices from defects.
5. Run the existing formatter, relevant lint checks, and affected tests when available. Report the commands and results, including checks that could not run.

## Golden Rules

1. **Run `gofmt` before commit** — formatting is non-negotiable
2. **Choose names by scope and clarity** — use `i`, `err`, or `ctx` where clear
3. **Error handling, not exceptions** — handle errors explicitly
4. **Interfaces for abstraction** — define small interfaces at the consumer when needed; prefer concrete return types when appropriate
5. **Defer for cleanup** — ensure resources are released
6. **Explicit is better** — avoid magic, prefer clarity
7. **Package names: lowercase, single word** — no underscores

## Quick Reference

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Packages | lowercase | `package user` |
| Files | lowercase_underscore | `user_service.go` |
| Types | UpperCamelCase | `UserService` |
| Functions/Methods | UpperCamelCase (exported) | `GetUser` |
| Functions/Methods | lowerCamelCase (unexported) | `getUserByID` |
| Variables | lowerCamelCase | `userCount` |
| Constants | MixedCaps (exported or unexported) | `MaxRetries`, `defaultTimeout` |
| Interfaces | MixedCaps; -er for single-method roles | `Reader`, `Writer` |

### Variables

```go
// ✓ CORRECT - short names in small scopes
for i := 0; i < 10; i++ {
	// ...
}

// ✓ CORRECT - descriptive names in larger scopes
func ProcessUserData(userRepository UserRepository) error {
	// ...
}

// Prefer a shorter name when its meaning remains clear
for index := 0; index < 10; index++ {
	// ...
}
```

### Error Handling

```go
// ✓ CORRECT - handle errors explicitly
user, err := getUser(id)
if err != nil {
	return nil, fmt.Errorf("failed to get user: %w", err)
}

// ✗ INCORRECT - ignoring errors
user, _ := getUser(id)
```

### Functions

```go
// ✓ CORRECT - multiple return values
func GetUser(id int) (*User, error) {
	// ...
}

// ✓ CORRECT - named return values for clarity
func ParseConfig(path string) (cfg *Config, err error) {
	// ...
}
```

### Interfaces

```go
// ✓ CORRECT - small, focused interfaces
type Reader interface {
	Read(p []byte) (n int, err error)
}

// Accept a focused interface; return a concrete result where appropriate
func ProcessData(r Reader) (*Result, error) {
	// ...
}
```

### Defer

```go
// ✓ CORRECT - defer for cleanup
func ReadFile(path string) ([]byte, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	return io.ReadAll(f)
}
```

### Goroutines and Channels

```go
// ✓ CORRECT - use context for cancellation
func ProcessItems(ctx context.Context, items []Item) error {
	for _, item := range items {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			if err := process(item); err != nil {
				return err
			}
		}
	}
	return nil
}

// ✓ CORRECT - buffered channels when appropriate
results := make(chan Result, len(items))
```

### Package Organization

```go
// ✓ CORRECT - package comment
// Package user provides user management functionality.
package user

// ✓ CORRECT - group imports
import (
	"context"
	"fmt"

	"github.com/pkg/errors"

	"myapp/internal/db"
)
```

## Common Mistakes

| Mistake | Correct Approach |
|---|---|
| Ignoring errors | Handle errors explicitly |
| Unclear local names | Choose names appropriate to scope |
| Panic for normal errors | Return errors |
| Naked returns | Use explicit returns |
| Not running gofmt | Always format code |
| Underscores in package names | Use single lowercase word |

## Scope and Validation

Use the dedicated Go testing and API documentation skills for test design and detailed godoc work. For style edits, format only changed files with `gofmt -w <files>` and use the project's existing `go vet` and test targets. Review cancellation, goroutine termination, channel ownership, and synchronization manually; formatting cannot establish concurrency safety.

## Full Guide

Read [the companion guide](references/go.md) for additional examples. Treat both files as summaries; consult the primary Google guide for exceptions or disputed rules.

## Sources and License

Adapted from [TestDino's Go skill](https://github.com/testdino-hq/google-styleguides-skills/tree/8674a2a2186a02f86852e061f6166a500ae30f7c/go) at commit `8674a2a2186a02f86852e061f6166a500ae30f7c`, including its companion guide. Copyright (c) 2026 TestDino; see [LICENSE](LICENSE) for the preserved MIT terms. This is a third-party adaptation, not an official Google skill.

Local changes rename the skill, relocate the companion guide, add repository-aware workflow and validation, and qualify oversimplified rules. Consult the [primary Google Go Style Guide](https://google.github.io/styleguide/go/) for authoritative guidance. Keep this attribution and the license when redistributing either file.
