## JSPyBridge

### Meta

+ Repo: JSPyBridge
+ Link: https://github.com/extremeheat/JSPyBridge
+ Stars: 718
+ Version: 1.2.1
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```PyInterface.Set("", 0, ['python','__globals__','PyInterface'], ('__name__', 'polluted'))```
+ Foundby: Zhong
+ Report: Pending
+ AppType: Lib
+ Input: Func

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
