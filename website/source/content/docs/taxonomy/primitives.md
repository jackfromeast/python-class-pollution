---
title: "Pollution Primitives"
weight: 2
---

# Pollution Primitives

A *pollution primitive* describes what an attacker can choose at each step of the access-then-assign sequence. The "get" primitive captures choices across the access steps. The "set" primitive captures the final assignment.

The atomic operations that compose each primitive are listed on the [Get & Set Atomics]({{< relref "atomics" >}}) page.

## Get primitives

There are two get primitives, distinguished by whether the program lets the attacker choose between attribute access and item access at each step.

**Agnostic-Get.** The attacker can pick either atomic at every step. This shape arises in two ways. The first is a control-flow branch that selects different atomics on different paths.

```python
for key in path:
    if isinstance(obj, dict):       # branching
        obj = obj[key]              # item access
    else:
        obj = getattr(obj, key)     # attribute access
```

The second is a hybrid reflection function such as `eval` or `exec`, which evaluates an expression that can use either form depending on the input.

**Constrained-Get.** The program fixes one atomic at every step, and the attacker must follow that pattern. In practice this is almost always a chain of attribute accesses, because item access alone cannot escape its container.

```python
for part in path.split("."):
    obj = getattr(obj, part)        # attribute only
```

## Set primitives

There are three set primitives, distinguished by whether the program lets the attacker choose between attribute and item assignment at the final write.

| Primitive | Attacker capability | Example |
|---|---|---|
| **Dual-Set** | Either attribute or item assignment | `setattr(obj, k, v)` or `obj[k] = v` |
| **Attr-Set** | Attribute assignment only | `setattr(obj, k, v)` |
| **Item-Set** | Item assignment only | `obj[k] = v` |

## Six variants

The two get primitives combined with the three set primitives yield the six pollution variants summarized in the [capability matrix]({{< relref "/docs/taxonomy" >}}#capability-matrix). Each subsection below gives the shape of the variant, a minimal Python snippet, and one observed real-world case.

| Variant | Get | Set | Status |
|---|---|---|---|
| [Agnostic-Get × Dual-Set](#agnostic-get--dual-set) | Agnostic | Dual | Previously known |
| [Agnostic-Get × Attr-Set](#agnostic-get--attr-set) | Agnostic | Attr | New |
| [Agnostic-Get × Item-Set](#agnostic-get--item-set) | Agnostic | Item | New |
| [Constrained-Get × Dual-Set](#constrained-get--dual-set) | Constrained | Dual | New |
| [Constrained-Get × Attr-Set](#constrained-get--attr-set) | Constrained | Attr | New |
| [Constrained-Get × Item-Set](#constrained-get--item-set) | Constrained | Item | New |

### Agnostic-Get × Dual-Set

The most permissive variant. The attacker chooses attribute or item access at every step and can use either atomic for the final write. This is the only variant documented before our work, and it covers the canonical recursive-merge bug pattern (Program A from the [taxonomy overview]({{< relref "/docs/taxonomy" >}})).

```python
def update(obj, data):
    for k, v in data.items():
        if isinstance(v, dict):
            if isinstance(obj, dict):
                update(obj[k], v)
            else:
                update(getattr(obj, k), v)
        else:
            if isinstance(obj, dict):
                obj[k] = v
            else:
                setattr(obj, k, v)
```

Observed in: pydash ([`set_`](https://blog.abdulrah33m.com/prototype-pollution-in-python/)), Azure CLI ([`set_properties`]({{< relref "/docs/collection/showcases/azure-cli" >}}#vulnerability)), and django-unicorn ([`set_property_value`]({{< relref "/docs/collection/showcases/django-unicorn" >}}#vulnerability)).

### Agnostic-Get × Item-Set

The traversal is mixed, but the final write is always an item assignment. There are two ways this is exploitable.

The first is when the final target is a dict-like, such as `__globals__`, `os.environ`, or `sys.modules`, where `obj[k] = v` directly modifies the entry.

```python
def assign(obj, path, val):
    for k in path[:-1]:
        obj = obj[k] if isinstance(obj, dict) else getattr(obj, k)
    obj[path[-1]] = val
```

The second is when the target is a general object with a writable `__dict__`. In that case the agnostic traversal lets the attacker step into `__dict__` and the final item-write becomes an attribute write, because `a.v = x` is semantically equivalent to `a.__dict__["v"] = x`. This means Agnostic-Get × Item-Set has the same effective capability as Agnostic-Get × Dual-Set: any attribute set reachable by the latter can be re-encoded as an item set on `__dict__` by the former.

Observed in: see the [Collection]({{< relref "/docs/collection" >}}) for confirmed cases.

### Agnostic-Get × Attr-Set

The attacker can mix attribute and item access during traversal, but the final write is always an attribute assignment. The dual-namespace traversal lets the attacker reach a class or module, and then the program forces an attribute write at the sink.

```python
def assign(obj, path, val):
    for k in path[:-1]:
        obj = obj[k] if isinstance(obj, dict) else getattr(obj, k)
    setattr(obj, path[-1], val)
```

Observed in: see the [Collection]({{< relref "/docs/collection" >}}) for confirmed cases.

### Constrained-Get × Dual-Set

Single-atomic traversal, typically `getattr` only, with both `setattr` and `obj[k] = v` available as the sink. The branch that picks between the two writes is usually based on the target type.

```python
def assign(obj, path, val):
    for part in path[:-1]:
        obj = getattr(obj, part)
    if isinstance(obj, dict):
        obj[path[-1]] = val
    else:
        setattr(obj, path[-1], val)
```

Observed in: Google Mesop ([`_recursive_update_dataclass_from_json_obj`]({{< relref "/docs/collection/showcases/mesop" >}}#vulnerability)).

### Constrained-Get × Attr-Set

The most prevalent variant in our scan. The program walks an attribute chain via `getattr` and ends with `setattr`. This is the shape of Program B from the [taxonomy overview]({{< relref "/docs/taxonomy" >}}), and it is easy to introduce by accident in any "deep set by dotted path" helper.

```python
def deep_set(obj, dotted, val):
    parts = dotted.split(".")
    for p in parts[:-1]:
        obj = getattr(obj, p)
    setattr(obj, parts[-1], val)
```

Observed in: Taipy ([`_attrsetter`]({{< relref "/docs/collection/showcases/taipy" >}}#vulnerability)).

### Constrained-Get × Item-Set

Single-atomic traversal followed by an item write. Pure item-only walks rarely escape their container, so this variant most commonly appears when the constrained traversal uses attribute access to reach a module or class and only the final write is constrained to item form.

```python
def assign(obj, path, val):
    for part in path[:-1]:
        obj = getattr(obj, part)
    obj[path[-1]] = val
```

Observed in: see the [Collection]({{< relref "/docs/collection" >}}) for confirmed cases.
