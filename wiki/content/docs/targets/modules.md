---
title: "Modules"
weight: 2
---

# Module Pollution Target

When a module `mod` is accessible, the attacker controls global variables used across modules. Module-level pollution is powerful because global variables are shared by all code that imports from that module.

## Access Mechanism: Global Variable Reference

Python modules use a global namespace (a dictionary) to store module-level variables. When code does `from mod import v` or `mod.v`, it reads from this namespace.

```python
# mod.py
def f():
    global v
    v = "safe"

# other.py
from mod import v   # Reads mod.__dict__['v']
print(v)            # → "safe"
```

## Loading Context

```python
# mod.py
def f(): global v; v    # Attacker controls the global variable
# other.py
from mod import v; v    # Used across modules
```

## How to Reach Modules

Modules are accessible through:

1. **`sys.modules`** — The global module cache containing all loaded modules
2. **`f.__globals__`** — Any function carries a reference to its defining module's `__dict__`
3. **Direct attribute access** — If the module object is reachable via traversal

```python
# Reaching sys.modules from any object:
obj.__class__.__init__.__globals__['sys'].modules

# Or via __globals__ directly:
obj.__class__.__init__.__globals__  # → module's namespace
```

## Example: Polluting Environment Variables

```python
# Traversal to os.environ:
# __class__.__init__.__globals__.sys.modules.os.environ

import os
# After pollution: os.environ["BROWSER"] = "/bin/sh -c 'malicious command'"
import antigravity  # Triggers webbrowser → reads BROWSER → RCE
```

## Example: Polluting Django Settings

```python
# Traversal to Django's SECRET_KEY:
# __init__.__globals__.sys.modules.django.conf.settings.SECRET_KEY

# After pollution: SECRET_KEY = "attacker_known_value"
# → Attacker can forge session cookies → authentication bypass
```

## Why Module Pollution Is Powerful

1. **Global scope**: Module variables are shared across the entire application
2. **Cross-module impact**: Polluting one module affects all importers
3. **Standard library**: Critical modules like `os`, `sys`, `subprocess` are always loaded
4. **No instance required**: Unlike class pollution, module pollution doesn't need multiple instances
