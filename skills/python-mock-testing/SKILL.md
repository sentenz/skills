---
name: python-mock-testing
description: Create and review Python tests with unittest.mock, autospec, AsyncMock, pytest monkeypatch, and test doubles. Use for mocked dependencies, patch targets, stubs, fakes, interaction assertions, failure injection, async collaborators, or isolating network, filesystem, clock, and environment boundaries.
---

# Mock Testing

Isolate Python collaborators while preserving the behavior of the unit under test. Use the standard-library `unittest.mock` with pytest or unittest; use pytest-mock only when the project already provides it.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
- [4. Workflow](#4-workflow)
- [5. Commands](#5-commands)
- [6. Style Guide](#6-style-guide)
- [7. Templates](#7-templates)
- [8. References](#8-references)

## 1. Benefits

- Exercise failure paths without depending on unavailable services.
- Verify contractual interactions such as retries, persistence, and notifications.
- Detect drift in collaborator signatures with constrained test doubles.

## 2. Principles

Apply FIRST:

- **Fast:** Replace costly external boundaries with focused doubles.
- **Independent:** Create new doubles per case and scope every patch.
- **Repeatable:** Configure return values, exceptions, and time explicitly.
- **Self-Validating:** Assert the result and only interactions required by the contract.
- **Timely:** Add failure-path coverage when introducing a dependency.

## 3. Patterns

| Pattern | Application |
| --- | --- |
| Stub | Return a known value when the interaction itself is unimportant. |
| Mock | Verify externally meaningful calls and arguments. |
| Fake | Use a small in-memory implementation when stateful behavior would make mocks brittle. |
| Autospec | Constrain calls to the real callable signature with `autospec=True` or `create_autospec`. |
| Failure injection | Use `side_effect` for a specific exception or a bounded retry sequence. |
| Async collaborator | Use an async-aware autospec or `AsyncMock`; assert awaits as well as results. |

## 4. Workflow

1. Read the target module, its imports, dependency interfaces, and nearby tests. Identify the observable contract and the narrowest external boundary.
2. Choose a real lightweight dependency, fake, stub, or mock based on the behavior needed. Do not mock the function being tested.
3. Resolve the lookup location before patching. For `from app.transport import fetch` inside `app.service`, patch `app.service.fetch`. Patch where the consumer looks up the symbol, not automatically where it was defined.
4. Specify representative return values and expected exceptions. Prefer autospec or `spec_set` when practical; account for attributes created only in `__init__` and descriptors that introspection may evaluate.
5. Exercise success, failure, and relevant retry/cancellation paths. For retries, inject a clock or patch the lookup of sleep; avoid wall-clock delays.
6. Verify returned values or state first, then required interactions. Test restoration by running the surrounding suite, not only the isolated test.
7. Report the boundary replaced, scenarios covered, commands run, and remaining integration coverage. Mocks alone do not verify compatibility with a real service.

## 5. Commands

Use the project's environment and existing test task; replace example paths with actual ones. `unittest.mock` needs no additional package.

| Command | Purpose |
| --- | --- |
| `python -m pytest tests/test_service.py -q` | Run the affected tests. |
| `python -m pytest tests/test_service.py -k retry -vv` | Diagnose retry scenarios. |
| `python -m pytest tests -q` | Check interactions with the surrounding suite. |
| `python -m unittest discover -s tests -v` | Run existing unittest-based mocks. |

## 6. Style Guide

- Use `patch` as a context manager, a managed fixture, or a decorator. If `patcher.start()` is required in unittest setup, immediately register `self.addCleanup(patcher.stop)`.
- Use `monkeypatch.setenv` and `delenv` for environment state; use `tmp_path` for real temporary files when file semantics matter.
- Configure meaningful concrete return values. An unconfigured `MagicMock` can accidentally satisfy truthiness checks or propagate through production logic.
- Use `assert_called_once_with` and `assert_not_called` for contractual interactions. Do not write `assert mock.assert_called_once_with(...)`; assertion helpers return `None` on success.
- Use `assert_has_calls` only when a sequence matters. It allows extra calls before and after the sequence; compare `call_args_list` when the exact sequence and count are required.
- Configure context-manager results through `return_value.__enter__.return_value`, or `__aenter__` for async contexts, only when the real API has those methods.
- Use `assert_awaited_once_with` for async work. A call assertion alone does not prove a coroutine was awaited.
- Prefer fresh mocks over resetting shared ones. `reset_mock()` does not clear configured return values or side effects by default.
- Avoid patching private implementation chains or copying a collaborator's implementation into a fake. Add separate integration tests for essential real boundary behavior.

## 7. Templates

Adapt the following contracts to existing application code. The illustrative `app.service` module imports `fetch` using `from app.transport import fetch`; `get_name(user_id)` returns `fetch(user_id)["name"]` and propagates `TimeoutError`. Its `get_name_with_retry` retries once after a timeout.

### 7.1. Lookup-Site Patch and Failure Injection

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

For a project using pytest-asyncio, assume `get_name_async` awaits the async `fetch_async` imported into `app.service`. Async autospec creates an async-aware mock. Use the project's existing async runner if different.

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

- Python [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) and [Mock examples](https://docs.python.org/3/library/unittest.mock-examples.html).
- pytest [Monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html).
- pytest-asyncio [Concepts](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html).
