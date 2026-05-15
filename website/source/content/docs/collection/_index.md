---
title: "Collection"
weight: 6
bookCollapseSection: true
---

# Class Pollution Vulnerability Collection

A curated dataset of confirmed vulnerable Python packages with proof-of-concept exploits. Assigned CVEs and end-to-end walkthroughs are on the [Showcases & CVEs]({{< relref "showcases" >}}) page. This page lists every confirmed case across the corpus.

**Summary**: 76 confirmed vulnerable packages, 5 with CVEs assigned, 3 fixed by developers, 9 remote-triggerable, 3 local-triggerable, 64 package-level.

## Vulnerable packages

| Application | Reach | Stars | Version | Get | Set | Found by | Status |
|---|---|---:|---|---|---|---|---|
| [ComfyUI](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/ComfyUI) | Remote | 112.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [ragflow](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/ragflow) | Remote | 80.3K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [taipy](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/taipy) | Remote | 19.2K | v4.0.3 | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Fixed |
| [sd-webui-controlnet](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/sd-webui-controlnet) | Remote | 17.9K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [stable-diffusion-webui-forge](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/stable-diffusion-webui-forge) | Remote | 12.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [mesop](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/mesop) | Remote | 6.5K | v0.13.0 | Constrained | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [docarray](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/docarray) | Remote | 3.1K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [django-unicorn](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/django-unicorn) | Remote | 2.6K | 0.61.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [fastapi-amis-admin](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/fastapi-amis-admin) | Remote | 1.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [azure-cli](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/azure-cli) | Local | 4.5K | v2.68.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Fixed |
| [azure-cli-core](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/azure-cli-core) | Local | 4.5K | latest | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [sverchok](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/sverchok) | Local | 2.5K | latest | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Assigned |
| [open-interpreter](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/open-interpreter) | Package | 63.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [diffusers](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/diffusers) | Package | 33.6K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [spaCy](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/spaCy) | Package | 33.6K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [fairseq](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/fairseq) | Package | 32.2K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [pytorch-lightning](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/pytorch-lightning) | Package | 31.1K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [minGPT](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/minGPT) | Package | 24.3K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [zipline](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/zipline) | Package | 19.8K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [hummingbot](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/hummingbot) | Package | 18.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [nni](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/nni) | Package | 14.4K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [stylegan2](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/stylegan2) | Package | 11.2K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Todo |
| [accelerate](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/accelerate) | Package | 9.7K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [pyinstrument](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/pyinstrument) | Package | 7.7K | N/A | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [mmpose](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/mmpose) | Package | 7.6K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [issaclab](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/issaclab) | Package | 7.1K | v1.4.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [clearml](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/clearml) | Package | 6.7K | v1.16.5 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [deepchem](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/deepchem) | Package | 6.7K | latest | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Todo |
| [ibis](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/ibis) | Package | 6.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [wfuzz](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/wfuzz) | Package | 6.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [tensorpack](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/tensorpack) | Package | 6.3K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [panel](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/panel) | Package | 5.7K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [Red-DiscordBot](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/Red-DiscordBot) | Package | 5.5K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [optimum](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/optimum) | Package | 3.4K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [deepdoctection](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/deepdoctection) | Package | 3.2K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [virt-manager](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/virt-manager) | Package | 3.1K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [robusta](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/robusta) | Package | 3.0K | 0.20.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [legged_gym](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/legged_gym) | Package | 2.9K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [neural-compressor](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/neural-compressor) | Package | 2.6K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [deepdiff](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/deepdiff) | Package | 2.5K | v8.0.0 | Agnostic | Dual | [diogotcorreia](https://github.com/qlustered/deepdiff/security/advisories/GHSA-mw26-5g2v-hqw3) | Accepted |
| [generative-ai-python](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/generative-ai-python) | Package | 2.3K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [wrapt](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/wrapt) | Package | 2.3K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [fixinventory](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/fixinventory) | Package | 2.1K | 4.2.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [glom](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/glom) | Package | 2.1K | v24.11.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [evennia](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/evennia) | Package | 2.0K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [EasyCV](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/EasyCV) | Package | 1.9K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [pydash](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/pydash) | Package | 1.4K | v5.1.2 | Agnostic | Dual | [abdulrah33m](https://blog.abdulrah33m.com/prototype-pollution-in-python/) | Fixed |
| [nut](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/nut) | Package | 1.3K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [pykka](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/pykka) | Package | 1.3K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [EPro-PnP](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/EPro-PnP) | Package | 1.2K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [otx](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/otx) | Package | 1.2K | v2.2.2 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [xorbits](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/xorbits) | Package | 1.2K | latest | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [CRNN_Tensorflow](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/CRNN_Tensorflow) | Package | 1.0K | latest | Agnostic | Item | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [JSPyBridge](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/JSPyBridge) | Package | 850 | 1.2.1 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [meta_dataset](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/meta_dataset) | Package | 802 | N/A | Constrained | Attr | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [riven](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/riven) | Package | 789 | v0.20.1 | Constrained | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [torchlens](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/torchlens) | Package | 641 | 0.1.26 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [agentlab](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/agentlab) | Package | 576 | v0.3.2 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [tournesol](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/tournesol) | Package | 375 | N/A | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [pokitoki](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/pokitoki) | Package | 339 | v210 | Constrained | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [nebari](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/nebari) | Package | 326 | 2024.12.1 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [edsnlp](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/edsnlp) | Package | 165 | v0.15.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [netchecks](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/netchecks) | Package | 164 | v0.5.4 | Constrained | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [uavSim](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/uavSim) | Package | 160 | N/A | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [jacinle](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/jacinle) | Package | 145 | N/A | Constrained | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [GCFT](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/GCFT) | Package | 141 | N/A | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [gensphere](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/gensphere) | Package | 132 | N/A | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [genielibs](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/genielibs) | Package | 113 | V24.9 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [laboneq](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/laboneq) | Package | 52 | v2.44.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [schemasheets](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/schemasheets) | Package | 52 | 0.3.1 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [magicattr](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/magicattr) | Package | 18 | v3.9.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [mo_dots](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/mo_dots) | Package | 7 | 10.659.25005 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [pystringattr](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/pystringattr) | Package | 2 | N/A | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [dektools](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/dektools) | Package | N/A | 0.2.59 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [geodesic-api](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/geodesic-api) | Package | N/A | 0.66.0 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |
| [steam-sdk](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/steam-sdk) | Package | N/A | 2025.1.1 | Agnostic | Dual | [Pyrl](https://github.com/jackfromeast/python-class-pollution) | Reported |

<p class="table-legend"><strong>Reach</strong>: <em>Remote</em> = reachable from the network, <em>Local</em> = reachable from local input such as a CLI argument, <em>Package</em> = reachable as a public API of a library and exploitable from any caller of that library. <strong>Get</strong> and <strong>Set</strong> are the <a href="/wiki/docs/taxonomy/primitives/">pollution primitives</a>. <strong>Found by</strong>: this work (Pyrl) unless an external researcher is credited.</p>
