---
title: "FAQ"
weight: 8
---

# Frequently Asked Questions

## How is this different from JavaScript prototype pollution?

TODO: the object model is class-based, not prototype-based; Python has two namespaces
(attribute and item); there is no single root prototype to pollute — instead the attacker
reaches whichever class or module the traversal path leads to. See the
[comparison table]({{< relref "/docs/#key-differences-from-javascript-prototype-pollution" >}}).

## Why does traversal through dunder attributes work?

TODO: `getattr(obj, "__class__")` is perfectly valid Python. Dunder attributes are not
access-restricted; they are simply naming conventions. Python's data model exposes
`__class__`, `__init__`, `__globals__`, etc. on every object without any permission check.

## Does `__slots__` prevent class pollution?

TODO: `__slots__` prevents *adding new attributes* to instances, but it does not prevent
overwriting existing class-level attributes via the class object itself. The traversal
goes through `__class__` to the class, not through the instance.

## Is this exploitable without `sys.modules`?

TODO: yes — `sys.modules` is the most powerful hop because it reaches any imported module,
but even without it, polluting class-level descriptors (`__getattribute__`,
`__setattr__`) or function defaults is sufficient for DoS and logic bugs.

## Why can't I just block `__class__` at the sink?

TODO: insufficient — `__init__.__globals__` also reaches the module namespace without
going through `__class__` first. And `__subclasses__()` can reach other classes. The
defense page lists what a sound blocklist needs to contain.

## Does this affect PyPy or other Python implementations?

TODO: yes, the object model behavior (`__class__`, `__init__`, `__globals__`) is part of
the language specification, not a CPython implementation detail. PyPy, GraalPy, and
Jython all expose the same dunder attributes.
