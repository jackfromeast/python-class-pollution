---
title: "Showcase Walkthroughs"
weight: 2
bookCollapseSection: true
---

# End-to-end Showcase Walkthroughs

Each page below walks through the full exploitation chain for a confirmed class pollution vulnerability: the vulnerable function, the pollution payload, the trigger, and the resulting consequence.

For the assigned CVEs and the index of every walkthrough, see [Showcases & CVEs]({{< relref "/docs/collection" >}}). For the full 76-package list, see the [Catalog]({{< relref "/docs/collection/catalog" >}}).

- [Azure CLI]({{< relref "azure-cli" >}}) - Token Leakage and OS Command Injection through `set_properties`.
- [ComfyUI]({{< relref "comfyui" >}}) - DoS through reflective attribute setting.
- [django-unicorn]({{< relref "django-unicorn" >}}) - DoS, XSS, Auth Bypass, and RCE through a single WebSocket message.
- [Mesop]({{< relref "mesop" >}}) - DoS and Remote Execution through reflective dataclass update.
- [Taipy]({{< relref "taipy" >}}) - DoS, XSS, RCE, and Token Leakage through `_attrsetter`.
