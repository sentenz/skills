# Google Go Style Guide

> Source: https://google.github.io/styleguide/go/

Read these examples as excerpts; supply project-specific types and imports before compiling or running them.

- [Golden Rules](#golden-rules)
- [1. Naming](#1-naming)
- [2. Error Handling](#2-error-handling)
- [3. Interfaces](#3-interfaces)
- [4. Structs](#4-structs)
- [5. Goroutines](#5-goroutines)
- [Common Mistakes](#common-mistakes)
- [Attribution](#attribution)

## Golden Rules

1. **Run `gofmt`** — all code must be formatted with gofmt
2. **Handle errors explicitly** — handle or propagate failures; document intentional discards
3. **Comment exported identifiers** — all exported names must have doc comment
4. **Return early** — prefer guard clauses over deep nesting
5. **Keep interfaces focused** — include the behavior the consumer needs
6. **Name things clearly** — short names for short scopes

---

## 1. Naming

```go
// packages: lowercase, no underscores
package userservice

// exported: UpperCamelCase
type UserService struct { }
func GetUser(id int) (*User, error) { return nil, nil }

// unexported: lowerCamelCase
type userRepository struct { }
func getUserByID(id int) (*User, error) { return nil, nil }

// constants: UpperCamelCase (not UPPER_SNAKE_CASE)
const MaxRetries = 3
const defaultTimeout = 30

// acronyms: all uppercase
type HTTPClient struct { }
func parseURL(raw string) string { return raw }
```

---

## 2. Error Handling

```go
// Handle errors before using returned resources
file, err := os.Open("data.txt")
if err != nil {
	return fmt.Errorf("opening data file: %w", err)
}
defer file.Close()

// CORRECT - wrap errors with context
func processUser(id int) error {
	user, err := getUser(id)
	if err != nil {
		return fmt.Errorf("processUser(%d): %w", id, err)
	}
	return nil
}

// INCORRECT - ignoring errors
file, _ := os.Open("data.txt") // handle or explain the error
```

---

## 3. Interfaces

```go
// CORRECT - small, focused interfaces
type Reader interface {
	Read(p []byte) (n int, err error)
}

// CORRECT - interface composition
type ReadWriter interface {
	Reader
	Writer
}

// AVOID - large interfaces (too many methods)
```

---

## 4. Structs

```go
// CORRECT
type User struct {
	ID	int
	Name  string
	Email string
}

// CORRECT - struct literal with field names
user := User{
	ID:	1,
	Name:  "Alice",
	Email: "alice@example.com",
}

// INCORRECT - positional struct literal
user := User{1, "Alice", "alice@example.com"} // fragile
```

---

## 5. Goroutines

```go
// CORRECT - always synchronize
var wg sync.WaitGroup

for _, item := range items {
	wg.Add(1)
	go func(item Item) {
		defer wg.Done()
		process(item)
	}(item)
}
wg.Wait()
```

---

## Common Mistakes

| Mistake | Correct Approach |
|---|---|
| Ignoring errors with _ | Handle or propagate errors; justify intentional discards |
| Large interfaces | Include only the methods needed by the consumer |
| Positional struct literals | Use field names |
| No doc comments on exports | Add doc comment to every export |
| UPPER_SNAKE_CASE constants | Use UpperCamelCase |
| Leaking goroutines | Always ensure goroutines terminate |

## Attribution

Adapted from [TestDino's companion guide](https://github.com/testdino-hq/google-styleguides-skills/blob/8674a2a2186a02f86852e061f6166a500ae30f7c/go/go.md). See [the skill](../SKILL.md#sources-and-license) for adaptation details and [LICENSE](../LICENSE) for the preserved MIT terms. This summary does not replace the primary Google guide.
