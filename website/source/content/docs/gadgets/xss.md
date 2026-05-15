---
title: "XSS Gadgets"
weight: 2
---

# XSS Gadgets

XSS gadgets disable the application's HTML-escaping pipeline so that attacker-supplied input later rendered into a page is interpreted as markup instead of text.

## Third-party packages

| Library | Trigger | Polluted property |
|---|---|---|
| `bs4` | [`EntitySubstitution.substitute_xml`](https://github.com/wention/BeautifulSoup4) | `EntitySubstitution.CHARACTER_TO_XML_ENTITY['<']` |
| `taipy.gui` | [`type(content).__name__` rendered as HTML](https://github.com/Avaiga/taipy/blob/main/taipy/gui/gui.py) | `<class>.__name__` |

## Real-world cases

| Application | Polluted property | Mechanism | CVE |
|---|---|---|---|
| [django-unicorn]({{< relref "/docs/collection/showcases/django-unicorn" >}}) | `EntitySubstitution.CHARACTER_TO_XML_ENTITY['<']` | WebSocket via `set_property_value` | [CVE-2025-24370](https://github.com/django-commons/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) |
| [Taipy]({{< relref "/docs/collection/showcases/taipy" >}}) | `<class>.__name__` | HTTP/SocketIO via `_attrsetter` | [CVE-2025-30374](https://nvd.nist.gov/vuln/detail/CVE-2025-30374) |
