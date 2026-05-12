---
title: "Defense"
weight: 7
---

# Defense Against Class Pollution

Defense against Python class pollution can be applied along the object resolution path — either at the "get" primitives or right before the "set" primitive.

## Strategy 1: Key Sanitization

Sanitize the reflective lookup keys by filtering out attacker-controlled access to dangerous attributes.

### Approach 1A: Filter Specific Dangerous Attributes

Block known dangerous attributes like `__globals__`, `__class__`, `__init__`:

```python
DANGEROUS_ATTRS = {"__globals__", "__class__", "__init__", "__subclasses__",
                   "__bases__", "__mro__", "__dict__", "__getattribute__"}

def safe_update(obj, key_path, value):
    for key in key_path.split("."):
        if key in DANGEROUS_ATTRS:
            raise ValueError(f"Access to '{key}' is not allowed")
        obj = getattr(obj, key)
```

{{< hint warning >}}
**Limitation**: This is often incomplete. An attacker can bypass by selecting alternate gadgets or modifying class methods that aren't in the blocklist. This approach was used by Pydash and is considered the weakest defense.
{{< /hint >}}

**Used by**: Pydash

### Approach 1B: Check for Leading/Trailing Underscores

Block any key that starts or ends with underscore(s):

```python
def safe_update(obj, key_path, value):
    for key in key_path.split("."):
        if key.startswith("_") or key.endswith("_"):
            raise ValueError(f"Access to private attribute '{key}' is not allowed")
        obj = getattr(obj, key)
```

**Effectiveness**: This effectively blocks access to all dunder attributes and private attributes, preventing traversal into Python's internal object structure.

**Used by**: Mesop (Google), Azure CLI (Microsoft)

### Approach 1C: Disallow Dotted Key Paths

Prevent path traversal entirely by disallowing dot-separated keys:

```python
def safe_update(obj, key, value):
    if "." in key:
        raise ValueError("Nested attribute access is not allowed")
    setattr(obj, key, value)
```

**Effectiveness**: Eliminates the "get" primitive entirely — without multi-step traversal, class pollution cannot reach dangerous targets.

**Used by**: Taipy (after fix)

## Strategy 2: Type Validation

Validate object types before performing assignments. This prevents pollution even when attacker-controlled keys resolve to unintended objects.

### Approach 2A: Restrict to Known Types

Only allow assignments to objects of expected types:

```python
from dataclasses import fields, is_dataclass

def safe_update(obj, key, value):
    if is_dataclass(obj):
        valid_fields = {f.name for f in fields(obj)}
        if key not in valid_fields:
            raise ValueError(f"'{key}' is not a valid field")
    setattr(obj, key, value)
```

### Approach 2B: Validate Against Annotations

Use type annotations to validate that the assigned value matches the expected type:

```python
def safe_update(obj, key, value):
    if hasattr(obj, '__annotations__'):
        expected_type = obj.__annotations__.get(key)
        if expected_type and not isinstance(value, expected_type):
            raise TypeError(f"Expected {expected_type}, got {type(value)}")
    setattr(obj, key, value)
```

## Strategy 3: Allowlist-Based Access

Only allow access to explicitly declared attributes:

```python
class SafeComponent:
    _allowed_attrs = {"name", "email", "age"}

    def update(self, key, value):
        if key not in self._allowed_attrs:
            raise ValueError(f"Cannot set '{key}'")
        setattr(self, key, value)
```

## Comparison of Defenses

| Defense | Completeness | Usability | Breaking Changes |
|---------|-------------|-----------|-----------------|
| Filter specific attrs | Low | High | None |
| Block underscores | High | Medium | May block legitimate private attrs |
| Disallow dots | Complete | Low | Breaks nested updates |
| Type validation | High | Medium | May reject valid polymorphic updates |
| Allowlist | Complete | Low | Requires explicit declaration |

## Recommendations

1. **For new code**: Use type validation (Strategy 2) with dataclasses or Pydantic models — this provides both safety and good developer experience
2. **For existing code (quick fix)**: Add underscore checking (Strategy 1B) — minimal code change, high effectiveness
3. **For security-critical code**: Use allowlist-based access (Strategy 3) — most restrictive but guarantees safety

{{< hint info >}}
**Key insight from our study**: The most effective real-world fixes check for leading/trailing underscores. This single check blocks the entire class pollution attack surface because all Python internal attributes use the dunder naming convention.
{{< /hint >}}
