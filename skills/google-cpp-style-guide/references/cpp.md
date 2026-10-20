# Google C++ Style Guide

> Source: https://google.github.io/styleguide/cppguide.html

Read these examples as excerpts; supply project-specific types and imports before compiling or running them.

- [Golden Rules](#golden-rules)
- [1. Headers](#1-headers)
- [2. Naming](#2-naming)
- [3. Classes](#3-classes)
- [4. Functions](#4-functions)
- [5. Smart Pointers](#5-smart-pointers)
- [6. Modern C++ Features](#6-modern-c-features)
- [7. Avoid These Features](#7-avoid-these-features)
- [8. Formatting](#8-formatting)
- [Common Mistakes](#common-mistakes)
- [Attribution](#attribution)

## Golden Rules

1. **Respect the project language standard** — avoid unsupported features and non-standard extensions
2. **80-character line limit** — for readability
3. **2-space indentation** — no tabs
4. **Use `const` where appropriate** — express intent; constness alone does not establish thread safety
5. **Follow the project exception policy** — Google style disallows exceptions; do not change an existing exception-based API as a style edit
6. **Smart pointers for ownership** — `std::unique_ptr` and `std::shared_ptr`
7. **Header guards** — use `PROJECT_PATH_FILE_H_` format

---

## 1. Headers

```cpp
// CORRECT - self-contained header with guard
#ifndef FOO_BAR_BAZ_H_
#define FOO_BAR_BAZ_H_

#include <string>

class Baz {
 public:
  void DoSomething();
};

#endif  // FOO_BAR_BAZ_H_
```

### Include Order

1. Related header
2. C system headers
3. C++ standard library headers
4. Other libraries' headers
5. Your project's headers

---

## 2. Naming

| Element | Convention | Example |
|---|---|---|
| Files | snake_case | `url_table.cc` |
| Types | UpperCamelCase | `UrlTable` |
| Variables | snake_case | `table_name` |
| Functions | UpperCamelCase | `AddTableEntry()` |
| Constants | kConstantName | `kDaysInAWeek` |
| Macros | UPPER_SNAKE_CASE | `MY_MACRO` |
| Class members | snake_case_ | `table_name_` (trailing underscore) |

---

## 3. Classes

```cpp
// CORRECT
class MyClass {
 public:
  MyClass();  // Constructor
  ~MyClass();  // Destructor

  void DoSomething();
  int GetValue() const { return value_; }

 private:
  int value_;
  std::string name_;
};
```

### Key Rules

- Declare data members `private` (except in structs)
- Use trailing underscore for private data members
- Mark single-argument constructors `explicit`
- Use `= delete` for uncopyable classes
- Prefer composition over inheritance

---

## 4. Functions

```cpp
// CORRECT - return type on same line
ReturnType ClassName::FunctionName(Type par_name1, Type par_name2) {
  DoSomething();
  return result;
}

// CORRECT - wrap long parameter lists
ReturnType LongClassName::ReallyLongFunctionName(
    Type par_name1,  // 4 space indent
    Type par_name2,
    Type par_name3) {
  DoSomething();
}
```

---

## 5. Smart Pointers

```cpp
// CORRECT - use unique_ptr for exclusive ownership
std::unique_ptr<Foo> FooFactory();
void FooConsumer(std::unique_ptr<Foo> ptr);

// CORRECT - use shared_ptr sparingly
std::shared_ptr<const Foo> immutable_foo;

// AVOID - never use auto_ptr
std::auto_ptr<Foo> foo;  // AVOID
```

---

## 6. Modern C++ Features

```cpp
// CORRECT - use auto for complex types
auto it = my_map.find(key);
auto widget = std::make_unique<Widget>(arg1, arg2);

// CORRECT - use range-based for loops
for (const auto& item : container) {
  Process(item);
}

// CORRECT - use nullptr, not NULL
Foo* ptr = nullptr;

// CORRECT - use constexpr for compile-time constants
constexpr int kArraySize = 100;
```

---

## 7. Avoid These Features

| Feature | Why Avoid |
|---|---|
| Exceptions | Disallowed by Google style; respect the target project policy |
| RTTI (`dynamic_cast`) | Use sparingly; prefer virtual methods |
| Multiple inheritance | Complex; use sparingly |
| Operator overloading | Use judiciously; must be obvious |
| Default arguments | Can be confusing; prefer overloads |

---

## 8. Formatting

```cpp
// CORRECT - braces and spacing
if (condition) {
  DoSomething();
} else {
  DoSomethingElse();
}

// CORRECT - pointer/reference alignment
char* c;
const std::string& str;

// CORRECT - function calls
DoSomething(argument1, argument2, argument3);

// CORRECT - wrap long calls
DoSomething(
    argument1, argument2,  // 4 space indent
    argument3, argument4);
```

---

## Common Mistakes

| Mistake | Correct Approach |
|---|---|
| Exceptions in a Google-style project | Follow the existing error API; do not add Abseil solely for style |
| Bare `new`/`delete` | Use smart pointers |
| `NULL` | Use `nullptr` |
| C-style casts | Use C++ casts (`static_cast`, etc.) |
| `using namespace std` | Never in headers; avoid in .cc files |
| Mutable globals | Prefer explicit dependencies and controlled lifetimes |

## Attribution

Adapted from [TestDino's companion guide](https://github.com/testdino-hq/google-styleguides-skills/blob/8674a2a2186a02f86852e061f6166a500ae30f7c/cpp/cpp.md). See [the skill](../SKILL.md#sources-and-license) for adaptation details and [LICENSE](../LICENSE) for the preserved MIT terms. This summary does not replace the primary Google guide.
