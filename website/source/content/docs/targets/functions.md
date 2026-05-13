---
title: "Functions"
weight: 3
---

# Function Pollution Target

Functions are a **novel pollution target** discovered in this work. Python functions carry references to their defining module's globals and can be polluted through `__kwdefaults__`, `__globals__`, and closures.

## Access Mechanism 1: Global Variable Reference via Module Lookup

When function `f` is accessible, the attacker can reach `f.__globals__["v"]` — the global variable `v` in the module where `f` is defined.

### Loading Context

```python
# mod.py
def f(): pass
v                    # Global variable in mod

# other.py
import mod
mod.f.__globals__    # → mod's entire namespace
```

### Why This Matters

Every function in Python has a `__globals__` attribute pointing to its module's `__dict__`. This means:
- From **any accessible function**, the attacker can reach the entire module namespace
- From the module namespace, `sys.modules` gives access to all loaded modules

```python
# From any function f:
f.__globals__['__builtins__']  # Built-in functions
f.__globals__['sys']           # sys module (if imported)
f.__globals__['os']            # os module (if imported)
```

## Access Mechanism 2: Local Variable Reference via `__kwdefaults__`

When function `f` is accessible, the attacker controls keyword-only parameter default values through `f.__kwdefaults__["p"]`.

### Loading Context

```python
def f(*, p="default"):
    return p

# After pollution: f.__kwdefaults__["p"] = "malicious"
f()  # → "malicious" (without passing any argument)
```

### What are Keyword-Only Parameters?

Parameters defined after `*` in a function signature (PEP 3102):

```python
def connect(host, *, timeout=30, retries=3, verify_ssl=True):
    ...

# __kwdefaults__ = {"timeout": 30, "retries": 3, "verify_ssl": True}
# Polluting verify_ssl → False bypasses SSL verification
```

{{< hint warning >}}
`__kwdefaults__` is a dictionary, so it requires **Item-Set** capability. This makes it exploitable by Agnostic-Get or Constrained-Get paired with Item-Set or Dual-Set.
{{< /hint >}}

## Access Mechanism 3: Function Closures

When a function `g` is accessible as a closure, the attacker can modify captured variables through `g.__closure__[i].cell_contents`.

### Loading Context

```python
def f(v):
    def g():
        return v       # Captured variable
    return g

g = f("safe")
g()  # → "safe"

# After pollution: g.__closure__[0].cell_contents = "malicious"
g()  # → "malicious"
```

### Closure Internals

Python closures store captured variables in `cell` objects:

```python
g.__closure__              # Tuple of cell objects
g.__closure__[0]           # First cell
g.__closure__[0].cell_contents  # The actual captured value
```

## Practical Exploitation

### Polluting `__kwdefaults__` for Config Bypass

```python
# Target function in a web framework:
def render_template(name, *, autoescape=True, cache=True):
    ...

# Pollution payload (via Item-Set):
# render_template.__kwdefaults__["autoescape"] = False
# → All templates rendered without XSS protection
```

### Polluting `__globals__` for RCE

```python
# Any accessible function gives us its module's globals:
func.__globals__['os']  # If os is imported in that module
func.__globals__['subprocess']  # If subprocess is imported

# Overwrite a "safe" function with a dangerous one:
# func.__globals__['sanitize'] = lambda x: x  # Bypass sanitization
```
