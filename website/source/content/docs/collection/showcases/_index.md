---
title: "Showcases & CVEs"
weight: 2
bookCollapseSection: true
---

# Showcases and CVEs

This section combines the assigned CVEs and the end-to-end exploitation write-ups. The CVE table lists every advisory that has been issued for class pollution, both from this work and from prior research. The showcase pages walk through full exploitation chains, from the vulnerable code to a working PoC, for the cases where we landed multiple consequences from a single primitive.

## Assigned CVEs

| CVE | Application | Consequences | Status |
|---|---|---|---|
| [CVE-2025-24370](https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) | django-unicorn | DoS, XSS, Auth Bypass, RCE | Fixed |
| [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049) | Azure CLI | Token Leakage, OS Command Injection | Fixed |
| [CVE-2025-30374](https://github.com/Avaiga/taipy/security/advisories) | Taipy | DoS, XSS, RCE, Token Leakage | Fixed |
| [CVE-2025-30358](https://github.com/google/mesop/security/advisories) | Google Mesop | DoS, Remote Execution | Fixed |
| [CVE-2025-6107](https://github.com/comfyanonymous/ComfyUI/security/advisories) | ComfyUI | DoS | Fixed |
| [CVE-2025-5150](https://github.com/docarray/docarray/security/advisories) | docarray | DoS | Reported |
| [CVE-2025-3982](https://github.com/nortikin/sverchok/security/advisories) | sverchok | Token Leakage | Reported |
| [CVE-2024-5452](https://nvd.nist.gov/vuln/detail/CVE-2024-5452) | deepdiff (prior work) | DoS | Fixed |

## End-to-end exploitation walkthroughs

Each page below walks through the full exploitation chain: the vulnerable function, the pollution payload, the trigger, and the resulting consequence.

- [Azure CLI]({{< relref "azure-cli" >}}) - Token Leakage and OS Command Injection through `set_properties`.
- [django-unicorn]({{< relref "django-unicorn" >}}) - DoS, XSS, Auth Bypass, and RCE through a single WebSocket message.
- [Mesop]({{< relref "mesop" >}}) - DoS and Remote Execution through reflective dataclass update.
- [Taipy]({{< relref "taipy" >}}) - DoS, XSS, RCE, and Token Leakage through `_attrsetter`.
