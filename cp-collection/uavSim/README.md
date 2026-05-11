## uavSim

### Meta

+ Repo: uavSim
+ Link: https://github.com/theilem/uavSim
+ Stars: 121
+ Version: N/A
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```uavSim.utils.setattr_recursive("__init__/__globals__/__name__", "polluted")```
+ Foundby: Pyrl
+ Report: Pending
+ AppType: App
+ Input: Func

### Vulnerable Code Snippet

```python
def setattr_recursive(obj, s, val):
    if not isinstance(s, list):
        s = s.split('/')

    if isinstance(obj, dict):
        if not s[0] in obj:
            s.insert(0, 'params')
        if len(s) > 1:
            return setattr_recursive(obj[s[0]], s[1:], val)
        else:
            obj[s[0]] = val
            return None
    if not hasattr(obj, s[0]):
        s.insert(0, 'params')
    return setattr_recursive(getattr(obj, s[0]), s[1:], val) if len(s) > 1 else setattr(obj, s[0],
                                                                                        val)
```
