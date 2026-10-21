# Google C++ Style Guide

> Source: https://google.github.io/styleguide/cppguide.html

- [1. Golden Rules](#1-golden-rules)
- [2. Headers](#2-headers)
  - [2.1. Include Order](#21-include-order)
- [3. Naming](#3-naming)
- [4. Classes](#4-classes)
  - [4.1. Key Rules](#41-key-rules)
- [5. Functions](#5-functions)
- [6. Smart Pointers](#6-smart-pointers)
- [7. Modern C++ Features](#7-modern-c-features)
- [8. Avoid These Features](#8-avoid-these-features)
- [9. Formatting](#9-formatting)
- [10. Common Mistakes](#10-common-mistakes)

## 1. Golden Rules

1. **Target C++20** — avoid non-standard extensions
2. **80-character line limit** — for readability
3. **2-space indentation** — no tabs
4. **Use `const` liberally** — for correctness and thread safety
5. **Avoid exceptions** — Google code doesn't use C++ exceptions
6. **Smart pointers for ownership** — `std::unique_ptr` and `std::shared_ptr`
7. **Header guards** — use `PROJECT_PATH_FILE_H_` format

---

## 2. Headers

```cpp
// CORRECT - self-contained header with guard
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

### 2.1. Include Order

1. Related header
2. C system headers
3. C++ standard library headers
4. Other libraries' headers
5. Your project's headers

---

## 3. Naming

| Element       | Convention       | Example                             |
| ------------- | ---------------- | ----------------------------------- |
| Files         | snake_case       | `url_table.cc`                      |
| Types         | UpperCamelCase   | `UrlTable`                          |
| Variables     | snake_case       | `table_name`                        |
| Functions     | UpperCamelCase   | `AddTableEntry()`                   |
| Constants     | kConstantName    | `kDaysInAWeek`                      |
| Macros        | UPPER_SNAKE_CASE | `MY_MACRO`                          |
| Class members | snake_case_      | `table_name_` (trailing underscore) |

---

## 4. Classes

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

### 4.1. Key Rules

- Declare data members `private` (except in structs)
- Use trailing underscore for private data members
- Mark single-argument constructors `explicit`
- Use `= delete` for uncopyable classes
- Prefer composition over inheritance

---

## 5. Functions

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

## 6. Smart Pointers

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

## 7. Modern C++ Features

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

## 8. Avoid These Features

| Feature               | Why Avoid                             |
| --------------------- | ------------------------------------- |
| Exceptions            | Not used at Google; use error codes   |
| RTTI (`dynamic_cast`) | Use sparingly; prefer virtual methods |
| Multiple inheritance  | Complex; use sparingly                |
| Operator overloading  | Use judiciously; must be obvious      |
| Default arguments     | Can be confusing; prefer overloads    |

---

## 9. Formatting

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

## 10. Common Mistakes

| Mistake               | Correct Approach                       |
| --------------------- | -------------------------------------- |
| Using exceptions      | Use error codes or `absl::Status`      |
| Bare `new`/`delete`   | Use smart pointers                     |
| `NULL`                | Use `nullptr`                          |
| C-style casts         | Use C++ casts (`static_cast`, etc.)    |
| `using namespace std` | Never in headers; avoid in .cc files   |
| Mutable globals       | Use singletons or dependency injection |
