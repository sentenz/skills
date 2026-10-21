# Google Python Style Guide

> Source: https://google.github.io/styleguide/pyguide.html

- [1. Golden Rules](#1-golden-rules)
- [2. Imports](#2-imports)
- [3. Type Annotations](#3-type-annotations)
- [4. Docstrings (Google Style)](#4-docstrings-google-style)
- [5. Naming Conventions](#5-naming-conventions)
- [6. Strings](#6-strings)
- [7. Comprehensions](#7-comprehensions)
- [8. Exception Handling](#8-exception-handling)
- [9. Default Arguments](#9-default-arguments)
- [10. Common Mistakes](#10-common-mistakes)

## 1. Golden Rules

1. **Follow PEP 8** as baseline — Google's guide extends it
2. **Use type annotations** for all public functions and methods
3. **4-space indentation** — no tabs
4. **Maximum line length: 80 characters**
5. **Docstrings mandatory** for all public modules, functions, classes, methods
6. **Prefer comprehensions** over `map()`/`filter()`
7. **Use f-strings** for string formatting (Python 3.6+)

---

## 2. Imports

```python
# CORRECT - stdlib, then third-party, then local
import os
import sys
from typing import Optional, List

import numpy as np

from myproject import utils

# INCORRECT
import os, sys        # one import per line
from os.path import * # never wildcard imports
```

---

## 3. Type Annotations

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

## 4. Docstrings (Google Style)

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

## 5. Naming Conventions

| Element           | Convention       | Example         |
| ----------------- | ---------------- | --------------- |
| Modules           | snake_case       | user_service.py |
| Classes           | UpperCamelCase   | UserService     |
| Functions/Methods | snake_case       | get_user_by_id  |
| Variables         | snake_case       | user_count      |
| Constants         | UPPER_SNAKE_CASE | MAX_RETRIES     |
| Protected         | _single_leading  | _internal       |
| Private           | __double_leading | __private       |

---

## 6. Strings

```python
# CORRECT - f-strings
name = "Alice"
greeting = f"Hello, {name}!"

# INCORRECT
greeting = "Hello, " + name + "!"    # use f-strings
greeting = "Hello, %s!" % name       # use f-strings
```

---

## 7. Comprehensions

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

## 8. Exception Handling

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

## 9. Default Arguments

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

## 10. Common Mistakes

| Mistake                    | Correct Approach            |
| -------------------------- | --------------------------- |
| Mutable default args       | Use None as default         |
| Wildcard imports           | Explicit imports only       |
| Bare `except`              | Catch specific exceptions   |
| `%` or `.format()` strings | Use f-strings               |
| `map()`/`filter()`         | Use comprehensions          |
| Missing docstrings         | Add Google-style docstrings |
| Missing type annotations   | Annotate public functions   |
