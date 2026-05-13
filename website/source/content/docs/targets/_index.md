---
title: "Pollution Targets"
weight: 3
bookCollapseSection: true
---

# Class Pollution Targets

A **pollution target** is a runtime object that is reachable via attribute or item access and can affect program behavior. After class pollution happens, pollution targets can be accessed by the program in two ways:

1. **Direct access** — the attacker modifies the exact attribute that is later used (e.g., setting `a.b` and the program later reads `a.b`)
2. **Indirect access** — arises from Python's data model and reflective mechanism (e.g., modifying a class variable `cls.v` affects all instances' `self.v`)

## Four Categories of Pollution Targets

| Target | Access Mechanism | Newly Discovered? |
|--------|-----------------|-------------------|
| Class | Attribute Lookup | No |
| Module | Global Variable Reference | No |
| Function (globals) | Global Variable Reference + Module Lookup | **Yes** |
| Function (kwdefaults) | Local Variable Reference | **Yes** |
| Function Closure | Local Variable Reference | **Yes** |

The **function** target (including closures) is a novel attack target discovered in this work.

## How Indirect Access Works

Python's attribute resolution follows the **Method Resolution Order (MRO)**. When an attribute is not found on an instance, Python looks up the class hierarchy:

```python
instance.attr
  → instance.__dict__['attr']        # 1. Instance dict
  → type(instance).__dict__['attr']  # 2. Class dict
  → base.__dict__['attr']           # 3. Base classes (MRO)
```

This means polluting a **class variable** affects all instances that don't explicitly override it.

Similarly, Python functions carry references to their defining module's globals (`f.__globals__`), enabling module-level pollution through any accessible function.
