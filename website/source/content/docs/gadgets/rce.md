---
title: "RCE Gadgets"
weight: 1
---

# RCE Gadgets

RCE gadgets cause the victim process to execute attacker-provided code. The attacker writes a string at a runtime location whose value the application's own code later passes to `subprocess`, an import hook, or a shell.

## Standard library

| Library | Trigger | Polluted property |
|---|---|---|
| `webbrowser` | `webbrowser.open` | `os.environ['BROWSER']` |
| `antigravity` | `import antigravity` (calls `webbrowser.open` on import) | `os.environ['BROWSER']` |
| `subprocess` | `subprocess.run(..., shell=True)` | `os.environ['COMSPEC']` |

## Third-party packages

| Library | Trigger | Polluted property |
|---|---|---|
| `taipy.gui` | - | `Gui.__SELF_VAR` |

## Real-world cases

| Application | Polluted property | Mechanism | CVE |
|---|---|---|---|
| [django-unicorn]({{< relref "/docs/collection/showcases/django-unicorn" >}}) | `os.environ['BROWSER']` plus `location_cache._Cache__data.todo` | WebSocket message via `set_property_value` | [CVE-2025-24370](https://github.com/django-commons/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) |
| [Azure CLI]({{< relref "/docs/collection/showcases/azure-cli" >}}) | `os.environ['COMSPEC']` | `--set` flag via `set_properties` | [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049) |
| [Taipy]({{< relref "/docs/collection/showcases/taipy" >}}) | `Gui.__SELF_VAR` | HTTP/SocketIO via `_attrsetter` | [CVE-2025-30374](https://nvd.nist.gov/vuln/detail/CVE-2025-30374) |
