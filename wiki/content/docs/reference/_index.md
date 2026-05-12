---
title: "Reference"
weight: 7
bookFlatSection: true
---

# Reference

## Attack matrix

Rows: the six vulnerability types. Columns: primitives, representative real case, known
gadgets, and recommended defense.

| Type | Get | Set | Real case | Gadgets | Defense |
|------|-----|-----|-----------|---------|---------|
| Agnostic-Get × Dual-Set | Agnostic | Dual | django-unicorn (CVE-2025-24370) | RCE, XSS, DoS, Auth Bypass | TODO |
| Constrained-Get × Dual-Set | Constrained | Dual | Azure CLI (CVE-2025-24049) | RCE, DoS | TODO |
| Agnostic-Get × Attr-Set | Agnostic | Attr | TODO | TODO | TODO |
| Constrained-Get × Attr-Set | Constrained | Attr | ComfyUI (CVE-2025-6107) | DoS | TODO |
| Agnostic-Get × Item-Set | Agnostic | Item | TODO | TODO | TODO |
| Constrained-Get × Item-Set | Constrained | Item | TODO | TODO | TODO |

## Pages in this section

- [CVE Index]({{< relref "cve-index" >}}) &mdash; all CVEs from this research, mapped to
  wiki pages.
