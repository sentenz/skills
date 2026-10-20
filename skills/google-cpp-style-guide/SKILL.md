---
name: google-cpp-style-guide
description: Apply Google C++ style guidance when writing, reviewing, or refactoring C++ headers and source files, auditing naming, formatting, classes, ownership, RAII, or smart pointers. Use for Google C++ style requests; preserve repository conventions, language version, and exception policy.
---

# Google C++ Style Guide

> Apply this third-party adaptation of Google style guidance within the target project's conventions. Code blocks illustrate individual rules; supply project-specific types and imports before running them.

## Workflow

1. Inspect repository instructions, nearby code, formatter and linter settings, and the supported language version before proposing edits. Give explicit project requirements precedence and explain any conflict with Google guidance.
2. Read [the companion guide](references/cpp.md) for the relevant topic. Keep changes scoped to the requested files and preserve behavior and public APIs unless a change is explicitly requested.
3. Separate automatic formatting from rules requiring judgment. Use existing project tools; do not introduce dependencies or rewrite tool configuration solely to enforce this skill.
4. For reviews, report file and line, the applicable rule, and a concrete correction. Distinguish project-specific choices from defects.
5. Run the existing formatter, relevant lint checks, and affected tests when available. Report the commands and results, including checks that could not run.

## Golden Rules

1. **Respect the project language standard** — avoid unsupported features and non-standard extensions
2. **80-character line limit** — for readability
3. **2-space indentation** — no tabs
4. **Use `const` where appropriate** — express intent; constness alone does not establish thread safety
5. **Follow the project exception policy** — Google style disallows exceptions; do not change an existing exception-based API as a style edit
6. **Smart pointers for ownership** — `std::unique_ptr` and `std::shared_ptr`
7. **Header guards** — use `PROJECT_PATH_FILE_H_` format

## Quick Reference

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Files | snake_case | `url_table.cc`, `url_table.h` |
| Classes/Structs | UpperCamelCase | `UserService` |
| Functions | UpperCamelCase | `GetUserById` |
| Variables | snake_case | `user_count` |
| Constants | kUpperCamelCase | `kMaxRetries` |
| Class members | snake_case_ | `user_name_` (trailing `_`) |
| Macros | UPPER_SNAKE_CASE | `MAX_BUFFER_SIZE` |

### Headers

```cpp
// ✓ CORRECT - self-contained header with guard
#ifndef FOO_BAR_BAZ_H_
#define FOO_BAR_BAZ_H_

#include <string>

class Baz {
 public:
  void DoSomething();
};

#endif  // FOO_BAR_BAZ_H_
```

Include order: related header → C system → C++ stdlib → other libs → your headers.

### Classes

```cpp
// ✓ CORRECT
class MyClass {
 public:
  explicit MyClass(int value);  // explicit for single-arg ctors
  ~MyClass();

  void DoSomething();
  int GetValue() const { return value_; }

 private:
  int value_;
  std::string name_;
};
```

### Smart Pointers

```cpp
// ✓ CORRECT - unique_ptr for exclusive ownership
std::unique_ptr<Foo> FooFactory();
void FooConsumer(std::unique_ptr<Foo> ptr);

// ✓ CORRECT - shared_ptr for shared ownership
std::shared_ptr<const Foo> immutable_foo;

// ✗ INCORRECT - avoid raw new/delete
Foo* foo = new Foo();  // avoid
delete foo;            // avoid
```

### Modern C++ Features

```cpp
// ✓ CORRECT - use auto for complex types
auto it = my_map.find(key);
auto widget = std::make_unique<Widget>(arg1, arg2);

// ✓ CORRECT - range-based for loops
for (const auto& item : container) {
  Process(item);
}

// ✓ CORRECT - nullptr, not NULL
Foo* ptr = nullptr;

// ✓ CORRECT - constexpr for compile-time constants
constexpr int kArraySize = 100;
```

### Functions

```cpp
// ✓ CORRECT - return type on same line
ReturnType ClassName::FunctionName(Type par_name1, Type par_name2) {
  DoSomething();
  return result;
}

// ✓ CORRECT - wrap long parameter lists (4-space indent)
ReturnType LongClassName::ReallyLongFunctionName(
    Type par_name1,
    Type par_name2,
    Type par_name3) {
  DoSomething();
}
```

### Formatting

```cpp
// ✓ CORRECT - braces and spacing
if (condition) {
  DoSomething();
} else {
  DoSomethingElse();
}

// ✓ CORRECT - pointer/reference alignment (attached to type)
char* c;
const std::string& str;
```

## Common Mistakes

| Mistake | Correct Approach |
|---|---|
| Exceptions in a Google-style project | Follow the existing error API; do not add Abseil solely for style |
| Bare `new`/`delete` | Use smart pointers (`unique_ptr`) |
| `NULL` or `0` for null | Use `nullptr` |
| C-style casts | Use C++ casts (`static_cast`, etc.) |
| `using namespace std` | Never in headers; avoid in `.cc` |
| Mutable global variables | Prefer explicit dependencies and controlled lifetimes |
| Missing `explicit` | Mark single-arg constructors `explicit` |

## Scope and Validation

Use the dedicated C++ testing and API documentation skills for test design and detailed Doxygen work. Prefer values and RAII; use `std::unique_ptr` for exclusive dynamic ownership and `std::shared_ptr` only for genuinely shared lifetimes. Raw pointers may be non-owning observers. Format changed files with the existing `.clang-format`; use `clang-format --style=Google` only when Google style is requested and no project configuration applies. Run the existing build, lint, and affected test targets.

## Full Guide

Read [the companion guide](references/cpp.md) for additional examples. Treat both files as summaries; consult the primary Google guide for exceptions or disputed rules.

## Sources and License

Adapted from [TestDino's C++ skill](https://github.com/testdino-hq/google-styleguides-skills/tree/8674a2a2186a02f86852e061f6166a500ae30f7c/cpp) at commit `8674a2a2186a02f86852e061f6166a500ae30f7c`, including its companion guide. Copyright (c) 2026 TestDino; see [LICENSE](LICENSE) for the preserved MIT terms. This is a third-party adaptation, not an official Google skill.

Local changes rename the skill, relocate the companion guide, add repository-aware workflow and validation, and qualify oversimplified rules. Consult the [primary Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) for authoritative guidance. Keep this attribution and the license when redistributing either file.
