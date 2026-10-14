---
name: cpp-mock-testing
description: Automates mock test creation for C++ projects using Google Mock (GMock) framework with consistent software testing patterns. Use when creating tests with mocked dependencies, interface mocking, behavior verification, or when the user mentions mocks, stubs, fakes, or GMock.
metadata:
  version: "1.2.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "mock"
      - "gmock"
      - "stub"
      - "fake"
      - "mock object"
      - "test double"
      - "mocked dependency"
    match:
      languages: ["cpp", "c", "c++"]
      paths: ["src/**/*_test.cpp", "tests/**/*_test.cpp", "test/**/*_test.cpp"]
      prompt_regex: "(?i)(mock|gmock|stub|fake|test double|mocked|interface mock)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Mock Testing

Instructions for AI coding agents on automating mock test creation using Google Mock (GMock) with consistent software testing patterns in this C++ project.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. FIRST](#21-first)
- [3. Testing Patterns](#3-testing-patterns)
- [4. Test Design](#4-test-design)
- [5. Workflow](#5-workflow)
- [6. Commands](#6-commands)
- [7. Style Guide](#7-style-guide)
- [8. Template](#8-template)
  - [8.1. File Header Template](#81-file-header-template)
  - [8.2. Mock Class Template](#82-mock-class-template)
  - [8.3. Table-Driven Mock Test Template](#83-table-driven-mock-test-template)
  - [8.4. Sequence Verification Template](#84-sequence-verification-template)
  - [8.5. Exception Testing Template](#85-exception-testing-template)
  - [8.6. NiceMock Template](#86-nicemock-template)
- [9. References](#9-references)

## 1. Benefits

- Isolation
  > Isolates the unit under test from external dependencies, ensuring tests focus on the specific component's behavior.

- Control
  > Provides precise control over dependency behavior through expectations and return values, enabling thorough testing of edge cases and error conditions.

- Verification
  > Automatically verifies that dependencies are called correctly with expected parameters and call counts.

- Flexibility
  > Supports various testing scenarios including strict mocks, nice mocks, and sequence verification for complex interactions.

## 2. Principles

### 2.1. FIRST

The `FIRST` principles for mock testing focus on creating effective and maintainable tests.

- Fast
  > Mock tests should execute quickly by replacing slow dependencies (network, file system, databases) with fast mock implementations to provide rapid feedback.

- Independent
  > Each mock test should be self-contained with its own mock setup and not rely on the state or behavior of other tests.

- Repeatable
  > Mock tests should produce deterministic results every time by controlling dependency behavior through expectations and return values.

- Self-Validating
  > Mock tests should have clear pass/fail outcomes with automatic verification of mock expectations and assertion results.

- Timely
  > Mock tests should be written alongside production code to validate the interaction contracts between components.

## 3. Testing Patterns

- Mock Objects
  > Simulated objects that mimic the behavior of real objects in controlled ways. They verify interactions between the unit under test and its dependencies.

- Interface Mocking
  > Creating mock implementations of abstract interfaces or base classes to isolate the unit under test from concrete implementations.

- Return Value Stubbing
  > Configuring mock objects to return specific values when their methods are called, allowing control over dependency behavior during tests.

## 4. Test Design

Choose scenarios from the dependency contract, then select the least complex test double that can reproduce them.

| Technique                | Application                                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------------------------- |
| Failure Injection        | Configure specific exceptions, failures, or bounded retry sequences and verify recovery or propagation. |
| Negative Testing         | Exercise rejected requests and verify that prohibited side effects do not occur.                        |
| Boundary Value Analysis  | Cover relevant argument limits and retry thresholds, including exhaustion.                              |
| Interaction Verification | Check arguments, counts, and ordering only when required by the observable contract.                    |

Assert returned values or state as well as contractual interactions. Keep real-boundary integration tests separate: a passing mock test does not establish compatibility with a live dependency. FIRST governs isolation and reproducibility; it is not an additional testing pattern.

## 5. Workflow

1. Identify Dependencies

    Identify interfaces or classes that need to be mocked (e.g., database connections, file systems, network services, external APIs).

2. Create Mock Classes

    Create mock classes for interfaces under `test(s)/unit/<module>/` using GMock's `MOCK_METHOD` macro.

3. Register with CMake

    Add the test file to `test(s)/unit/<module>/CMakeLists.txt` using `meta_gtest()` with `WITH_GMOCK` option.

    ```cmake
    meta_gtest(
      WITH_GMOCK
      TARGET ${PROJECT_NAME}-test
      SOURCES
        <header>_test.cpp
    )
    ```

4. Define Expectations

    Set up expectations using `EXPECT_CALL` to specify:

    - Which methods should be called
    - Expected arguments (using matchers)
    - Call frequency (Times, AtLeast, AtMost, etc.)
    - Return values or actions

5. Test Coverage Requirements

    Include comprehensive scenarios:

    - Normal operation with mocked dependencies
    - Error conditions (exceptions, null returns, invalid data)
    - Boundary conditions in dependency interactions
    - Sequence of calls to multiple dependencies
    - Concurrent access scenarios when applicable

6. Apply Templates

    Structure all tests using the template pattern below.

## 6. Commands

Verify that the listed Make targets exist in the current project. Reuse its configured build and test tasks; do not assume these example targets are available.

1. Make Tasks

    | Tasks                               | Description                                                                        |
    | ----------------------------------- | ---------------------------------------------------------------------------------- |
    | `make cmake-gcc-test-unit-build`    | Configure CMake presets with Google Mock support and compile with Ninja            |
    | `make cmake-gcc-test-unit-run`      | Execute tests via CTest (mock tests are part of unit tests)                        |
    | `make cmake-gcc-test-unit-coverage` | Execute tests via CTest and generate coverage reports including mock test coverage |

2. Command Instructions

    Run from the project root. Replace angle-bracket placeholders with values from the project's Makefile and CMake presets before execution. These examples illustrate the underlying operations; retain project-specific flags and targets. Coverage requires a clean build with GCC coverage instrumentation, a matching gcov tool, and successful test execution before reporting. Use the project's configured coverage tool and filters; the report examples assume [gcovr](https://gcovr.com/en/stable/) is installed.

    | Instructions                                                                      | Description                                                                       |
    | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
    | `cmake --list-presets`                                                            | List available configure presets and select the project's unit-test configuration |
    | `cmake --preset <unit-configure-preset>`                                          | Configure the existing GCC/Ninja unit-test build with Google Mock support         |
    | `cmake --build --list-presets`                                                    | List build presets and select one using the configured unit-test directory        |
    | `cmake --build --preset <unit-build-preset>`                                      | Compile the configured unit-test targets                                          |
    | `ctest --test-dir <unit-build-dir> --output-on-failure`                           | Execute registered unit tests, including mock tests, and display failure output   |
    | `ctest --test-dir <unit-build-dir> -R '<test-regex>' --output-on-failure`         | Execute CTest entries matching a test-name regular expression                     |
    | `gcovr --root . --object-directory <unit-build-dir> --html-details coverage.html` | Generate a detailed HTML report from instrumented test execution                  |
    | `gcovr --root . --object-directory <unit-build-dir> --xml coverage.xml`           | Generate a Cobertura XML report from the same coverage data                       |

## 7. Style Guide

- Test Framework
  > Use [Google Mock (GMock)](https://google.github.io/googletest/gmock_for_dummies.html) framework via `#include <gmock/gmock.h>` and `#include <gtest/gtest.h>`.

- Mock Class Definition
  > Define mock classes inheriting from the interface to be mocked. Use `MOCK_METHOD` macro with proper method signature, including const qualifiers and override specifiers.

- Include Headers
  > GMock/GTest headers are listed first in mock test files as a convention to clearly identify the file as a test file using the GMock framework.

  Include necessary headers in this order:
  1. GMock/GTest headers (`<gmock/gmock.h>`, `<gtest/gtest.h>`)
  2. Standard library headers (`<memory>`, `<string>`, etc.)
  3. Project interface headers
  4. Project implementation headers

- Namespace
  > Use `using namespace <namespace>;` and `using namespace ::testing;` for convenience within test functions to access GMock matchers and actions.

- Test Organization
  > Use table-driven testing for multiple scenarios with the same mock setup. Each `TEST` or `TEST_F` should focus on one aspect of the interaction with mocked dependencies.

- Mock Types
  - NiceMock
    > Suppresses warnings for uninteresting calls (methods without expectations); unexpected calls still fail.
  - StrictMock
    > Fails on uninteresting calls as well as unexpected calls; use only when the interaction contract requires strict verification.
  - Default Mock
    > Warns on uninteresting calls; unexpected calls fail regardless of mock strictness.

- Expectations
  - Use `EXPECT_CALL` to set up expectations before exercising the unit under test
  - Chain matchers with `.With()`, `.WillOnce()`, `.WillRepeatedly()`, `.Times()`
  - Prefer specific matchers (`Eq()`, `Gt()`, `_`) over generic ones when possible

- Matchers and Actions
  - Use built-in matchers: `_` (anything), `Eq()`, `Ne()`, `Lt()`, `Gt()`, `Le()`, `Ge()`, `IsNull()`, `NotNull()`
  - Container matchers: `IsEmpty()`, `SizeIs()`, `Contains()`, `ElementsAre()`
  - String matchers: `StartsWith()`, `EndsWith()`, `HasSubstr()`, `MatchesRegex()`
  - Use `Return()`, `ReturnRef()`, `Throw()`, `DoAll()`, `Invoke()` for actions

- Sequence Verification
  > Use `InSequence` or `Sequence` objects when call order matters.

- Traceability
  > Employ `SCOPED_TRACE(tc.label)` for traceable failures in table-driven mock tests.

- Assertions
  > Use `EXPECT_*` macros to allow all test cases to run. Mock expectations are automatically verified at the end of each test.

## 8. Template

Use these templates for new mock tests. Replace placeholders with actual values.

### 8.1. File Header Template

```cpp
#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <memory>
#include <string>
#include <vector>

#include "<module>/<interface>.hpp"
#include "<module>/<implementation>.hpp"

using namespace <namespace>;
using namespace ::testing;
```

### 8.2. Mock Class Template

```cpp
/**
 * @brief Mock implementation of <Interface> for testing.
 */
class Mock<Interface> : public <Interface>
{
public:
  MOCK_METHOD(<return_type>, <method_name>, (<param_types>), (override));
  MOCK_METHOD(<return_type>, <method_name2>, (<param_types>), (const, override));
};
```

### 8.3. Table-Driven Mock Test Template

```cpp
TEST(<Module>Test, <FunctionName>WithMock)
{
  // In-Got-Want
  struct Tests
  {
    std::string label;

    struct In
    {
      /* input types and names */
    } in;

    struct Want
    {
      <output_type> expected;     // expected output type(s) and name(s)
      /* expected mock call parameters and behavior */
      <size_t> call_count;        // number of times method should be called
      <return_type> return_value; // value mock should return
      <param_type> param;         // expected parameter value(s)
    } want;
  };

  // Table-Driven Testing
  const std::vector<Tests> tests = {
    {
      "case-description-1", 
      /* in */ {/* input values */}, 
      /* want */ {/* expected */, /* call_count */ 1, /* return_value */ {}, /* param */ {}}
    },
    {
      "case-description-2", 
      /* in */ {/* input values */}, 
      /* want */ {/* expected */, /* call_count */ 1, /* return_value */ {}, /* param */ {}}
    },
    // add more cases as needed
  };

  for (const auto &tc : tests)
  {
    SCOPED_TRACE(tc.label);

    // Arrange
    auto mock_dependency = std::make_shared<Mock<Interface>>();

    EXPECT_CALL(*mock_dependency, <method_name>(tc.want.param))
        .Times(tc.want.call_count)
        .WillOnce(Return(tc.want.return_value));

    <Implementation> object(mock_dependency);

    // Act
    auto got = object.<function>(tc.in.<input>);

    // Assert
    EXPECT_EQ(got, tc.want.expected);
  }
}
```

### 8.4. Sequence Verification Template

```cpp
TEST(<Module>Test, <FunctionName>WithSequence)
{
  // Arrange
  auto mock_dependency = std::make_shared<StrictMock<Mock<Interface>>>();

  InSequence seq;
  EXPECT_CALL(*mock_dependency, <method1>(_)).WillOnce(Return(<value1>));
  EXPECT_CALL(*mock_dependency, <method2>(_)).WillOnce(Return(<value2>));

  <Implementation> object(mock_dependency);

  // Act
  auto got = object.<function>();

  // Assert
  EXPECT_EQ(got, <expected>);
}
```

### 8.5. Exception Testing Template

```cpp
TEST(<Module>Test, <FunctionName>ThrowsOnError)
{
  // Arrange
  auto mock_dependency = std::make_shared<Mock<Interface>>();

  EXPECT_CALL(*mock_dependency, <method_name>(_))
      .WillOnce(Throw(std::runtime_error("error message")));

  <Implementation> object(mock_dependency);

  // Act & Assert
  EXPECT_THROW(object.<function>(), std::runtime_error);
}
```

### 8.6. NiceMock Template

```cpp
TEST(<Module>Test, <FunctionName>WithNiceMock)
{
  // Arrange
  auto mock_dependency = std::make_shared<NiceMock<Mock<Interface>>>();

  ON_CALL(*mock_dependency, <method_name>(_))
      .WillByDefault(Return(<default_value>));

  EXPECT_CALL(*mock_dependency, <critical_method>(_))
      .Times(1)
      .WillOnce(Return(<value>));

  <Implementation> object(mock_dependency);

  // Act
  auto got = object.<function>();

  // Assert
  EXPECT_EQ(got, <expected>);
}
```

## 9. References

- GoogleTest [Mocking for Dummies](https://google.github.io/googletest/gmock_for_dummies.html) guide.
- GoogleTest [Mocking Cookbook](https://google.github.io/googletest/gmock_cook_book.html) guide.
- GoogleTest [Mocking Cheat Sheet](https://google.github.io/googletest/gmock_cheat_sheet.html) guide.
