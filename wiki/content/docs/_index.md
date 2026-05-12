---
title: "Overview"
weight: 1
bookToc: true
bookFlatSection: false
---

# Python Class Pollution

**Class pollution** is a vulnerability pattern in which an attacker traverses Python's
runtime object graph through dunder attributes &mdash; `__class__`, `__init__`,
`__globals__`, `sys.modules`, and so on &mdash; and overwrites attributes in unintended
classes, functions, or modules. The traversal is driven by a reflective
`getattr`/`setattr` (or `__getitem__`/`__setitem__`) loop whose path or keys come from
untrusted input.

It is the Python analogue of JavaScript prototype pollution[^silvanovich2021], but the
primitives are richer: because Python's object model is class-based with a flexible
reflection layer, pollution can reach classes, functions, modules, and even descriptor
slots &mdash; not just a single root prototype.

## A motivating example

```python
def update(user, data):
    for key in data:
        val = data[key]
        if isinstance(val, dict):
            update(getattr(user, key), val)
        else:
            setattr(user, key, val)
```

The function looks like a routine deep-merge of nested form data onto a model object. But
because `getattr` does not distinguish between developer-defined attributes and dunder
attributes, an attacker-controlled `data` can step through Python's object graph:

```json
{"__class__": {"__getattribute__": "1337"}}
```

After this call, `type(user).__getattribute__` is the string `"1337"`. Any attribute
access on any instance of the `User` class now raises `TypeError: 'str' object is not
callable` &mdash; a denial-of-service primitive. Extending the path through
`__init__.__globals__.sys.modules` reaches any imported module, which is where the
primitive becomes RCE ([gadgets/rce]({{< relref "gadgets/rce" >}})), stored XSS
([gadgets/xss]({{< relref "gadgets/xss" >}})), or authentication bypass
([gadgets/auth-bypass]({{< relref "gadgets/auth-bypass" >}})).

## Reading guide

Different audiences read this wiki differently. Start here:

- **Security researchers** looking to understand the vulnerability class:
  [Taxonomy]({{< relref "taxonomy" >}}) → [Targets]({{< relref "targets" >}}) →
  [Gadgets]({{< relref "gadgets" >}}).
- **Bug hunters and CTF players** looking for exploits to adapt:
  [Showcases]({{< relref "collection/showcases" >}}) are end-to-end PoCs;
  [Gadgets]({{< relref "gadgets" >}}) catalogues the building blocks.
- **Library maintainers** with a reflective update function in their codebase:
  [Defense]({{< relref "defense" >}}) is the shortest path, then
  [Pyrl]({{< relref "tool/pyrl" >}}) to scan your own code.
- **Readers of the paper** looking to map claims onto artifacts:
  [Tools]({{< relref "tool" >}}) documents Pyrl and Polluter;
  [Collection]({{< relref "collection" >}}) lists every confirmed finding.

## Key differences from JavaScript prototype pollution

| Aspect | JS prototype pollution | Python class pollution |
|--------|------------------------|------------------------|
| Object model | Prototype-based | Class-based + descriptor protocol |
| Pollution path | Uniform prototype chain (`__proto__`) | Multiple: attribute, item, variable |
| Canonical target | `Object.prototype` | Classes, modules, functions, closures |
| Namespace | Single (properties) | Two (attribute vs. item) |
| Resolution | Prototype chain lookup | MRO + descriptor protocol |
| Typical sink | `{}` merged from user input | `setattr` / `obj[k]=v` over a dotted path |

The second-to-last row is the important one for exploitation. Python's two namespaces
(`obj.attr` vs. `obj[key]`) give rise to three distinct "set" primitives (attr-only,
item-only, or dual), which combined with two "get" primitives (agnostic or constrained)
produce the six vulnerability types in the [taxonomy]({{< relref "taxonomy" >}}).

## Threat model

The vulnerable Python package processes input from one of three channels:

1. **Remote input** &mdash; HTTP body, query string, WebSocket message, RPC argument
   reaching a server-side reflective update. Example:
   [django-unicorn]({{< relref "collection/showcases/django-unicorn" >}}) (WebSocket).
2. **Local input** &mdash; command-line arguments, configuration files, LLM tool outputs
   reaching a CLI's reflective setter. Example:
   [Azure CLI]({{< relref "collection/showcases/azure-cli" >}}) (`--set`).
3. **Package-level input** &mdash; a public API of a library that accepts a dotted path
   and a value, reachable from another package that trusts its caller. Example:
   `pydash.set_`, `glom.assign`, `mo_dots.set_attr`.

In all three cases, the attacker controls the `name` (dotted path) and/or the `value` that
reach a reflective sink. The attacker does **not** need to control imports: any
`sys.modules` entry reached by any code path in the victim process is in scope.

## Scale of the problem

The analysis behind this research[^paper] scanned **671,475** real-world Python programs
with Pyrl and produced:

- **868** unique vulnerability reports,
- **47** confirmed zero-day exploitable vulnerabilities,
- **7** CVE identifiers assigned from this research (see
  [CVE index]({{< relref "reference/cve-index" >}})),
- Critical findings in Microsoft Azure CLI, Google Mesop, Taipy, django-unicorn, ComfyUI,
  Hugging Face Diffusers, and others.

## Related work

- **JavaScript prototype pollution** was first documented by Olivier Arteau in 2018 and
  systematized by Silvanovich and others[^silvanovich2021]. The object-model differences
  above mean the Python variant is not a mechanical port.
- **`pydash` gadget** (2022): [@abdulrah33m] published the first public demonstration of a
  dunder-walk gadget in Python via `pydash.set_`.
- **`deepdiff` advisory** ([CVE-2024-5254][deepdiff-cve], by [@chilaxan][chilaxan]): the
  first CVE issued for a Python reflective-merge sink.
- **Pyrl** (this work, IEEE S&P 2025[^paper]): the first automated detector, built on an
  operational taint-analysis extension of CodeQL's Python support.

## References

[^silvanovich2021]: Natalie Silvanovich. *The Risks of JavaScript Prototype Pollution*.
    Project Zero, 2021. <https://googleprojectzero.blogspot.com/>
[^paper]: Zhengyu Liu, Jiacheng Zhong, Jianjia Yu, Muxi Lyu, Zifeng Kang, Yinzhi Cao.
    *The First Large-Scale Systematic Study of Python Class Pollution Vulnerability*.
    IEEE S&P 2025. <https://jackfromeast.github.io/assets/Pyrl.pdf>

[deepdiff-cve]: https://nvd.nist.gov/vuln/detail/CVE-2024-5254
[chilaxan]: https://github.com/chilaxan
[@abdulrah33m]: https://github.com/abdulrah33m
