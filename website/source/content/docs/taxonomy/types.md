---
title: "Vulnerability Types"
weight: 2
---

# Vulnerability Types

The combination of two "get" primitives and three "set" primitives yields six distinct vulnerability types, each reflecting a different attacker capability in resolving and modifying runtime structures.

## Type 1: Agnostic-Get × Dual-Set

**The only previously known type.**

The attacker can freely choose between attribute access and item access at each "get" step, and can choose between attribute assignment and item assignment at the "set" step.

```python
def update(obj, data):
    for key in data:
        val = data[key]
        if isinstance(val, dict):
            if hasattr(obj, key):
                update(getattr(obj, key), val)  # Attr-Get
            elif isinstance(obj, dict):
                update(obj[key], val)            # Item-Get
        else:
            if isinstance(obj, dict):
                obj[key] = val                   # Item-Set
            else:
                setattr(obj, key, val)           # Attr-Set
```

**Prevalence**: 106 reports (20 checked → 7 TP)

## Type 2: Constrained-Get × Dual-Set

The attacker is restricted to a fixed chain of **attribute access only** for the "get" primitive, but can choose between attribute and item assignment at the "set" step.

```python
def set_properties(instance, expression, force_string):
    key, value = _split_key_value_pair(expression)
    name, path = _get_name_path(key)
    instance = _find_property(instance, path)  # Constrained: getattr chain
    if isinstance(instance, dict):
        instance[name] = value                  # Item-Set
    else:
        setattr(instance, make_snake_case(name), value)  # Attr-Set
```

**Real-world example**: Azure CLI (CVE-2025-24049)  
**Prevalence**: 17 reports (2 checked → 1 TP)

## Type 3: Agnostic-Get × Attr-Set

The attacker can freely choose between attribute and item access at each "get" step, but is **restricted to attribute assignment** at the "set" step.

```python
def deep_set(obj, path, value):
    for key in path[:-1]:
        if isinstance(obj, dict):
            obj = obj[key]              # Item-Get
        else:
            obj = getattr(obj, key)     # Attr-Get
    setattr(obj, path[-1], value)       # Attr-Set only
```

**Prevalence**: 27 reports (1 checked → 0 TP, 1 FP)

## Type 4: Constrained-Get × Attr-Set

**The most prevalent type.** The attacker is constrained to attribute access chains, and the assignment is also restricted to attribute-based writes.

```python
def _attrsetter(obj, attr_str, value):
    var_name_split = attr_str.split(sep=".")
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)            # Constrained: getattr only
    setattr(obj, var_name_split[-1], value)     # Attr-Set only
```

**Real-world example**: Taipy (CVE-2025-30374), django-unicorn (CVE-2025-24370)  
**Prevalence**: 617 reports (56 checked → 39 TP)

{{< hint warning >}}
This is the most common pattern because many Python frameworks implement "dot-path" attribute setters (`a.b.c = value`) using `getattr` chains followed by `setattr`.
{{< /hint >}}

## Type 5: Agnostic-Get × Item-Set

The attacker can freely choose between attribute and item access for "get" steps, but is **restricted to item assignment** at the "set" step.

```python
def deep_update(obj, path, value):
    for key in path[:-1]:
        if hasattr(obj, key):
            obj = getattr(obj, key)     # Attr-Get
        else:
            obj = obj[key]              # Item-Get
    obj[path[-1]] = value               # Item-Set only
```

**Prevalence**: 80 reports (0 checked)

## Type 6: Constrained-Get × Item-Set

The attacker is constrained to attribute access chains, and **restricted to item assignment** at the "set" step.

```python
def set_nested(obj, dotted_key, value):
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        obj = getattr(obj, part)        # Constrained: getattr only
    obj[parts[-1]] = value              # Item-Set only
```

**Prevalence**: 21 reports (5 checked → 0 TP, 5 FP)

## Summary Table

| Type | Get | Set | Reports | TP | FP |
|------|-----|-----|---------|----|----|
| Agnostic × Dual | Free choice | Free choice | 106 | 7 | 13 |
| Constrained × Dual | Attr only | Free choice | 17 | 1 | 1 |
| Agnostic × Attr | Free choice | Attr only | 27 | 0 | 1 |
| **Constrained × Attr** | **Attr only** | **Attr only** | **617** | **39** | **17** |
| Agnostic × Item | Free choice | Item only | 80 | 0 | 0 |
| Constrained × Item | Attr only | Item only | 21 | 0 | 5 |
| **Total** | | | **868** | **47** | **37** |
