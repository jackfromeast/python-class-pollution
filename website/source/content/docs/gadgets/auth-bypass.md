---
title: "Auth Bypass Gadgets"
weight: 4
---

# Auth Bypass Gadgets

Auth bypass gadgets let the attacker forge credentials, escalate privileges, or skip an access check. The most powerful variants overwrite a signing key, so the attacker can forge a session for any user without ever guessing a password.

## Third-party packages

| Library | Trigger | Polluted property |
|---|---|---|
| `django.core.signing` | [`Signer.sign` / `Signer.unsign`](https://github.com/django/django/blob/main/django/core/signing.py) - covers session cookies, CSRF tokens, password-reset tokens | `django.conf.settings.SECRET_KEY` |

## Real-world cases

| Application | Polluted property | Mechanism | CVE |
|---|---|---|---|
| [django-unicorn]({{< relref "/docs/collection/showcases/django-unicorn" >}}) | `django.conf.settings.SECRET_KEY` | WebSocket message via `set_property_value` | [CVE-2025-24370](https://github.com/django-commons/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) |
