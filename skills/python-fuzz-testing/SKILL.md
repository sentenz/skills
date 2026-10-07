---
name: python-fuzz-testing
description: Create and review Python property-based tests with Hypothesis and coverage-guided fuzz targets with Atheris. Use for generated inputs, invariants, parser robustness, malformed data, shrinking failures, seed corpora, crash reproduction, or fuzz regression tests.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "fuzz test"
      - "property-based test"
      - "hypothesis"
      - "atheris"
      - "fuzzing"
      - "create fuzz test"
      - "add fuzz test"
    match:
      languages: ["python"]
      paths: ["**/test*.py", "**/*_test.py", "tests/**/*.py"]
      prompt_regex: '(?i)(fuzz test|property-based test|hypothesis|atheris|fuzzing|create fuzz test|add fuzz test)'
    usage:
      load_on_prompt: true
      autodispatch: true
---

# Fuzz Testing

Fuzz testing explores an input space through generated or mutated data to expose unexpected behavior. A test oracle is the rule that determines whether a result is correct; an invariant is a property that holds throughout the specified input domain.

This skill covers structured property-based tests with [Hypothesis](https://hypothesis.readthedocs.io/en/latest/quickstart.html) and coverage-guided byte-oriented targets with [Atheris](https://github.com/google/atheris). Hypothesis generates examples for stated properties and shrinks failures; Atheris uses coverage feedback to guide input mutation. Ordinary randomized tests do not establish coverage-guided exploration.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. FIRST](#21-first)
- [3. Patterns](#3-patterns)
  - [3.1. Input Generation](#31-input-generation)
  - [3.2. Test Oracles](#32-test-oracles)
- [4. Workflow](#4-workflow)
- [5. Commands](#5-commands)
- [6. Style Guide](#6-style-guide)
- [7. Templates](#7-templates)
  - [7.1. Structured Property with Hypothesis](#71-structured-property-with-hypothesis)
  - [7.2. Coverage-Guided Target with Atheris](#72-coverage-guided-target-with-atheris)
- [8. References](#8-references)

## 1. Benefits

Generated tests extend the input cases covered by deterministic examples and retain reproducible evidence of failures.

- Input Exploration

    Generated combinations and boundary values exercise behavior absent from hand-written examples.

- Failure Reduction

    Shrinking or corpus minimization reduces failing inputs to cases that support diagnosis and regression testing.

- Branch Exploration

    Coverage-guided mutation uses a seed corpus, a collection of initial inputs, to explore parser and decoder branches.

## 2. Principles

Generated tests require bounded execution and an oracle whose domain matches the target's contract.

### 2.1. FIRST

FIRST groups five test-design properties: Fast, Independent, Repeatable, Self-Validating, and Timely. These properties apply to each generated example as well as the enclosing campaign.

- Fast

    Bounded input sizes and operations separate short continuous integration (CI) runs from longer campaigns.

- Independent

    State resets between inputs prevent earlier examples or external services from determining later results.

- Repeatable

    Retained failing inputs, environment details, and dependency versions support reproduction.

- Self-Validating

    A stated invariant or independently computed result determines whether each input exposes a defect.

- Timely

    Generated properties accompany deterministic unit tests at input boundaries with significant failure consequences.

## 3. Patterns

Input-generation techniques determine how examples are produced. Test oracles determine how the resulting behavior is evaluated.

### 3.1. Input Generation

Structured generation encodes the input domain in strategies; coverage-guided mutation selects inputs using execution feedback.

| Technique | Application |
| --- | --- |
| Property-Based Generation | Generate structured inputs with Hypothesis strategies and shrink failures. |
| Coverage-Guided Mutation | Instrument relevant Python code with Atheris and mutate a seed corpus. |

### 3.2. Test Oracles

The following oracles evaluate equality, agreement between implementations, relations between operations, or documented rejection behavior.

| Oracle | Application |
| --- | --- |
| Round Trip | Assert `decode(encode(value)) == value` over the supported domain; add independent known-answer cases because paired defects can cancel out. |
| Differential Comparison | Compare implementations only where their documented semantics agree. |
| Metamorphic Relation | Check idempotence, permutation invariance, or monotonicity when guaranteed by the contract. |
| Input Rejection | Check documented rejection behavior without swallowing unrelated exceptions. |

## 4. Workflow

The workflow defines the input domain and oracle before selecting an engine, executing a campaign, and preserving regression cases.

1. Inspect Environment

    Inspect runtime versions, dependency constraints, CI budgets, existing fuzz targets, and corpus conventions. Verify Atheris platform/interpreter support before selecting it; do not silently replace a required coverage-guided campaign with property tests.

2. Define Input Contract

    Identify an input boundary and write down its valid domain, expected rejection types, and oracle. Include empty input, boundaries, encodings, and state transitions that matter to that boundary.

3. Select Engine

    Choose Hypothesis for structured data or Atheris for coverage feedback. Keep the target small and deterministic. Instrument imports before loading the code under test; native-extension sanitizer coverage requires a compatible instrumented build.

4. Construct Inputs

    Generate valid cases by construction. Create separate malformed-input cases where needed; avoid excessive `assume` or filtering that discards most generated examples.

5. Bound Execution

    Bound input sizes, recursion, allocations, and campaign runtime. Keep assertions outside the exception handler for expected parsing failures. Never catch `Exception` or `BaseException` around the whole target.

6. Reproduce Failures

    Run a bounded smoke test, reproduce any failure, and retain its minimal input. Distinguish a defect in the oracle from a defect in production code before changing either.

7. Retain Regressions

    Add a deterministic regression test or Hypothesis `@example` for confirmed bugs; preserve useful Atheris seeds. Cache Hypothesis's example database when appropriate, but do not rely on that cache as the sole permanent regression record.

8. Report Campaign

    Report the engine, versions, target, budget, explored cases or coverage when available, reproduction command, and retained artifacts. A clean finite campaign is not proof that all inputs are safe.

## 5. Commands

Use the project's dependency manager to provide Hypothesis or Atheris as development dependencies. Run from the project root and adapt paths. The Atheris example is saved as `fuzz/fuzz_json.py`; execute it as a module so installed project imports resolve consistently.

| Command | Purpose |
| --- | --- |
| `python -m pytest tests/test_properties.py -q` | Run Hypothesis properties. |
| `python -m pytest tests/test_properties.py --hypothesis-seed=1234 -vv` | Investigate a run with a fixed seed; also retain the concrete failure. |
| `mkdir -p fuzz/corpus/json fuzz/artifacts` | Prepare corpus and artifact directories. |
| `python -m fuzz.fuzz_json fuzz/corpus/json -max_total_time=30 -max_len=4096 -artifact_prefix=fuzz/artifacts/` | Run a bounded Atheris smoke campaign. |
| `python -m fuzz.fuzz_json fuzz/artifacts/crash-example -runs=1` | Replay an actual saved crash, replacing the example filename. |

Atheris forwards [libFuzzer options](https://llvm.org/docs/LibFuzzer.html#options). Use CI process timeouts and resource limits as well as the campaign budget, since a single hung invocation may exceed the campaign duration. Preserve artifacts before cleaning temporary runners.

## 6. Style Guide

These conventions preserve meaningful exploration, visible failures, and reproducible inputs.

- Naming

    Name Hypothesis tests `test_<property>` and Atheris entry points `fuzz_<target>.py`; avoid naming standalone fuzz launchers `test_*.py`.

- Boundary Examples

    Include explicit examples of critical boundaries even when strategies may generate them.

- Numeric Domains

    Exclude not-a-number (NaN) and infinity only when outside the contract. Equality is not a valid oracle for NaN, and floating-point round trips may need specified tolerances.

- Strategy Composition

    Avoid `.example()` inside tests; draw through `@given`, composite strategies, or `st.data()` so failures remain shrinkable.

- Example State

    Do not suppress Hypothesis health checks to hide poor strategy design or shared-state defects. Function-scoped pytest fixtures are not recreated for each Hypothesis example; initialize or reset mutable state inside the generated test body.

- Exploration and Reproduction

    Do not set a global fixed seed solely to make CI results repeatable. Retain stored examples and reproduction details while allowing ongoing exploration.

- Exception Handling

    Catch only expected input-rejection exceptions around the parser call. Let assertion failures, unexpected exceptions, and crashes fail the run.

- Corpus Retention

    Keep corpora small, representative, and free of credentials or sensitive production data. Minimize and review newly retained inputs.

## 7. Templates

These self-contained examples exercise the standard-library JavaScript Object Notation (JSON) codec. Replace the codec with the project's implementation and retain only properties guaranteed by its contract.

### 7.1. Structured Property with Hypothesis

The property checks equality after serialization and deserialization within a bounded integer-list domain. Save the example as `tests/test_properties.py`.

Example:

```python
import json

from hypothesis import example, given, settings, strategies as st


@given(st.lists(st.integers(min_value=-(2**31), max_value=2**31 - 1), max_size=100))
@example([])
@example([-(2**31), 0, 2**31 - 1])
@settings(max_examples=100)
def test_json_integer_list_round_trip(values):
    encoded = json.dumps(values)
    got = json.loads(encoded)
    assert got == values
```

Adapt the integer range to the actual format; this range is a workload choice, not a Python integer limit. Add separate known-answer and invalid-input tests. For stateful application programming interfaces (APIs), consider a Hypothesis rule-based state machine with an independent model.

### 7.2. Coverage-Guided Target with Atheris

Save as `fuzz/fuzz_json.py`. Keep `atheris.Setup` and `atheris.Fuzz` behind the main guard so importing the module does not start a campaign.

Example:

```python
import sys

import atheris

with atheris.instrument_imports():
    import json


@atheris.instrument_func
def test_one_input(data):
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return

    # Use a bounded, exactly comparable subdomain for the round-trip oracle.
    if not isinstance(value, list) or len(value) > 100:
        return
    if not all(type(item) is int and -(2**31) <= item < 2**31 for item in value):
        return

    got = json.loads(json.dumps(value))
    assert got == value


if __name__ == "__main__":
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
```

Seed the corpus with small examples such as `[]`, `[0]`, and malformed JSON. Inputs outside the oracle's subdomain still reach the parser. Decide explicitly whether depth/resource exceptions are defects or documented rejections for the actual target.

## 8. References

- Hypothesis [Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html) documentation.
- Hypothesis [Strategies](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html) documentation.
- Hypothesis [Replaying Failures](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html) documentation.
- Google [Atheris](https://github.com/google/atheris) repository.
- LLVM [libFuzzer Options](https://llvm.org/docs/LibFuzzer.html#options) documentation.
