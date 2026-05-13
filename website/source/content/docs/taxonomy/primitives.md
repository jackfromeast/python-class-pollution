---
title: "Pollution Primitives"
weight: 1
---

# Pollution Primitives

Class pollution vulnerabilities consist of multiple object access steps followed by a final object assignment step. Each step is defined as a **primitive** — with object access treated as a "get" primitive and the final assignment as a "set" primitive.

## Atomic "Get" Operations

Python supports two atomic "get" operations that differ in their working namespace and reachability:

### Attribute Access
Retrieves values from the **attribute namespace**, supported by all Python objects.

```python
getattr(obj, key)              # Most common
obj.__dict__[name]             # Direct dict access
obj.__getattribute__(name)     # Explicit call
vars(obj)[name]                # Via vars()
inspect.getmembers(obj)        # Inspection
object.__getattribute__(obj, name)  # Builtins
```

**20 syntactic variants** identified in the Python Standard Library (Table 1 of the paper).

### Item Access
Retrieves elements using keys or indexes from the **item namespace**, only supported by container objects (dictionaries, lists, sets).

```python
dict[key]                      # Most common (50.7M instances)
dict.get(key)                  # Safe get (8.6M instances)
dict.pop(key)                  # Get and remove (1.7M instances)
operator.getitem(dict, key)    # Operator module
operator.__getitem__(dict, key) # Explicit
```

{{< hint warning >}}
**Key Insight**: Attribute and item access operate on different namespaces. An attribute cannot be accessed using item lookup, and vice versa. This is a fundamental difference from JavaScript where property access is uniform.
{{< /hint >}}

## Atomic "Set" Operations

### Attribute Set (Attr-Set)
Sets attributes on objects:

```python
obj.__dict__[name] = val       # 437.8K packages
setattr(obj, name, val)        # 214.3K packages
object.__setattr__(obj, name, val)  # 11.4K packages
obj.__setattr__(name, val)     # 10.4K packages
```

### Item Set (Item-Set)
Sets items in container objects:

```python
dict[key] = val                # 7.7M packages (36.8K)
dict.update(key=val)           # 687.8K packages (22.7K)
dict.setdefault(key, val)      # 111.1K packages
dict.__setitem__(key, val)     # 7.7K packages
```

### Dual Set (eval/exec)
Can perform both attribute and item assignment:

```python
exec(f"EXPR†", {"o": obj})    # 90 packages
eval(f"EXPR‡", {"o": obj})    # 16 packages
```

## "Get" Primitives

The combination of atomic get operations forms two types of "get" primitives:

### Agnostic-Get
The attacker can freely choose between `getattr` and `getitem` at each access step.

Formed in two ways:
1. Through a **control-flow branch** that allows selection of different atomic gets across paths
2. Dynamically via **reflection functions** such as `eval` and `exec`

```python
# Example: Agnostic-Get via branching
for key in data:
    if hasattr(obj, key):
        obj = getattr(obj, key)     # attribute access
    elif isinstance(obj, dict):
        obj = obj[key]              # item access
```

### Constrained-Get
The attacker must follow a **fixed access pattern** imposed by the program logic — a chain of attribute access only.

```python
# Example: Constrained-Get (attribute chain only)
for part in path.split("."):
    obj = getattr(obj, part)
```

{{< hint info >}}
**Note**: Item access alone cannot form a valid Constrained-Get primitive for class pollution, since it operates within container objects (dictionaries) and cannot affect shared runtime objects outside the container.
{{< /hint >}}

## "Set" Primitives

Three types based on the attacker's ability to set the final object:

| Primitive | Description | Example |
|-----------|-------------|---------|
| **Dual-Set** | Can choose between attribute and item assignment | `setattr(obj, key, val)` OR `obj[key] = val` |
| **Attr-Set** | Restricted to attribute-based writes | `setattr(obj, key, val)` |
| **Item-Set** | Restricted to item-based writes | `obj[key] = val` |

## Primitive Combinations → 6 Vulnerability Types

The two "get" primitives combined with the three "set" primitives define **six types** of class pollution vulnerabilities:

| | Dual-Set | Attr-Set | Item-Set |
|---|----------|----------|----------|
| **Agnostic-Get** | Known | **New** | **New** |
| **Constrained-Get** | **New** | **New** | **New** |

The most prevalent type in practice is **Constrained-Get × Attr-Set** (617 reports out of 868).
