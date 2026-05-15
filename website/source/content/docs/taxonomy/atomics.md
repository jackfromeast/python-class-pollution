---
title: "Get & Set Atomics"
weight: 1
---

# Get & Set Atomics

This page catalogs the reflective operations Python supports for reading and writing object state. These are the building blocks that the [pollution primitives]({{< relref "primitives" >}}) page combines into attacker capabilities.

## Atomic "get" operations

Python has two kinds of atomic "get". The first is **attribute access** (e.g., `getattr(obj, name)`), which retrieves values from an object's attribute namespace and is supported by every Python object. The second is **item access** (e.g., `dict[key]`), which retrieves values from a container's item namespace and is only supported by mappings and sequences.

The two namespaces are not interchangeable: an attribute cannot be retrieved with item lookup and vice versa. A third group, **hybrid** operations like `eval`/`exec`, can perform either depending on the evaluated expression.

We surveyed the Python Standard Library and identified 20 syntactic variants. Prevalence numbers come from CodeQL on the 50K most-downloaded PyPI packages.

<div class="atomics-table">

| Code | Type | Apply | Origin | Capability | # Inst. | # Pack. |
|---|---|---|---|:---:|---:|---:|
| `getattr(obj, name)` | Attr | O/M/S | Builtins | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 719.1K | 21.7K |
| `obj.__dict__[name]` | Attr | O/M/S | Builtins | <span class="cap half"></span> <span class="cap half"></span> <span class="cap full"></span> | 15.3K | 3.3K |
| `obj.__getattribute__(name)` | Attr | O/M/S | Builtins | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 13.1K | 1.7K |
| `vars(obj)[name]` | Attr | O/M/S | Builtins | <span class="cap half"></span> <span class="cap half"></span> <span class="cap full"></span> | 9.3K | 1.0K |
| `dict(inspect.getmembers(obj))[name]` | Attr | O/M/S | Inspect | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 4.9K | 1.9K |
| `object.__getattribute__(obj, name)` | Attr | O/M/S | Builtins | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 4.3K | 843 |
| `operator.attrgetter(name)(obj)` | Attr | O/M/S | Operator | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 543 | 194 |
| `inspect.getattr_static(obj, name)` | Attr | O/M/S | Inspect | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 398 | 121 |
| `getattr(obj, dir(obj)[index])` | Attr | O/M/S | Builtins | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 93 | 23 |
| `dict(inspect.getmembers_static(obj))[name]` | Attr | O/M/S | Inspect | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 11 | 8 |
| `dict[key]` | Item | M/S | Builtins | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 50.7M | 44.1K |
| `dict.get(key)` | Item | M | Builtins | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 8.6M | 33.1K |
| `dict.pop(key)` | Item | M/S | Builtins | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 1.7M | 17.9K |
| `dict.setdefault(key)` | Item | M | Builtins | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 111.1K | 8.0K |
| `dict.__getitem__(key)` | Item | M/S | Builtins | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 63.3K | 3.0K |
| `operator.getitem(dict, key)` | Item | M/S | Operator | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 271 | 79 |
| `operator.itemgetter(key)(dict)` | Item | M/S | Operator | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 153 | 60 |
| `operator.__getitem__(dict, key)` | Item | M/S | Operator | <span class="cap none"></span> <span class="cap none"></span> <span class="cap full"></span> | 3 | 1 |
| `eval(f"EXPR", {"o": obj})` | Attr/Item | O/M/S | Builtins | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 331 | 135 |
| `exec(f"EXPR", {"o": obj})` | Attr/Item | O/M/S | Builtins | <span class="cap full"></span> <span class="cap full"></span> <span class="cap full"></span> | 172 | 112 |

</div>

<p class="table-legend"><strong>Legend.</strong> <em>Apply</em>: O = Object, M = Mapping, S = Sequence. <em>Capability</em> shows what kinds of names the operation can retrieve, as a triple <strong>dunder / method / other</strong>: <span class="cap full"></span> fully supported, <span class="cap half"></span> conditionally supported (<code>obj.__dict__[name]</code> and <code>vars(obj)[name]</code> only apply when the object has a writable <code>__dict__</code>), <span class="cap none"></span> not supported. <em>EXPR</em> in the <code>eval</code>/<code>exec</code> rows means any of the other operations above with only the key name attacker-controlled.</p>

## Atomic "set" operations

Python has two kinds of atomic "set": **attribute assignment** (e.g., `setattr(obj, name, val)`) and **item assignment** (e.g., `dict[key] = val`). Unlike "get", the two atomic "sets" are interchangeable when the target object has a writable `__dict__`: `obj.x = v` is semantically equivalent to `obj.__dict__["x"] = v`.

We surveyed the Python Standard Library and identified 12 syntactic variants. Prevalence numbers come from CodeQL on the 50K most-downloaded PyPI packages.

<div class="atomics-table">

| Code | Type | Apply | Origin | # Inst. | # Pack. |
|---|---|---|---|---:|---:|
| `obj.__dict__[name] = val` | Attr | O/M/S | Builtins | 437.8K | 3.1K |
| `setattr(obj, name, val)` | Attr | O/M/S | Builtins | 214.3K | 12.0K |
| `object.__setattr__(obj, name, val)` | Attr | O/M/S | Builtins | 11.4K | 1.6K |
| `obj.__setattr__(name, val)` | Attr | O/M/S | Builtins | 10.4K | 2.3K |
| `dict[key] = val` | Item | M/S | Builtins | 7.7M | 36.8K |
| `dict.update(key=val)` | Item | M | Builtins | 687.8K | 22.7K |
| `dict.setdefault(key, val)` | Item | M | Builtins | 111.1K | 8.0K |
| `dict.__setitem__(key, val)` | Item | M/S | Builtins | 7.7K | 2.2K |
| `operator.setitem(dict, key, val)` | Item | M/S | Operator | 27 | 12 |
| `operator.__setitem__(dict, key, val)` | Item | M/S | Operator | 0 | 0 |
| `exec(f"EXPR", {"o": obj})` | Attr/Item | O/M/S | Builtins | 90 | 47 |
| `eval(f"EXPR", {"o": obj})` | Attr/Item | O/M/S | Builtins | 16 | 7 |

</div>

<p class="table-legend"><strong>Legend.</strong> <em>Apply</em>: O = Object, M = Mapping, S = Sequence. The <code>exec</code>/<code>eval</code> rows count occurrences where only the key name and value are attacker-controlled.</p>

The next page, [Pollution Primitives]({{< relref "primitives" >}}), groups these atomics by what an attacker can choose at each step in a vulnerable program. That is what determines the variant.
