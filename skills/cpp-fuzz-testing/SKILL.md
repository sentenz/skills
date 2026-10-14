---
name: cpp-fuzz-testing
description: Automates fuzz test creation for C++ projects using Google FuzzTest with consistent software testing patterns. Use when creating fuzz tests or when the user mentions fuzzing, AFL, or coverage-guided testing.
metadata:
  version: "1.2.0"
  activation:
    implicit: true
    priority: 2
    triggers:
      - "fuzz"
      - "fuzzing"
      - "fuzztest"
      - "afl"
      - "coverage-guided"
    match:
      languages: ["cpp", "c", "c++"]
      paths: ["src/**/*_fuzz.cpp", "tests/**/*_fuzz.cpp", "fuzz/**/*.cpp"]
      prompt_regex: "(?i)(fuzz|fuzzing|fuzztest|afl|coverage-guided)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Fuzz Testing

Create focused C/C++ fuzz targets with Google FuzzTest. Inspect the project's compiler, dependency revision, build presets, and existing targets before adding dependencies or commands. Keep an established alternative engine when the task requires it.

Input mutation explores the input space; mutation testing changes production code to assess a test suite. Do not treat them as interchangeable.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. FIRST](#21-first)
- [3. Testing Patterns](#3-testing-patterns)
- [4. Test Design](#4-test-design)
- [5. Workflow](#5-workflow)
- [6. Commands](#6-commands)
- [7. Style Guide](#7-style-guide)
- [8. Template](#8-template)
- [9. References](#9-references)

## 1. Benefits

- Input Exploration
  > Explore input-dependent behavior beyond hand-written examples.

- Regression Prevention
  > Retain discovered failures as regression cases.

- Runtime Defect Detection
  > Use sanitizer instrumentation to expose memory errors and undefined behavior in executed C/C++ paths.

## 2. Principles

### 2.1. FIRST

The `FIRST` principles for fuzz testing focus on effective and reproducible tests.

- Fast
  > Keep targets fast by bounding input size and execution cost.

- Independent
  > Keep each target isolated from shared state and other tests.

- Repeatable
  > Make target execution reproducible for a given input.

- Self-Validating
  > Use explicit assertions to evaluate the target contract.

- Timely
  > Develop fuzz tests alongside the affected code.

A completed campaign is evidence about explored behavior, not proof of vulnerability absence.

## 3. Testing Patterns

| Pattern                  | Application                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------- |
| Arrange-Act-Assert (AAA) | Initialize fresh state, invoke the boundary, and evaluate its result.                 |
| In-Got-Want              | Distinguish generated inputs, actual results, and independently derived expectations. |
| Table-Driven Seeds       | Supply representative valid, boundary, malformed, and regression cases.               |
| Test Fixtures            | Reset state on each invocation; join threads and release resources before returning.  |

## 4. Test Design

Define the supported input domain and a meaningful oracle before selecting an engine.

| Technique               | Application                                                               |
| ----------------------- | ------------------------------------------------------------------------- |
| Property-Based Testing  | Assert an invariant required by the contract over generated inputs.       |
| Boundary Value Analysis | Include empty inputs, limits, and values adjacent to thresholds.          |
| Negative Testing        | Exercise malformed inputs and check specified rejection behavior.         |
| Round-Trip Testing      | Check encode/decode consistency and add independent known-answer cases.   |
| Differential Testing    | Compare independent implementations only on shared semantics.             |
| Metamorphic Testing     | Check guaranteed relations such as idempotence or permutation invariance. |

> [!NOTE]
> Treat coverage feedback and corpus mutation as input-generation techniques. Specify resource limits separately from validity constraints; do not discard malformed inputs the API is required to handle. Instrumentation detects defects on executed paths and does not replace semantic assertions.

## 5. Workflow

1. Inspect Project

    Inspect the existing framework, compiler support, CMake targets, and CI budgets. Verify requirements against the pinned FuzzTest revision.

2. Define Input Contract

    Choose one external-input boundary. Document valid inputs, rejection behavior, state ownership, and the oracle.

3. Construct Inputs

    Construct bounded domains and representative seeds. Use a property function returning `void`; avoid harness arithmetic that itself invokes undefined behavior.

4. Register with CMake

    Integrate the target using the project's build conventions. With FuzzTest's CMake integration, load FuzzTest before applying `fuzztest_setup_fuzzing_flags()` to the code under test and link the executable with `link_fuzztest(target)`. Do not add a competing test main.

5. Configure Instrumentation

    Run the normal test mode first. Build a separate instrumented configuration for coverage-guided fuzzing; instrument the target code and relevant libraries, not only the harness. Check sanitizer compatibility rather than combining every sanitizer in one binary.

6. Execute Campaign

    Execute a bounded campaign. Verify duration flags against the installed binary's help. Do not silently substitute ordinary property-test execution for a requested coverage-guided run.

7. Retain Regressions

    Reproduce and minimize each failure. Preserve the reproducing input and add a deterministic regression assertion; distinguish a faulty oracle from a production defect.

8. Report Results

    Report exact commands, framework/compiler revisions, instrumentation, campaign budget, results, and retained regressions. Report unavailable checks explicitly.

## 6. Commands

Use the existing build task where possible. These commands assume a CMake project already integrating FuzzTest and a target named `parser_fuzz_test`; adapt target names and output paths.

```bash
CC=clang CXX=clang++ cmake -S . -B build/fuzz \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo -DFUZZTEST_FUZZING_MODE=ON
cmake --build build/fuzz --target parser_fuzz_test
./build/fuzz/parser_fuzz_test --help
```

Select the registered property with `--fuzz=Suite.Property` and the bounded-duration option supported by the pinned revision. Preserve the process exit status and distinguish normal budget exhaustion from a crash or external timeout. Keep normal unit-test and fuzzing build directories separate.

## 7. Style Guide

- Exception Handling
  > Restrict the expected-exception try block to the parser call; evaluate assertions afterward. Do not catch every exception or suppress sanitizer failures.

- Target Isolation
  > Avoid network access, persistent global state, uncontrolled clocks, and unbounded allocations in the target.

- Input Domains
  > Keep valid and malformed-input domains explicit. Prefer direct construction to excessive filtering.

- Target Platform
  > Use host-mode execution for supported C/C++ targets; host success does not validate hardware-specific behavior.

- Corpus Retention
  > Keep seed data small and free of credentials or sensitive production data.

## 8. Template

Adapt this registration skeleton to a project-defined `Parse` function returning `Packet` and an independently defined `MatchesContract` oracle. The maximum size is an illustrative resource budget, not a validity rule. Supply the declarations of `Packet` and `InputRejected` and verify the documented rejection conditions; arbitrary malformed bytes still reach the parser.

```cpp
#include "fuzztest/fuzztest.h"
#include "gtest/gtest.h"

#include <optional>
#include <string>

void ParserHonorsContract(const std::string& input) {
  // Arrange: create fresh parser state here if required.
  std::optional<Packet> got;
  bool rejected = false;
  // Act: catch only the documented input-rejection exception.
  try {
    got = Parse(input);
  } catch (const InputRejected&) {
    rejected = true;
  }
  // Assert: keep oracle failures outside the parser's exception handler.
  if (rejected) {
    EXPECT_TRUE(IsDocumentedRejection(input));
  } else {
    ASSERT_TRUE(got.has_value());
    EXPECT_TRUE(MatchesContract(input, *got));
  }
}

FUZZ_TEST(ParserTest, ParserHonorsContract)
    .WithDomains(fuzztest::Arbitrary<std::string>().WithMaxSize(4096))
    .WithSeeds({{""}, {"valid-example"}, {"malformed-example"}});
```

Use this skeleton only when the contract supplies independent acceptance and rejection checks. Do not reproduce the parser's algorithm or invent a rejection oracle. If rejection cannot be classified independently, check known malformed examples separately and apply justified properties to accepted inputs. Always include known-valid inputs with expected results so an implementation that rejects everything cannot pass. For error-code APIs, assert the returned status instead of introducing exceptions. The skeleton requires project declarations and is not a standalone executable.

## 9. References

- Google FuzzTest [CMake Quickstart](https://github.com/google/fuzztest/blob/main/doc/quickstart-cmake.md).
- Google FuzzTest [FUZZ_TEST Macro](https://github.com/google/fuzztest/blob/main/doc/fuzz-test-macro.md).
- Google FuzzTest [Domains Reference](https://github.com/google/fuzztest/blob/main/doc/domains-reference.md).
- LLVM Clang [Sanitizer Documentation](https://clang.llvm.org/docs/index.html).
