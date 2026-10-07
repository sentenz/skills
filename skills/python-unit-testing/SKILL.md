---
name: python-unit-testing
description: Create, modify, and review Python unit tests using pytest or an existing unittest suite, with In-Got-Want, table-driven testing, AAA, fixtures, and branch coverage. Use for Python unit tests, regression tests, test isolation, parametrization, exception assertions, async tests, or test coverage.
---

# Unit Testing

Create focused Python tests that verify observable contracts and produce actionable failures. Preserve the project's framework, supported Python versions, package layout, and dependency workflow.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
- [4. Workflow](#4-workflow)
- [5. Commands](#5-commands)
- [6. Style Guide](#6-style-guide)
- [7. Templates](#7-templates)
- [8. References](#8-references)

## 1. Benefits

- Document behavior with independently collected, descriptively named cases.
- Catch regressions at the smallest useful boundary.
- Use coverage gaps to identify missing scenarios rather than treating a percentage as proof of correctness.

## 2. Principles

Apply FIRST:

- **Fast:** Keep unit tests free of live services and unnecessary sleeps.
- **Independent:** Create fresh mutable state per test and restore changed process state.
- **Repeatable:** Control clocks, randomness, environment variables, and filesystem paths.
- **Self-Validating:** Assert explicit results, exceptions, or externally visible effects.
- **Timely:** Add a reproducing test with each behavior change or defect fix.

## 3. Patterns

| Pattern | Python application |
| --- | --- |
| In-Got-Want | Name inputs `value` or `input_value`, actual results `got`, and expectations `want`; `in` is a keyword. |
| Table-driven testing | Use `pytest.mark.parametrize` with readable case IDs; use `subTest` in existing unittest suites. |
| Arrange, Act, Assert (AAA) | Separate setup, the operation, and its assertions; keep one cohesive behavior per test. |
| Fixtures | Use function scope by default, `tmp_path` for files, and context managers or yield fixtures for cleanup. |
| Data-driven testing | Load versioned JSON/CSV cases relative to `Path(__file__)`, validate their schema, and parametrize each case. |
| Test doubles | Isolate external boundaries; use [Python Mock Testing](../python-mock-testing/SKILL.md) for interaction contracts. |

## 4. Workflow

1. Inspect `pyproject.toml`, test configuration, lockfiles, `conftest.py`, CI, and nearby tests. Determine the supported interpreters, test runner, import setup, and available plugins before adding dependencies.
2. Read the public contract and identify normal, boundary, and failure cases. Cover `None`, empty collections, Unicode, invalid types, and numeric limits only where relevant to that contract. Python integers do not have fixed-width overflow; test explicit protocol or native-extension limits instead.
3. Extend the existing layout, normally `tests/test_<module>.py`. Keep installed-package imports working through the project's environment; avoid ad hoc `sys.path` edits. Prefer pytest for a new suite, but retain unittest when already established.
4. For a bug fix, reproduce the original failure, then confirm the fix. Derive expected values independently of the implementation under test.
5. Use the appropriate [template](#7-templates). Reuse fixtures when they clarify ownership; avoid broad autouse fixtures that obscure dependencies.
6. Run the selected tests, then the affected suite. Inspect branch coverage when requested or needed to locate an untested decision. Preserve existing coverage thresholds.
7. Report changed tests, exact commands, outcomes, and any unexecuted checks. Diagnose collection failures and unexpected skips; do not report them as passing tests.

## 5. Commands

Run from the project root in its configured environment. Adapt paths to the actual suite; use an existing Make, tox, nox, uv, or Poetry task when provided. Do not assume a Make target exists.

| Command | Purpose |
| --- | --- |
| `python -m pytest tests/test_parser.py -q` | Run the affected module. |
| `python -m pytest tests/test_parser.py::test_parse_port -vv` | Run a selected behavior and show case IDs. |
| `python -m pytest --collect-only -q` | Check discovery and parametrization. |
| `python -m pytest tests -q` | Run the relevant suite. |
| `python -m coverage run --branch -m pytest tests` | Collect branch coverage when coverage.py is installed. |
| `python -m coverage report -m` | Inspect missing statements and branches. |
| `python -m unittest discover -s tests -v` | Run an existing unittest suite. |

## 6. Style Guide

- Name pytest files `test_*.py` or `*_test.py` and functions `test_<behavior>`. Keep distinct contracts in separate tests.
- Use plain `assert` for pytest diagnostics. Use `pytest.approx` with contract-appropriate tolerances for floating-point results; assert NaN and infinity explicitly where allowed.
- Match the expected exception type with `pytest.raises`; check message fragments only when stable. Keep only the operation expected to raise inside the context manager.
- Create or copy mutable parametrized inputs per case before mutation. Do not reuse mutable module-level state across tests.
- Use `monkeypatch`, `capsys`, `caplog`, and `pytest.warns` for environment, output, logging, and warning behavior when relevant.
- Close files, connections, and background tasks even after assertion failures. Prefer context managers and fixture finalizers to teardown dependent on test success.
- For async code, use the project's configured plugin and event-loop policy, or `unittest.IsolatedAsyncioTestCase`. Await the operation and test cancellation/cleanup where relevant. Never assume an unconfigured `async def` test executes correctly.
- Avoid arbitrary sleeps, assertions on private implementation details, blanket `xfail`, and disabling warnings to conceal failures. Use strict expected failures with a tracked reason when necessary.

## 7. Templates

Adapt the illustrative imports and contracts to the project; these examples expect `app.parser.parse_port(text)` to accept decimal ports 1–65535 and raise `ValueError` otherwise.

### 7.1. Table-Driven Test

```python
import pytest

from app.parser import parse_port


@pytest.mark.parametrize(
    "input_value,want",
    [
        pytest.param("1", 1, id="minimum"),
        pytest.param("443", 443, id="https"),
        pytest.param("65535", 65535, id="maximum"),
    ],
)
def test_parse_port(input_value, want):
    # Act
    got = parse_port(input_value)

    # Assert
    assert got == want
```

### 7.2. Error and Boundary Cases

```python
@pytest.mark.parametrize("input_value", ["", "0", "65536", "-1", "abc"])
def test_parse_port_rejects_invalid_input(input_value):
    with pytest.raises(ValueError):
        parse_port(input_value)
```

### 7.3. Resource Fixture

Use this standalone pattern when testing code that consumes a database connection. Replace the demonstrated query with the project's operation.

```python
import sqlite3

import pytest


@pytest.fixture
def connection():
    database = sqlite3.connect(":memory:")
    try:
        database.execute("CREATE TABLE ports (value INTEGER NOT NULL)")
        yield database
    finally:
        database.close()


def test_connection_starts_empty(connection):
    got = connection.execute("SELECT COUNT(*) FROM ports").fetchone()
    assert got == (0,)
```

### 7.4. Existing unittest Suite

```python
import unittest

from app.parser import parse_port


class TestParsePort(unittest.TestCase):
    def test_valid_ports(self):
        for input_value, want in [("1", 1), ("443", 443), ("65535", 65535)]:
            with self.subTest(input_value=input_value):
                self.assertEqual(parse_port(input_value), want)
```

## 8. References

- pytest [Parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html) and [Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html).
- Python [unittest](https://docs.python.org/3/library/unittest.html).
- coverage.py [Branch coverage](https://coverage.readthedocs.io/en/latest/branch.html).
