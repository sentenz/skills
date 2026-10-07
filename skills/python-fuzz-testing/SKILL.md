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

Explore Python input spaces with explicit oracles, bounded resources, and reproducible regressions. Select Hypothesis for structured properties and Atheris for coverage-guided byte-oriented targets; do not describe ordinary randomized tests as coverage-guided fuzzing.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
- [4. Workflow](#4-workflow)
- [5. Commands](#5-commands)
- [6. Style Guide](#6-style-guide)
- [7. Templates](#7-templates)
- [8. References](#8-references)

## 1. Benefits

- Discover combinations and boundary cases absent from hand-written examples.
- Reduce failing inputs into understandable regression cases.
- Exercise parser and decoder branches using evolving seed corpora.

## 2. Principles

Apply FIRST to each generated example:

- **Fast:** Bound input size and expensive operations; separate short CI runs from longer campaigns.
- **Independent:** Reset state between inputs and avoid external services.
- **Repeatable:** Preserve the failing input, environment, and dependency versions.
- **Self-Validating:** Assert a meaningful invariant or independently computed result.
- **Timely:** Add properties alongside deterministic unit tests at high-risk boundaries.

## 3. Patterns

| Pattern | Application |
| --- | --- |
| Property-based testing | Generate structured inputs with Hypothesis strategies and shrink failures. |
| Coverage-guided fuzzing | Instrument relevant Python code with Atheris and mutate a seed corpus. |
| Round trip | Assert `decode(encode(value)) == value` over the supported domain; add independent known-answer cases because paired defects can cancel out. |
| Differential testing | Compare implementations only where their documented semantics agree. |
| Metamorphic testing | Check relations such as idempotence, permutation invariance, or monotonicity when guaranteed by the contract. |
| Malformed input | Check documented rejection behavior without swallowing unrelated exceptions. |

## 4. Workflow

1. Inspect runtime versions, dependency constraints, CI budgets, existing fuzz targets, and corpus conventions. Verify Atheris platform/interpreter support before selecting it; do not silently replace a required coverage-guided campaign with property tests.
2. Identify an input boundary and write down its valid domain, expected rejection types, and oracle. Include empty input, boundaries, encodings, and state transitions that matter to that boundary.
3. Choose Hypothesis for structured data or Atheris for coverage feedback. Keep the target small and deterministic. Instrument imports before loading the code under test; native-extension sanitizer coverage requires a compatible instrumented build.
4. Generate valid cases by construction. Create separate malformed-input cases where needed; avoid excessive `assume` or filtering that discards most generated examples.
5. Bound input sizes, recursion, allocations, and campaign runtime. Keep assertions outside the exception handler for expected parsing failures. Never catch `Exception` or `BaseException` around the whole target.
6. Run a bounded smoke test, reproduce any failure, and retain its minimal input. Distinguish a defect in the oracle from a defect in production code before changing either.
7. Add a deterministic regression test or Hypothesis `@example` for confirmed bugs; preserve useful Atheris seeds. Cache Hypothesis's example database when appropriate, but do not rely on that cache as the sole permanent regression record.
8. Report the engine, versions, target, budget, explored cases or coverage when available, reproduction command, and retained artifacts. A clean finite campaign is not proof that all inputs are safe.

## 5. Commands

Use the project's dependency manager to provide Hypothesis or Atheris as development dependencies. Run from the project root and adapt paths. The Atheris example is saved as `fuzz/fuzz_json.py`; execute it as a module so installed project imports resolve consistently.

| Command | Purpose |
| --- | --- |
| `python -m pytest tests/test_properties.py -q` | Run Hypothesis properties. |
| `python -m pytest tests/test_properties.py --hypothesis-seed=1234 -vv` | Investigate a run with a fixed seed; also retain the concrete failure. |
| `mkdir -p fuzz/corpus/json fuzz/artifacts` | Prepare corpus and artifact directories. |
| `python -m fuzz.fuzz_json fuzz/corpus/json -max_total_time=30 -max_len=4096 -artifact_prefix=fuzz/artifacts/` | Run a bounded Atheris smoke campaign. |
| `python -m fuzz.fuzz_json fuzz/artifacts/crash-example -runs=1` | Replay an actual saved crash, replacing the example filename. |

Atheris forwards libFuzzer options. Use CI process timeouts and resource limits as well as the campaign budget, since a single hung invocation may exceed the campaign duration. Preserve artifacts before cleaning temporary runners.

## 6. Style Guide

- Name Hypothesis tests `test_<property>` and Atheris entry points `fuzz_<target>.py`; avoid naming standalone fuzz launchers `test_*.py`.
- Include explicit examples of critical boundaries even when strategies may generate them.
- Exclude NaN/infinity only when outside the contract. Equality is not a valid oracle for NaN, and floating-point round trips may need specified tolerances.
- Avoid `.example()` inside tests; draw through `@given`, composite strategies, or `st.data()` so failures remain shrinkable.
- Do not suppress Hypothesis health checks to hide poor strategy design or shared-state defects. Function-scoped pytest fixtures are not recreated for each Hypothesis example; initialize/reset mutable state inside the generated test body.
- Do not set a global fixed seed solely to make CI look deterministic. Use stored examples and reproduction details; allow ongoing exploration.
- Catch only expected input-rejection exceptions around the parser call. Let assertion failures, unexpected exceptions, and crashes fail the run.
- Keep corpora small, representative, and free of credentials or sensitive production data. Minimize and review newly retained inputs.

## 7. Templates

These self-contained examples exercise standard-library JSON as a runnable starting point. Replace the codec with the project's implementation and retain only properties guaranteed by its contract.

### 7.1. Structured Property with Hypothesis

Save as `tests/test_properties.py`.

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

Adapt the integer range to the actual format; this range is a workload choice, not a Python integer limit. Add separate known-answer and invalid-input tests. For stateful APIs, consider a Hypothesis rule-based state machine with an independent model.

### 7.2. Coverage-Guided Target with Atheris

Save as `fuzz/fuzz_json.py`. Keep `atheris.Setup` and `atheris.Fuzz` behind the main guard so importing the module does not start a campaign.

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

- Hypothesis [Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html), [Strategies](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html), and [Replaying failures](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html).
- Google [Atheris](https://github.com/google/atheris).
- LLVM [libFuzzer options](https://llvm.org/docs/LibFuzzer.html#options).
