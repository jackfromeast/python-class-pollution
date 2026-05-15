---
title: "DoS Gadgets"
weight: 5
---

# DoS Gadgets

DoS gadgets crash the application or render it unusable. The general shape is broad: overwriting any callable target with a non-callable value (typically a string) makes every later invocation raise `TypeError: 'str' object is not callable`. 

## Cross-module DoS

In some cases, applications would wrap code in `try`/`except`, so a per-call crash often gets swallowed. The interesting DoS gadgets are the ones that escape those handlers, either by triggering before the `try` is entered, by polluting state shared across requests, or by raising in a different module that has no handler at all. The problem then becomes finding a target whose later read happens *outside* the protected scope.

Python's import system gives us such a target. When the polluted class lives in a shared module and the application's `try`/`except` only wraps the *attacker's* call site, the corruption escapes the handler. Because `import` caches modules in `sys.modules`, every importer of the shared module ends up with a reference to the *same* class object. A later read from a different module raises freely on whatever the attacker wrote, even if that module imported the class long before the pollution.

### Example

**Step 1.** `main.py` is the first module loaded by the application at startup. It imports `NN` and binds the (still pristine) class object into its own namespace.

```python
# main.py
from shared import NN                          # binds main.NN to the NN class object

def serve_request():
    return NN().toString()                     # used much later, after the request loop starts
```

**Step 2.** The framework loads `shared.py` once, on first import.

```python
# shared.py
class NN:
    def toString(self):
        return "NN"
```

**Step 3.** `extension.py` is loaded when the application registers user-installed plugins. It also imports `NN`. Because `shared` is already in `sys.modules`, the `from shared import NN` here gets the same class object that `main.py` already holds.

```python
# extension.py
from shared import NN                          # same NN object, via sys.modules cache

def pollute_and_use(payload):
    obj = NN()
    try:
        obj.__class__.toString = payload       # 1. pollutes shared.NN.toString globally
        obj.toString()                         # 2. raises TypeError on the polluted class
    except Exception:
        pass                                   # 3. handler swallows the error, no visible failure
```

**Step 4.** An attacker reaches `extension.pollute_and_use("Polluted")`. Lines 1–3 execute. The handler swallows the error and the application returns 200 OK with no log entry.

**Step 5.** Some time later, an unrelated request calls `main.serve_request()`. The `NN` reference bound back in Step 1 still points to the *same* class object as `extension.NN` and `shared.NN`, so `NN().toString()` reads the polluted attribute and raises `TypeError`. The framework's top-level handler converts the exception into a 500 or terminates the worker.

The pollution at Step 4 outlived its own try/except and reached a read site that imported the class long before the attacker even existed. That delay is what makes this gadget useful for DoS even when every attacker-reachable code path is wrapped in `try`/`except`.

## Real-world cases

| Application | Polluted property | Mechanism | CVE |
|---|---|---|---|
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | `<C>.__getattribute__` on a node configuration class | reflective attribute setter on workflow JSON | [CVE-2025-6107](https://nvd.nist.gov/vuln/detail/CVE-2025-6107) |
| [Taipy]({{< relref "/docs/collection/showcases/taipy" >}}) | `<C>.__getattribute__` on a session-state class | HTTP/SocketIO via `_attrsetter` | [CVE-2025-30374](https://nvd.nist.gov/vuln/detail/CVE-2025-30374) |
| [Mesop]({{< relref "/docs/collection/showcases/mesop" >}}) | `<C>.__getattribute__` on a dataclass | reflective dataclass update | [CVE-2025-30358](https://nvd.nist.gov/vuln/detail/CVE-2025-30358) |
| [sd-webui-controlnet](https://github.com/Mikubill/sd-webui-controlnet) | callable on a model class shared via `sys.modules` (cross-module pattern above) | reflective attribute setter on extension | Reported |