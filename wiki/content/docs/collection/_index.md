---
title: "Collection"
weight: 6
bookFlatSection: true
---

# Class Pollution Vulnerability Collection

A curated database of **77+ confirmed vulnerable Python packages** with proof-of-concept exploits. All vulnerabilities were discovered by Pyrl and verified through manual analysis.

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total vulnerable packages | 77+ |
| CVEs assigned | 7 |
| Fixed by developers | 5 |
| Remote-triggerable | 11 |
| Local-triggerable | 15 |
| Package-level | 21 |

## Vulnerabilities with CVEs

| Application | Stars | CVE | Consequence | Status |
|-------------|-------|-----|-------------|--------|
| [django-unicorn](https://github.com/adamghill/django-unicorn) | 2.4K | [CVE-2025-24370](https://github.com/adamghill/django-unicorn/security/advisories/GHSA-g9wf-5777-gq43) | DoS, XSS, RCE, Auth Bypass | Fixed |
| [Azure CLI](https://github.com/Azure/azure-cli) | 4.1K | [CVE-2025-24049](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2025-24049) | Token Leakage, OS Command Injection | Fixed |
| [Taipy](https://github.com/Avaiga/taipy) | 19.2K | [CVE-2025-30374](https://github.com/Avaiga/taipy/security/advisories/) | DoS, XSS, RCE, Token Leakage | Fixed |
| [Mesop](https://github.com/google/mesop) | 5.7K | [CVE-2025-30358](https://github.com/google/mesop/security/advisories/) | DoS, Remote Execution | Fixed |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | 78.5K | [CVE-2025-6107](https://github.com/comfyanonymous/ComfyUI/security/advisories/) | DoS | Fixed |
| [docarray](https://github.com/docarray/docarray) | 3.1K | [CVE-2025-5150](https://github.com/docarray/docarray/security/advisories/) | DoS | Reported |
| [sverchok](https://github.com/nortikin/sverchok) | 2.3K | [CVE-2025-3982](https://github.com/nortikin/sverchok/security/advisories/) | Token Leakage | Reported |

## Remote-Triggerable Vulnerabilities (Sorted by Stars)

| Application | Stars | Version | Get Primitive | Set Primitive | Consequence |
|-------------|-------|---------|---------------|---------------|-------------|
| ComfyUI | 78.5K | v0.3.39 | Constrained | Attr | DoS |
| RAGFlow | 52.8K | v0.19.0 | Constrained | Attr | DoS |
| Taipy | 19.2K | v4.0.3 | Constrained | Attr | DoS, XSS, RCE, TL |
| sd-webui-controlnet | 17.6K | v1.1.436 | Constrained | Attr | DoS |
| stable-diffusion-webui-forge | 10.9K | latest | Constrained | Attr | DoS |
| Mesop | 5.7K | v0.14.0 | Constrained | Dual | DoS, RE |
| django-unicorn | 2.4K | v0.62.0 | Agnostic | Dual | DoS, XSS, RCE, AB |
| docarray | 3.1K | v0.40.1 | Constrained | Attr | DoS |
| fastapi-amis-admin | 1.3K | v0.7.3 | Constrained | Dual | DoS |

## Local-Triggerable Vulnerabilities

| Application | Stars | Version | Get Primitive | Set Primitive | Consequence |
|-------------|-------|---------|---------------|---------------|-------------|
| Azure CLI | 4.1K | v2.68.0 | Agnostic | Dual | TL, OSCI |
| sverchok | 2.3K | v1.3.0 | Agnostic | Dual | TL |

## PyPI Package Vulnerabilities (Sorted by Weekly Downloads)

| Package | Downloads | Version | Get Primitive | Set Primitive | Status |
|---------|-----------|---------|---------------|---------------|--------|
| accelerate | 2.7M | v1.7.0 | Constrained | Attr | Reported |
| spaCy | 2.6M | v3.8.7 | Constrained | Attr | Reported |
| magicattr | 1.5M | v0.1.6 | Agnostic | Dual | Reported |
| glom | 1.4M | v24.11.0 | Agnostic | Dual | Acknowledged |
| google-generativeai | 1.3M | v0.8.5 | Constrained | Attr | Reported |
| diffusers | 86.2K | v0.33.1 | Constrained | Attr | Reported |
| tf-keras | 59.5K | v2.19.0 | Agnostic | Dual | Reported |
| mo-dots | 55.2K | v10.678.x | Agnostic | Dual | Reported |
| pykka | 15.7K | v4.2.0 | Constrained | Attr | Reported |

## Full Collection

The complete collection with proof-of-concept code is available in the [`cp-collection/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection) directory.

Each entry includes:
- `README.md` — Vulnerability metadata and code snippet
- `poc/` — Proof-of-concept exploit code
- `poc/requirements.txt` — Dependencies
- `poc/run.sh` — Script to reproduce

**Legend**: TL = Token Leakage, OSCI = OS Command Injection, RE = Remote Execution, AB = Authentication Bypass
