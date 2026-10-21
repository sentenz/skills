# Google Go Style Guide

> Source: https://google.github.io/styleguide/go/

- [1. Golden Rules](#1-golden-rules)
- [2. Naming](#2-naming)
- [3. Error Handling](#3-error-handling)
- [4. Interfaces](#4-interfaces)
- [5. Structs](#5-structs)
- [6. Goroutines](#6-goroutines)
- [7. Testing (Table-Driven)](#7-testing-table-driven)
- [8. Common Mistakes](#8-common-mistakes)

## 1. Golden Rules

1. **Run `gofmt`** — all code must be formatted with gofmt
2. **Handle errors explicitly** — never ignore returned errors with `_`
3. **Comment exported identifiers** — all exported names must have doc comment
4. **Return early** — prefer guard clauses over deep nesting
5. **Keep interfaces small** — one or two methods is ideal
6. **Name things clearly** — short names for short scopes

---

## 2. Naming

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

## 3. Error Handling

```go
// CORRECT - always handle errors
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
file, _ := os.Open("data.txt") // never ignore errors
```

---

## 4. Interfaces

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

## 5. Structs

```go
// CORRECT
type User struct {
    ID    int
    Name  string
    Email string
}

// CORRECT - struct literal with field names
user := User{
    ID:    1,
    Name:  "Alice",
    Email: "alice@example.com",
}

// INCORRECT - positional struct literal
user := User{1, "Alice", "alice@example.com"} // fragile
```

---

## 6. Goroutines

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

## 7. Testing (Table-Driven)

```go
// CORRECT - table-driven tests
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("add(%d, %d) = %d; want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

---

## 8. Common Mistakes

| Mistake                    | Correct Approach                   |
| -------------------------- | ---------------------------------- |
| Ignoring errors with _     | Always handle returned errors      |
| Large interfaces           | Keep to 1-2 methods                |
| Positional struct literals | Use field names                    |
| No doc comments on exports | Add doc comment to every export    |
| UPPER_SNAKE_CASE constants | Use UpperCamelCase                 |
| Leaking goroutines         | Always ensure goroutines terminate |
