---
title: "Consequences"
weight: 3
---

# Consequences

The consequence of class pollution is that an adversary corrupts program behaviors by changing either data or control flow via exploiting class pollution, leading to other well-known vulnerabilities.

## Sink Value Corruption

The polluted value flows directly into a traditional vulnerability sink, such as `os.system`, `file.write`, and `requests.get`.

**Resulting impacts:**
- Remote Code Execution (RCE)
- Arbitrary File Writing
- Server-Side Request Forgery (SSRF)

```python
# Example: Polluting os.environ to achieve RCE
# Payload: __class__.__init__.__globals__.sys.modules.os.environ.BROWSER = "/bin/sh -c 'touch /tmp/pwned'"

import antigravity  # Triggers webbrowser which reads BROWSER env var
# → Shell command executed
```

## Call Target Corruption

An attacker can overwrite a defined callable with a non-callable primitive such as a string. When the callable is invoked, the program raises an exception that, if unhandled, crashes the application.

**Resulting impact:** Denial of Service (DoS)

```python
# Example: Overwriting __getattribute__
# Payload: {"__class__": {"__getattribute__": "1337"}}

# After pollution:
user.name  # → TypeError: '1337' is not callable
# Any attribute access on ANY User instance crashes
```

{{< hint danger >}}
This is particularly severe because `__getattribute__` is invoked for **every** attribute access. Polluting it on a class affects all instances and is irrecoverable without restarting the application.
{{< /hint >}}

## Corruption of Security Conditions

The attacker can change the outcome of a security-sensitive condition, enabling access to functionality that would otherwise be unreachable.

**Resulting impacts:**
- Authentication Bypass
- Authorization Bypass
- Input Validation Bypass

```python
# Example: Overwriting Django's SECRET_KEY
# Payload: __init__.__globals__.sys.modules.django.template.backends.django.settings.SECRET_KEY = "13371337"

# After pollution:
# Attacker knows the SECRET_KEY → can forge session cookies
# → Authentication bypass on all users
```

## Consequence Matrix by Vulnerability Type

| Consequence | Agnostic-Get | Constrained-Get |
|-------------|-------------|-----------------|
| **RCE** | Via env vars, module cache | Via env vars, module cache |
| **DoS** | Via __getattribute__ overwrite | Via __getattribute__ overwrite |
| **XSS** | Via entity map overwrite | Via entity map overwrite |
| **Token Leakage** | Via SSRF sinks | Via SSRF sinks |
| **Auth Bypass** | Via SECRET_KEY pollution | Via SECRET_KEY pollution |

## Real-World Impact Distribution

From our analysis of 47 confirmed zero-day vulnerabilities:

| Consequence | Count | Example Target |
|-------------|-------|----------------|
| DoS | Most common | ComfyUI, RAGFlow, sd-webui-controlnet |
| RCE | High impact | Azure CLI, django-unicorn |
| XSS (Stored) | Web apps | django-unicorn, Taipy |
| Token Leakage | Cloud apps | Azure CLI, Taipy |
| Auth Bypass | Web frameworks | django-unicorn |
