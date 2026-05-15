---
title: "Classes"
weight: 1
---

# Classes

Classes are the most intuitive pollution target. When a class object `C` is accessible, the attacker can modify `C.v`, and from then on every read of `cls.v` or `self.v` that does not have a shadowing instance attribute returns the polluted value.

## Access mechanism: attribute lookup via the MRO

Python's attribute resolution follows the Method Resolution Order (MRO). When `instance.attr` is read, the lookup tries the instance's own `__dict__` first, then walks up the class chain:

```text
instance.attr
  1. instance.__dict__['attr']          # instance dict
  2. type(instance).__dict__['attr']    # class dict
  3. base.__dict__['attr']              # base classes (MRO)
```

If the attribute is not on the instance, the lookup falls back to the class. Polluting `C.v` therefore changes the value that every `self.v` and `cls.v` read returns, for every instance of `C` that does not shadow it:

```python
class C:
    def __init__(self):
        self.v          # falls back to cls.v when not set on the instance
    @classmethod
    def other(cls):
        cls.v           # always reads from the class
```

### Example: DoS via `__getattribute__`

```python
class User:
    def __init__(self, name):
        self.name = name

u = User("alice")
u.name             # returns "alice"

# Attacker payload (Attr-Set on User.__getattribute__):
#   User.__getattribute__ = "not_a_function"

u.name             # raises TypeError: 'str' object is not callable
```

Every attribute access on every `User` instance now raises, because Python invokes `__getattribute__` on the class for every read. This pattern is detailed on the [DoS gadgets]({{< relref "/docs/gadgets/dos" >}}) page.