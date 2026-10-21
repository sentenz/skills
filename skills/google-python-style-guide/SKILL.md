---
name: python
description: Google's official Python style guide extending PEP 8. Covers type annotations, Google-style docstrings, imports, naming conventions, f-strings, comprehensions, and exception handling. Enforces 80-char line length and 4-space indentation.
---

# Google Python Style Guide

> Official Google Python coding standards extending PEP 8.

- [1. Golden Rules](#1-golden-rules)
- [2. Quick Reference](#2-quick-reference)
  - [2.1. Naming Conventions](#21-naming-conventions)
  - [2.2. Type Annotations](#22-type-annotations)
  - [2.3. Docstrings (Google Style)](#23-docstrings-google-style)
  - [2.4. Imports](#24-imports)
  - [2.5. String Formatting](#25-string-formatting)
  - [2.6. Comprehensions](#26-comprehensions)
  - [2.7. Exception Handling](#27-exception-handling)
  - [2.8. Default Arguments](#28-default-arguments)
- [3. Common Mistakes](#3-common-mistakes)
- [4. When to Use This Guide](#4-when-to-use-this-guide)
- [5. Install](#5-install)
- [6. Full Guide](#6-full-guide)

## 1. Golden Rules

1. **Follow PEP 8** as baseline — Google's guide extends it
2. **Use type annotations** for all public functions and methods
3. **4-space indentation** — no tabs
4. **Maximum line length: 80 characters**
5. **Docstrings mandatory** for all public modules, functions, classes, methods
6. **Prefer comprehensions** over `map()`/`filter()`
7. **Use f-strings** for string formatting (Python 3.6+)

## 2. Quick Reference

### 2.1. Naming Conventions

| Element           | Convention       | Example           |
| ----------------- | ---------------- | ----------------- |
| Modules           | snake_case       | `user_service.py` |
| Classes           | UpperCamelCase   | `UserService`     |
| Functions/Methods | snake_case       | `get_user_by_id`  |
| Variables         | snake_case       | `user_count`      |
| Constants         | UPPER_SNAKE_CASE | `MAX_RETRIES`     |
| Protected         | _single_leading  | `_internal`       |
| Private           | __double_leading | `__private`       |

### 2.2. Type Annotations

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

### 2.3. Docstrings (Google Style)

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

### 2.4. Imports

```python
# ✓ CORRECT - stdlib, then third-party, then local
import os
import sys
from typing import Optional, List

import numpy as np

from myproject import utils

# ✗ INCORRECT
import os, sys        # one import per line
from os.path import * # never wildcard imports
```

### 2.5. String Formatting

```python
# ✓ CORRECT - f-strings
name = "Alice"
greeting = f"Hello, {name}!"

# ✗ INCORRECT
greeting = "Hello, " + name + "!"    # use f-strings
greeting = "Hello, %s!" % name       # use f-strings
```

### 2.6. Comprehensions

```python
# ✓ CORRECT
squares = [x ** 2 for x in range(10)]
user_map = {user.id: user for user in users}
evens = [x for x in range(20) if x % 2 == 0]

# ✗ INCORRECT
squares = list(map(lambda x: x ** 2, range(10)))  # use comprehension
```

### 2.7. Exception Handling

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

### 2.8. Default Arguments

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

## 3. Common Mistakes

| Mistake                    | Correct Approach            |
| -------------------------- | --------------------------- |
| Mutable default args       | Use None as default         |
| Wildcard imports           | Explicit imports only       |
| Bare `except`              | Catch specific exceptions   |
| `%` or `.format()` strings | Use f-strings               |
| `map()`/`filter()`         | Use comprehensions          |
| Missing docstrings         | Add Google-style docstrings |
| Missing type annotations   | Annotate public functions   |

## 4. When to Use This Guide

- Writing new Python code
- Refactoring existing Python
- Code reviews
- Setting up linting rules (pylint, flake8)
- Onboarding new team members

## 5. Install

```bash
npx skills add testdino-hq/google-styleguides-skills/python
```

## 6. Full Guide

See [python.md](references/python.md) references for complete details, examples, and edge cases.
