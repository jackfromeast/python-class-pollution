---
title: "DoS Gadgets"
weight: 3
---

# DoS Gadgets

Denial of Service gadgets crash the application or render it unusable.

## Gadget 1: `__getattribute__` Overwrite

**The most universal DoS gadget.** Works on any class.

**Mechanism**: `__getattribute__` is called for every attribute access on an object. Overwriting it with a non-callable value causes a `TypeError` on any subsequent attribute access.

**Key Path**:
```
__class__.__getattribute__
```

**Value**: `"1337"` (any non-callable)

**Effect**: Every attribute access on any instance of the class raises:
```
TypeError: 'str' object is not callable
```

### Why This Is So Effective

```python
# After pollution: User.__getattribute__ = "1337"

user.name       # → TypeError
user.email      # → TypeError
str(user)       # → TypeError (calls __str__ which needs __getattribute__)
repr(user)      # → TypeError
type(user)      # This still works (built-in, not through __getattribute__)
```

The application cannot even inspect or debug the corrupted objects. The only recovery is restarting the process.

{{< hint warning >}}
This affects **all existing and future instances** of the class, not just the polluted instance. It's a class-level corruption.
{{< /hint >}}

## Gadget 2: `__class__` Reassignment

**Mechanism**: Change an object's class to an incompatible type, causing subsequent operations to fail.

**Key Path**:
```
__class__
```

**Value**: Reference to an incompatible class

**Effect**: Method calls and attribute accesses behave unexpectedly or raise exceptions.

## Gadget 3: `__str__` / `__repr__` Overwrite

**Mechanism**: Overwrite string representation methods with non-callable values. Many logging frameworks and error handlers call `str()` or `repr()` on objects.

**Key Path**:
```
__class__.__str__
```

**Value**: `"crashed"`

**Effect**: Any logging, debugging, or string formatting involving the object crashes.

## Gadget 4: Module-Level Function Overwrite

**Mechanism**: Overwrite a frequently-called module function with `None` or a non-callable.

**Key Path** (example):
```
__init__.__globals__.json.dumps
```

**Value**: `None`

**Effect**: Any code calling `json.dumps()` crashes with `TypeError: 'NoneType' object is not callable`.

## Real-World DoS Examples

| Application | Stars | Gadget | CVE |
|-------------|-------|--------|-----|
| ComfyUI | 78.5K | `__getattribute__` overwrite | CVE-2025-6107 |
| RAGFlow | 52.8K | `__getattribute__` overwrite | - |
| Taipy | 18.1K | `__getattribute__` overwrite | CVE-2025-30374 |
| Mesop | 6.3K | `__getattribute__` overwrite | CVE-2025-30358 |
| sd-webui-controlnet | 17.6K | `__getattribute__` overwrite | - |
| stable-diffusion-webui-forge | 10.9K | `__getattribute__` overwrite | - |

## Persistent vs. Transient DoS

- **Persistent DoS**: If the polluted class/module state is preserved across requests (e.g., in a long-running web server), the DoS persists until restart
- **Transient DoS**: If each request creates fresh objects, the DoS only affects the current request

Most web frameworks use persistent class objects, making `__getattribute__` overwrite a **persistent DoS** by default.
