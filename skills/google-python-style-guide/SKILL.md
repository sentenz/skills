---
name: google-python-style-guide
description: Apply Google Python style guidance when writing, reviewing, or refactoring Python code, auditing imports, naming, type annotations, Google-style docstrings, comprehensions, or exception handling. Use for Google Python style requests; preserve repository conventions and delegate test design to dedicated testing skills.
---

# Google Python Style Guide

> Apply this third-party adaptation of Google style guidance within the target project's conventions. Code blocks illustrate individual rules; supply project-specific types and imports before running them.

## Workflow

1. Inspect repository instructions, nearby code, formatter and linter settings, and the supported language version before proposing edits. Give explicit project requirements precedence and explain any conflict with Google guidance.
2. Read [the companion guide](references/python.md) for the relevant topic. Keep changes scoped to the requested files and preserve behavior and public APIs unless a change is explicitly requested.
3. Separate automatic formatting from rules requiring judgment. Use existing project tools; do not introduce dependencies or rewrite tool configuration solely to enforce this skill.
4. For reviews, report file and line, the applicable rule, and a concrete correction. Distinguish project-specific choices from defects.
5. Run the existing formatter, relevant lint checks, and affected tests when available. Report the commands and results, including checks that could not run.

## Golden Rules

1. **Follow PEP 8** as baseline — Google's guide extends it
2. **Annotate public APIs** using syntax supported by the project; retain documented exceptions
3. **4-space indentation** — no tabs
4. **Maximum line length: 80 characters**
5. **Document public APIs** with Google-style docstrings, respecting documented exceptions
6. **Prefer comprehensions** over `map()`/`filter()`
7. **Choose readable string formatting** — f-strings, `%`, and `.format()` are supported; keep logging arguments lazy

## Quick Reference

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Modules | snake_case | `user_service.py` |
| Classes | UpperCamelCase | `UserService` |
| Functions/Methods | snake_case | `get_user_by_id` |
| Variables | snake_case | `user_count` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Non-public | single leading underscore | `_internal` |

### Type Annotations

```python
# ✓ CORRECT
def get_user(user_id: int) -> Optional[dict]:
    ...

def process_items(items: List[str], max_count: int = 10) -> List[str]:
    ...

# ✗ INCORRECT
def get_user(user_id):  # missing type annotations
    ...
```

### Docstrings (Google Style)

```python
def fetch_data(url: str, timeout: int = 30) -> dict:
    """Fetches data from the given URL.

    Args:
        url: The URL to fetch data from.
        timeout: Request timeout in seconds. Defaults to 30.

    Returns:
        A dictionary containing the response data.

    Raises:
        ValueError: If the URL is invalid.
    """
    ...
```

### Imports

```python
# ✓ CORRECT - stdlib, then third-party, then local
import os
import sys
from typing import List, Optional

import numpy as np

from myproject import utils

# ✗ INCORRECT
import os, sys        # one import per line
from os.path import * # never wildcard imports
```

### String Formatting

```python
# ✓ CORRECT - f-strings
name = "Alice"
greeting = f"Hello, {name}!"

# Other supported formatting forms
greeting = "Hello, " + name + "!"
greeting = "Hello, %s!" % name
```

### Comprehensions

```python
# ✓ CORRECT
squares = [x ** 2 for x in range(10)]
user_map = {user.id: user for user in users}
evens = [x for x in range(20) if x % 2 == 0]

# ✗ INCORRECT
squares = list(map(lambda x: x ** 2, range(10)))  # use comprehension
```

### Exception Handling

```python
# ✓ CORRECT - catch specific exceptions
try:
    data = json.loads(raw_input)
except json.JSONDecodeError as e:
    raise ValueError(f"Could not parse: {e}") from e

# ✗ INCORRECT
try:
    ...
except:     # never bare except
    pass
```

### Default Arguments

```python
# ✗ INCORRECT - mutable default arguments
def add_item(item: str, items: List[str] = []) -> List[str]:  # BAD!
    items.append(item)
    return items

# ✓ CORRECT - use None for mutable defaults
def add_item(item: str, items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

## Common Mistakes

| Mistake | Correct Approach |
|---|---|
| Mutable default args | Use None as default |
| Wildcard imports | Explicit imports only |
| Bare `except` | Catch specific exceptions |
| Eager formatting in logging | Pass the format string and arguments separately |
| `map()`/`filter()` | Use comprehensions |
| Missing docstrings | Add Google-style docstrings |
| Missing type annotations | Annotate public functions |

## Scope and Validation

Prefer a single leading underscore for non-public names; Google discourages double-underscore name mangling. Keep logging lazy, for example `logger.info("Loaded %s records", count)`. Use the project's existing formatter, lint, type-check, and affected test targets. A formatter does not verify Google-style docstrings, API contracts, or exception handling. Use the dedicated Python testing skills for test design.

## Full Guide

Read [the companion guide](references/python.md) for additional examples. Treat both files as summaries; consult the primary Google guide for exceptions or disputed rules.

## Sources and License

Adapted from [TestDino's Python skill](https://github.com/testdino-hq/google-styleguides-skills/tree/8674a2a2186a02f86852e061f6166a500ae30f7c/python) at commit `8674a2a2186a02f86852e061f6166a500ae30f7c`, including its companion guide. Copyright (c) 2026 TestDino; see [LICENSE](LICENSE) for the preserved MIT terms. This is a third-party adaptation, not an official Google skill.

Local changes rename the skill, relocate the companion guide, add repository-aware workflow and validation, and qualify oversimplified rules. Consult the [primary Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for authoritative guidance. Keep this attribution and the license when redistributing either file.
