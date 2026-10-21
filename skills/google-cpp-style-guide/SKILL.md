---
name: cpp
description: Google's official C++ style guide. Covers headers, naming conventions, formatting, classes, memory management, RAII, smart pointers, and modern C++ features.
---

# Google C++ Style Guide

> Official Google C++ coding standards for consistent, maintainable code.

- [1. Golden Rules](#1-golden-rules)
- [2. Quick Reference](#2-quick-reference)
  - [2.1. Naming Conventions](#21-naming-conventions)
  - [2.2. Headers](#22-headers)
  - [2.3. Classes](#23-classes)
  - [2.4. Smart Pointers](#24-smart-pointers)
  - [2.5. Modern C++ Features](#25-modern-c-features)
  - [2.6. Functions](#26-functions)
  - [2.7. Formatting](#27-formatting)
- [3. Common Mistakes](#3-common-mistakes)
- [4. When to Use This Guide](#4-when-to-use-this-guide)
- [5. Install](#5-install)
- [6. Full Guide](#6-full-guide)

## 1. Golden Rules

1. **Target C++20** — avoid non-standard extensions
2. **80-character line limit** — for readability
3. **2-space indentation** — no tabs
4. **Use `const` liberally** — for correctness and thread safety
5. **Avoid exceptions** — Google code doesn't use C++ exceptions
6. **Smart pointers for ownership** — `std::unique_ptr` and `std::shared_ptr`
7. **Header guards** — use `PROJECT_PATH_FILE_H_` format

## 2. Quick Reference

### 2.1. Naming Conventions

| Element         | Convention       | Example                       |
| --------------- | ---------------- | ----------------------------- |
| Files           | snake_case       | `url_table.cc`, `url_table.h` |
| Classes/Structs | UpperCamelCase   | `UserService`                 |
| Functions       | UpperCamelCase   | `GetUserById`                 |
| Variables       | snake_case       | `user_count`                  |
| Constants       | kUpperCamelCase  | `kMaxRetries`                 |
| Class members   | snake_case_      | `user_name_` (trailing `_`)   |
| Macros          | UPPER_SNAKE_CASE | `MAX_BUFFER_SIZE`             |

### 2.2. Headers

```cpp
// ✓ CORRECT - self-contained header with guard
#ifndef FOO_BAR_BAZ_H_
#define FOO_BAR_BAZ_H_

#include <string>
#include "base/basictypes.h"

class Baz {
 public:
  void DoSomething();
};

#endif  // FOO_BAR_BAZ_H_
```

Include order: related header → C system → C++ stdlib → other libs → your headers.

### 2.3. Classes

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

### 2.4. Smart Pointers

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

### 2.5. Modern C++ Features

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

### 2.6. Functions

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

### 2.7. Formatting

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

## 3. Common Mistakes

| Mistake                  | Correct Approach                        |
| ------------------------ | --------------------------------------- |
| Using exceptions         | Use error codes or `absl::Status`       |
| Bare `new`/`delete`      | Use smart pointers (`unique_ptr`)       |
| `NULL` or `0` for null   | Use `nullptr`                           |
| C-style casts            | Use C++ casts (`static_cast`, etc.)     |
| `using namespace std`    | Never in headers; avoid in `.cc`        |
| Mutable global variables | Use singletons or dependency injection  |
| Missing `explicit`       | Mark single-arg constructors `explicit` |

## 4. When to Use This Guide

- Writing new C++ code
- Refactoring existing C++
- Code reviews
- Setting up clang-format rules
- Onboarding new team members

## 5. Install

```bash
npx skills add testdino-hq/google-styleguides-skills/cpp
```

## 6. Full Guide

See [cpp.md](references/cpp.md) references for complete details, examples, and edge cases.
