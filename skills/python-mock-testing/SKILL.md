---
name: python-mock-testing
description: Create and review Python tests with unittest.mock, autospec, AsyncMock, pytest monkeypatch, and test doubles. Use for mocked dependencies, patch targets, stubs, fakes, interaction assertions, failure injection, async collaborators, or isolating network, filesystem, clock, and environment boundaries.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "test double"
      - "mock test"
      - "python mock"
      - "unittest.mock"
      - "patch object"
      - "create mock"
      - "mocking"
      - "stub"
    match:
      languages: ["python"]
      paths: ["**/test*.py", "**/*_test.py", "tests/**/*.py"]
      prompt_regex: '(?i)(mock test|python mock|unittest\.mock|patch object|create mock|mocking|stub|fake)'
    usage:
      load_on_prompt: true
      autodispatch: true
---

# Mock Testing

Mock testing verifies a unit's behavior when controlled test doubles replace its collaborators. Python's standard-library [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) provides configurable return values, exception injection, and interaction assertions for use with [pytest](https://docs.pytest.org/en/stable/) or unittest.

This skill guides dependency isolation and contract verification. Use pytest-mock only when the project already provides it; the standard-library examples require no additional mocking package.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. FIRST](#21-first)
- [3. Patterns](#3-patterns)
  - [3.1. Test Double Categories](#31-test-double-categories)
  - [3.2. Configuration and Verification](#32-configuration-and-verification)
- [4. Workflow](#4-workflow)
- [5. Commands](#5-commands)
- [6. Style Guide](#6-style-guide)
- [7. Templates](#7-templates)
  - [7.1. Lookup-Site Patch and Failure Injection](#71-lookup-site-patch-and-failure-injection)
  - [7.2. Bounded Retry](#72-bounded-retry)
  - [7.3. Async Dependency](#73-async-dependency)
- [8. References](#8-references)

## 1. Benefits

Controlled collaborators expose dependency behavior that is difficult to reproduce reliably through live services.

1. Failure-Path Coverage

    Configured exceptions and responses exercise error handling without depending on service availability.

2. Interaction Verification

    Call and await assertions verify contractual retries, persistence, and notifications.

3. Interface Conformance

    Constrained test doubles detect calls that diverge from the specified collaborator interface.

## 2. Principles

Mock-test design applies isolation to both the unit under test and the lifetime of each substituted dependency.

### 2.1. FIRST

FIRST groups five test-design properties: Fast, Independent, Repeatable, Self-Validating, and Timely.

1. Fast

    Test doubles replace costly external operations with bounded local behavior.

2. Independent

    Each case owns its test doubles, and every patch has an explicit lifetime.

3. Repeatable

    Configured return values, exceptions, and clocks reproduce the intended dependency behavior.

4. Self-Validating

    Assertions verify the result and the interactions required by the contract.

5. Timely

    Failure-path coverage accompanies the introduction of each dependency.

## 3. Patterns

Test doubles are classified by their role in a test. Configuration and verification techniques constrain how those doubles represent a collaborator.

### 3.1. Test Double Categories

Stubs supply responses, mocks verify interactions, and fakes implement a bounded substitute for stateful behavior.

| Category | Application |
| --- | --- |
| Stub | Return a known value when the interaction itself is unimportant. |
| Mock | Verify externally meaningful calls and arguments. |
| Fake | Use a small in-memory implementation when stateful behavior would make mocks brittle. |

### 3.2. Configuration and Verification

The following techniques preserve signatures, inject failures, and verify asynchronous execution.

| Technique | Application |
| --- | --- |
| Autospec | Constrain calls to the real callable signature with `autospec=True` or `create_autospec`. |
| Failure Injection | Use `side_effect` for a specific exception or a bounded retry sequence. |
| Asynchronous Verification | Use an async-aware autospec or `AsyncMock`; assert awaits as well as results. |

## 4. Workflow

The workflow identifies the dependency boundary, configures its substitute, and verifies the unit's observable behavior.

1. Inspect Dependencies

    Read the target module, its imports, dependency interfaces, and nearby tests. Identify the observable contract and the narrowest external boundary.

2. Select Test Double

    Choose a real lightweight dependency, fake, stub, or mock based on the behavior needed. Do not mock the function being tested.

3. Resolve Patch Target

    Resolve the lookup location before patching. For `from app.transport import fetch` inside `app.service`, patch `app.service.fetch`. Patch where the consumer looks up the symbol, not automatically where it was defined.

4. Configure Behavior

    Specify representative return values and expected exceptions. Prefer autospec or `spec_set` when practical; account for attributes created only in `__init__` and descriptors that introspection may evaluate.

5. Exercise Scenarios

    Exercise success, failure, and relevant retry/cancellation paths. For retries, inject a clock or patch the lookup of sleep; avoid wall-clock delays.

6. Verify Contract

    Verify returned values or state first, then required interactions. Test restoration by running the surrounding suite, not only the isolated test.

7. Report Coverage

    Report the boundary replaced, scenarios covered, commands run, and remaining integration coverage. Mocks alone do not verify compatibility with a real service.

## 5. Commands

Use the project's environment and existing test task; replace example paths with actual ones. `unittest.mock` needs no additional package.

| Command | Purpose |
| --- | --- |
| `python -m pytest tests/test_service.py -q` | Run the affected tests. |
| `python -m pytest tests/test_service.py -k retry -vv` | Diagnose retry scenarios. |
| `python -m pytest tests -q` | Check interactions with the surrounding suite. |
| `python -m unittest discover -s tests -v` | Run existing unittest-based mocks. |

## 6. Style Guide

These conventions constrain patch scope and prevent mock behavior from obscuring a production defect.

1. Patch Lifetime

    Use `patch` as a context manager, a managed fixture, or a decorator. If `patcher.start()` is required in unittest setup, immediately register `self.addCleanup(patcher.stop)`.

2. Environment and Filesystem State

    Use [pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) through `monkeypatch.setenv` and `delenv` for environment state; use `tmp_path` for real temporary files when file semantics matter.

3. Return Values

    Configure concrete values that represent the expected dependency response. An unconfigured `MagicMock` can satisfy truthiness checks or propagate through production logic without exercising the intended path.

4. Call Assertions

    Use `assert_called_once_with` and `assert_not_called` for contractual interactions. Do not write `assert mock.assert_called_once_with(...)`; assertion helpers return `None` on success.

5. Call Sequences

    Use `assert_has_calls` only when a sequence matters. It allows extra calls before and after the sequence; compare `call_args_list` when the exact sequence and count are required.

6. Context Managers

    Configure context-manager results through `return_value.__enter__.return_value`, or `__aenter__` for asynchronous contexts, only when the real application programming interface (API) has those methods.

7. Await Assertions

    Use `assert_awaited_once_with` for asynchronous work. A call assertion alone does not prove a coroutine was awaited.

8. Mock State

    Prefer fresh mocks over resetting shared ones. `reset_mock()` does not clear configured return values or side effects by default.

9. Integration Coverage

    Avoid patching private implementation chains or copying a collaborator's implementation into a fake. Add separate integration tests for essential real boundary behavior.

## 7. Templates

Adapt the following contracts to existing application code. The illustrative `app.service` module imports `fetch` using `from app.transport import fetch`; `get_name(user_id)` returns `fetch(user_id)["name"]` and propagates `TimeoutError`. Its `get_name_with_retry` retries once after a timeout.

### 7.1. Lookup-Site Patch and Failure Injection

The patch replaces the symbol resolved by `app.service`, and autospec constrains the call signature.

Example:

```python
from unittest.mock import patch

import pytest

from app.service import get_name


@pytest.mark.parametrize(
    "user_id,want",
    [("user-1", "Ada"), ("user-2", "Grace")],
)
def test_get_name(user_id, want):
    # Arrange
    with patch("app.service.fetch", autospec=True) as fetch:
        fetch.return_value = {"name": want}

        # Act
        got = get_name(user_id)

        # Assert
        assert got == want
        fetch.assert_called_once_with(user_id)


def test_get_name_propagates_timeout():
    with patch("app.service.fetch", autospec=True) as fetch:
        fetch.side_effect = TimeoutError("upstream unavailable")
        with pytest.raises(TimeoutError):
            get_name("user-1")
        fetch.assert_called_once_with("user-1")
```

### 7.2. Bounded Retry

The side-effect sequence represents one timeout followed by a successful response. The call list verifies the exact retry count.

Example:

```python
from unittest.mock import call, patch

from app.service import get_name_with_retry


def test_get_name_retries_once():
    with patch("app.service.fetch", autospec=True) as fetch:
        fetch.side_effect = [TimeoutError("temporary"), {"name": "Ada"}]

        got = get_name_with_retry("user-1")

        assert got == "Ada"
        assert fetch.call_args_list == [call("user-1"), call("user-1")]
```

Also test exhausted retries and non-retryable errors according to the application contract; do not hide unlimited retries with an endlessly successful stub.

### 7.3. Async Dependency

For a project using [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html), the example assumes `get_name_async` awaits the asynchronous `fetch_async` imported into `app.service`. Autospec creates an async-aware mock for that collaborator. Use the project's existing asynchronous runner if different.

Example:

```python
from unittest.mock import patch

import pytest

from app.service import get_name_async


@pytest.mark.asyncio
async def test_get_name_async():
    with patch("app.service.fetch_async", autospec=True) as fetch:
        fetch.return_value = {"name": "Ada"}

        got = await get_name_async("user-1")

        assert got == "Ada"
        fetch.assert_awaited_once_with("user-1")
```

## 8. References

- Python Software Foundation [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) documentation.
- Python Software Foundation [Mock Examples](https://docs.python.org/3/library/unittest.mock-examples.html) documentation.
- pytest [Monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) documentation.
- pytest-asyncio [Concepts](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html) documentation.
