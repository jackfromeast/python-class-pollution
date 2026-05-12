---
title: "Classes"
weight: 1
---

# Class Pollution Target

Classes are the most intuitive pollution target. When a class variable `C.v` is accessible, the attacker can control `cls.v` and `self.v` when the attribute is not defined on the instance.

## Access Mechanism: Attribute Lookup

Python's attribute resolution uses the Method Resolution Order (MRO). If an attribute is not found on the instance, Python traverses the class hierarchy:

```python
class User:
    role = "user"  # Class variable

    def __init__(self, name):
        self.name = name  # Instance variable

admin = User("admin")
print(admin.role)  # → "user" (resolved from class)

# After pollution: User.role = "admin"
print(admin.role)  # → "admin" (all instances affected!)
```

## Loading Context

```python
class C:
    def __init__(self): self.v    # Attacker controls cls.v and self.v
    @classmethod
    def other(cls): cls.v         # When attribute not on instance
```

## Why This Is Dangerous

1. **Affects all instances**: Modifying a class attribute changes the behavior of every existing and future instance
2. **Dunder methods**: Class-level dunder methods (`__getattribute__`, `__str__`, etc.) are always resolved from the class, never the instance
3. **Metaclass escalation**: Via `__class__`, the attacker can reach the class of the class (metaclass), broadening the attack surface

## Example: DoS via `__getattribute__`

```python
# Vulnerable code:
def update(user, data):
    for key in data:
        val = data[key]
        if isinstance(val, dict):
            update(getattr(user, key), val)
        else:
            setattr(user, key, val)

# Payload:
data = {"__class__": {"__getattribute__": "not_a_function"}}

# After pollution:
# User.__getattribute__ = "not_a_function"
# ANY attribute access on ANY User instance raises TypeError
```

## Traversal Paths

From any instance, the attacker can reach:

```
instance
  → __class__ → Class
    → __bases__[0] → Base Class (object)
    → __init__ → Function
      → __globals__ → Module namespace
        → sys.modules → ALL loaded modules
```

This traversal chain is the foundation for most class pollution exploits.
