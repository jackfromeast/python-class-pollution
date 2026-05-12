---
title: "ComfyUI"
weight: 5
---

# ComfyUI (CVE-2025-6107)

**ComfyUI** is a node-based UI for Stable Diffusion (78.5K stars) that accepts workflow
definitions as JSON from the browser. A reflective attribute setter processes
user-provided node configuration without path validation.

| Field | Value |
|-------|-------|
| Repository | [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |
| Version | v0.3.39 |
| CVE | [CVE-2025-6107](https://github.com/comfyanonymous/ComfyUI/security/advisories) |
| Type | Constrained-Get × Attr-Set |
| Input | Remote (HTTP) |
| Status | Fixed |

## Vulnerability

TODO: identify the exact sink function and include annotated code.

## Exploitation

### 1. Denial of Service

TODO: key path and payload. Effect on the ComfyUI server.

## Detection by Pyrl

TODO: taint flow summary.

## Disclosure timeline

TODO: dates for report, fix, CVE assignment.

## Proof of concept

[`cp-collection/ComfyUI/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/ComfyUI/poc)

## References

1. TODO: GHSA advisory link.
