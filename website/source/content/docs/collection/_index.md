---
title: "Showcases & CVEs"
weight: 6
bookCollapseSection: true
---

# Showcases and CVEs

A curated dataset of confirmed vulnerable Python packages with proof-of-concept exploits. This page combines the **assigned CVEs** and the **end-to-end exploitation walkthroughs**. The full list of 78 confirmed cases lives on the [Catalog]({{< relref "catalog" >}}) page.

## Assigned CVEs

The CVE table lists every advisory issued for class pollution, both from this work and from prior research.

<div class="atomics-table">

| CVE | Application | Consequences | Found by | Status |
|---|---|---|---|---|
| [CVE-2025-24370](https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) | django-unicorn | DoS, XSS, Auth Bypass, RCE | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Fixed |
| [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049) | Azure CLI | Token Leakage, OS Command Injection | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Fixed |
| [CVE-2025-30374](https://github.com/Avaiga/taipy/security/advisories) | Taipy | DoS, XSS, RCE, Token Leakage | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Fixed |
| [CVE-2025-30358](https://github.com/google/mesop/security/advisories) | Google Mesop | DoS, Remote Execution | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Fixed |
| [CVE-2025-6107](https://github.com/comfyanonymous/ComfyUI/security/advisories) | ComfyUI | DoS | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Fixed |
| [CVE-2025-5150](https://github.com/docarray/docarray/security/advisories) | docarray | DoS | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [CVE-2025-3982](https://github.com/nortikin/sverchok/security/advisories) | sverchok | Token Leakage | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [CVE-2024-5452](https://nvd.nist.gov/vuln/detail/CVE-2024-5452) | deepdiff (prior work) | DoS | [diogotcorreia](https://github.com/qlustered/deepdiff/security/advisories/GHSA-mw26-5g2v-hqw3) | Fixed |

</div>

## End-to-end exploitation walkthroughs

Each page below walks through the full exploitation chain: the vulnerable function, the pollution payload, the trigger, and the resulting consequence.

- [Azure CLI]({{< relref "showcases/azure-cli" >}}) - Token Leakage and OS Command Injection through `set_properties`.
- [ComfyUI]({{< relref "showcases/comfyui" >}}) - DoS through reflective attribute setting.
- [django-unicorn]({{< relref "showcases/django-unicorn" >}}) - DoS, XSS, Auth Bypass, and RCE through a single WebSocket message.
- [Mesop]({{< relref "showcases/mesop" >}}) - DoS and Remote Execution through reflective dataclass update.
- [Taipy]({{< relref "showcases/taipy" >}}) - DoS, XSS, RCE, and Token Leakage through `_attrsetter`.
