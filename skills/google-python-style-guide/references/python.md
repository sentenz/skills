# Google Python Style Guide

> Source: https://google.github.io/styleguide/pyguide.html

Read these examples as excerpts; supply project-specific types and imports before compiling or running them.

- [Golden Rules](#golden-rules)
- [1. Imports](#1-imports)
- [2. Type Annotations](#2-type-annotations)
- [3. Docstrings (Google Style)](#3-docstrings-google-style)
- [4. Naming Conventions](#4-naming-conventions)
- [5. Strings](#5-strings)
- [6. Comprehensions](#6-comprehensions)
- [7. Exception Handling](#7-exception-handling)
- [8. Default Arguments](#8-default-arguments)
- [Common Mistakes](#common-mistakes)
- [Attribution](#attribution)

## Golden Rules

1. **Follow PEP 8** as baseline — Google's guide extends it
2. **Annotate public APIs** using syntax supported by the project; retain documented exceptions
3. **4-space indentation** — no tabs
4. **Maximum line length: 80 characters**
5. **Document public APIs** with Google-style docstrings, respecting documented exceptions
6. **Prefer comprehensions** over `map()`/`filter()`
7. **Choose readable string formatting** — f-strings, `%`, and `.format()` are supported; keep logging arguments lazy

---

## 1. Imports

```python
# CORRECT - stdlib, then third-party, then local
import os
import sys
from typing import List, Optional

import numpy as np

from myproject import utils

# INCORRECT
import os, sys        # one import per line
from os.path import * # never wildcard imports
```

---

## 2. Type Annotations

```python
# CORRECT
def get_user(user_id: int) -> Optional[dict]:
    ...

def process_items(items: List[str], max_count: int = 10) -> List[str]:
    ...

# INCORRECT
def get_user(user_id):  # add type annotations
    ...
```

---

## 3. Docstrings (Google Style)

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

---

## 4. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Modules | snake_case | user_service.py |
| Classes | UpperCamelCase | UserService |
| Functions/Methods | snake_case | get_user_by_id |
| Variables | snake_case | user_count |
| Constants | UPPER_SNAKE_CASE | MAX_RETRIES |
| Non-public | single leading underscore | _internal |

---

## 5. Strings

```python
# CORRECT - f-strings
name = "Alice"
greeting = f"Hello, {name}!"

# Other supported formatting forms
greeting = "Hello, " + name + "!"
greeting = "Hello, %s!" % name
```

---

## 6. Comprehensions

```python
# CORRECT
squares = [x ** 2 for x in range(10)]
user_map = {user.id: user for user in users}
unique_names = {user.name for user in users}
evens = [x for x in range(20) if x % 2 == 0]

# INCORRECT
squares = list(map(lambda x: x ** 2, range(10)))  # use comprehension
```

---

## 7. Exception Handling

```python
# CORRECT - catch specific exceptions
try:
    data = json.loads(raw_input)
except json.JSONDecodeError as e:
    raise ValueError(f"Could not parse: {e}") from e

# CORRECT - use context managers
with open("data.txt") as file:
    content = file.read()

# INCORRECT
try:
    ...
except:     # never bare except
    pass
```

---

## 8. Default Arguments

```python
# INCORRECT - mutable default arguments
def add_item(item: str, items: List[str] = []) -> List[str]:  # BAD!
    items.append(item)
    return items

# CORRECT - use None for mutable defaults
def add_item(item: str, items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

---

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

## Attribution

Adapted from [TestDino's companion guide](https://github.com/testdino-hq/google-styleguides-skills/blob/8674a2a2186a02f86852e061f6166a500ae30f7c/python/python.md). See [the skill](../SKILL.md#sources-and-license) for adaptation details and [LICENSE](../LICENSE) for the preserved MIT terms. This summary does not replace the primary Google guide.
