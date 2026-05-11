## steam-sdk

### Meta

+ Repo: steam-sdk
+ Link: https://steam-sdk.docs.cern.ch/
+ Stars: N/A
+ Version: 2025.1.1
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```rsetattr(obj, "__init__.__globals__.__name__", 'polluted')```
+ Foundby: Zhong
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```python
def rsetattr(obj, attr, val):
    attrs = attr.split('.')
    for attribute in attrs[:-1]:
        if isinstance(obj, dict):
            obj = obj[attribute]
        elif isinstance(obj, list):
            obj = obj[int(attribute)]
        else:
            obj = getattr(obj, attribute)
    if isinstance(obj, dict):
        obj[attrs[-1]] = val
    else:
        setattr(obj, attrs[-1], val)
```
