---
title: "Taxonomy"
weight: 2
bookCollapseSection: true
---

# Vulnerability Taxonomy

Class pollution consists of multiple **object access** steps followed by a final **object assignment** step. Each access or assignment step is a **pollution primitive**, and each primitive is built from one or more **atomic "get" or "set"** operations.

<figure class="diagram diagram-pair">
  <div class="diagram-row">
    <div>
      <img src="/wiki/img/procedure.png" alt="Class pollution as a chain of get-primitive steps that resolve a target object, followed by a single set-primitive step that writes a value." />
      <div class="sub-caption">(a) Pollution procedure</div>
    </div>
    <div>
      <img src="/wiki/img/primitives.png" alt="The two get primitives (Constrained-Get, Agnostic-Get) and three set primitives (Dual-Set, Attr-Set, Item-Set), each composed from atomic get/set operations." />
      <div class="sub-caption">(b) Get and set primitives</div>
    </div>
  </div>
  <figcaption>The get primitive runs N times to traverse from a starting object to the target, then a single set primitive performs the write. Each primitive is composed from one or more atomic get/set operations.</figcaption>
</figure>

Our taxonomy separates this structure into two layers:

1. **[Get & Set Atomics]({{< relref "atomics" >}})**: the individual reflective operations Python supports for reading and writing object state, e.g., `getattr(obj, name)`, `obj.__dict__[name]`, `dict[key]`, `setattr(obj, name, val)`.
2. **[Pollution Primitives]({{< relref "primitives" >}})**: the attacker's *capability* at each step, expressed in terms of which atomics they can use there. The "get" primitive is either *Agnostic* (the program allows free choice between attribute and item access) or *Constrained* (program logic fixes one atomic). The "set" primitive is *Dual*, *Attr-only*, or *Item-only*. The 2 × 3 combination yields the **six class pollution variants**.

## Why this classification?

Two programs that look superficially similar can have very different pollution capability. Consider these two instructive code snippets, both "reflective writes from user input":

**Program A:**

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

**Program B:**

```python
def deep_set(obj, dotted, value):
    parts = dotted.split(".")
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], value)
```

The two programs differ along two axes:

- **Get capability** (target object access path): Every Python object exposes two namespaces, the *attribute namespace* (read by `getattr`/`obj.x`) and the *item namespace* (read by `obj[k]`). They are not interchangeable: an attribute cannot be retrieved with item lookup, and a dict entry cannot be retrieved with attribute access. So whether the program lets the attacker mix the two at each step determines what they can reach. Program A can traverse mappings *and* attributes, so it can step from a dict into a class via `__class__`, or from a class into a module via `__init__.__globals__`. Program B is locked to attribute-only walks and cannot enter or escape a container.
- **Set capability** (final write target): Program A can finish with either `setattr` or `obj[k] = v`, while Program B only with `setattr`. The choice of final write determines what kinds of targets are reachable: an attribute-write lands on classes, modules, and functions, while an item-write lands on container internals such as `__globals__` and `os.environ`.

Classifying by primitive (what the attacker can choose at each step) captures these differences precisely. Of the six variants, only *Agnostic-Get × Dual-Set* was shown before and the other five were introduced in our IEEE S&P 2026 paper.

## Capability matrix

The two columns under *target object access path* describe what the attacker can use to reach the target during traversal; the two columns under *target object types* describe what kinds of objects the final write can land on. A "Yes" means the variant supports that path or target; a "No" means the program shape forbids it.

<table class="capability-matrix">
  <thead>
    <tr>
      <th rowspan="2">Variant Types</th>
      <th colspan="2">Target Object Access Path</th>
      <th colspan="2">Target Object Types</th>
    </tr>
    <tr>
      <th>GetAttr only</th>
      <th>GetItem &amp; GetAttr</th>
      <th>Containers<br>(dict, list)</th>
      <th>General objects</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Agnostic-Get × Dual-Set</td><td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td></tr>
    <tr><td>Agnostic-Get × Attr-Set</td><td>Yes</td><td>Yes</td><td>No</td><td>Yes</td></tr>
    <tr><td>Agnostic-Get × Item-Set</td><td>Yes</td><td>Yes</td><td>Yes</td><td>No</td></tr>
    <tr><td>Constrained-Get × Dual-Set</td><td>Yes</td><td>No</td><td>Yes</td><td>Yes</td></tr>
    <tr><td>Constrained-Get × Attr-Set</td><td>Yes</td><td>No</td><td>No</td><td>Yes</td></tr>
    <tr><td>Constrained-Get × Item-Set</td><td>Yes</td><td>No</td><td>Yes</td><td>No</td></tr>
  </tbody>
</table>

Reading the table:

- The first two columns track the **get** capability. "GetAttr only" is always available because attribute access works on every Python object. The "GetItem & GetAttr" column is what separates *Agnostic-Get* (the program lets the attacker reach through containers) from *Constrained-Get* (it does not).
- The last two columns track the **set** capability. *Attr-Set* can land writes on classes, modules, functions, and other general objects, but not on container internals. *Item-Set* is the inverse: it can only modify mapping/sequence entries. *Dual-Set* combines both.

The variant that "Yes everything" is *Agnostic-Get × Dual-Set* &mdash; the only variant prior work covered. The other five each carve off a strict subset of the capability surface, which is why they need different detection logic and different gadgets to exploit.
