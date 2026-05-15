---
title: "Pollution Targets"
weight: 3
bookCollapseSection: true
---

# Pollution Targets

A *pollution target* is a runtime object that is reachable via attribute or item access and whose value affects program behavior. The [pollution primitives]({{< relref "/docs/taxonomy/primitives" >}}) page describes how an attacker resolves and modifies such an object. This page describes which objects are worth resolving in the first place.

A polluted target is consumed by the program in two ways.

- **Direct access.** The program later reads the same attribute the attacker just wrote, e.g. the attacker sets `a.b` and the program later reads `a.b`.
- **Indirect access.** Python's data model and reflection layer route the read through a different path. For example, modifying a class variable `cls.v` changes the default value of `self.v` for every instance of that class, and modifying a function's `__kwdefaults__` changes the default value of every keyword-only parameter on subsequent calls.

Direct access is the boring case. The interesting cases are indirect, and the rest of this section catalogs them.

## Categories

We surveyed Python's data model and identified four categories of pollution targets. Each category has a single access mechanism and a loading context that explains how the polluted value reaches a sensitive use site.

| Target | Access mechanism | Description |
|---|---|---|
| [Classes]({{< relref "classes" >}}) | Attribute lookup | `C.v`, where class `C` is accessible. The attacker controls `cls.v` and `self.v` whenever the attribute is not defined on the instance. |
| [Modules]({{< relref "modules" >}}) | Global variable reference | `mod.v`, where module `mod` is accessible. The attacker controls a global variable used across modules. |
| [Functions]({{< relref "functions" >}}) (globals) | Global variable reference via module lookup | `f.__globals__["v"]`, where function `f` is accessible. The attacker controls a global variable in `f`'s defining module. |
| [Functions]({{< relref "functions" >}}) (kwdefaults) | Local variable reference | `f.__kwdefaults__["p"]`, where function `f` is accessible. The attacker controls the default value of keyword-only parameter `p`. |
| [Functions]({{< relref "functions" >}}) (closure) | Local variable reference | `g.__closure__[i].cell_contents`, where function `g` is accessible as a closure. The attacker controls the captured variable. |

The closure foothold (`g.__closure__[i].cell_contents`) is novel to this work. Prior literature on Python class pollution covered classes, module globals, function `__globals__`, and `__kwdefaults__`, but not closure cells.

## Why these are the high-value targets

Pollution capability is determined by the [primitive]({{< relref "/docs/taxonomy/primitives" >}}). Pollution *impact* is determined by the target. The categories above share two properties that make them especially dangerous.

First, they are *reachable from any object*. Every Python value exposes a chain such as `obj.__class__.__init__.__globals__["sys"].modules`, which steps from an instance up to its class, into a defining module, and from there into any imported module. Once `sys.modules` is in scope the attacker can reach `os`, `subprocess`, `django.conf`, and any other loaded library.

Second, modifications to them propagate beyond the polluted object itself. Polluting a class attribute changes every instance that does not shadow it. Polluting a module global changes every importer. Polluting a function's `__kwdefaults__` changes every subsequent call without an explicit keyword argument. This propagation is what turns a single reflective write into a remote impact.

The subpages below cover each category in detail, including the access mechanism, a loading-context snippet, and the typical exploitation shape.
