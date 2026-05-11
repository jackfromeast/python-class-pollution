## agentlab

### Meta

+ Repo: agentlab
+ Link: https://github.com/ServiceNow/AgentLab
+ Stars: 189
+ Version: v0.3.2
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```_set_value(obj, ['__init__','__globals__', '__name__'], 'polluted')```
+ Foundby: Zhong
+ Report: Pending
+ AppType: App/Lib
+ Input: Func

### Vulnerable Code Snippet

```python
def _set_value(obj, path, value):
    """Set the value of the given path in the given object to the given value."""
    for key in path[:-1]:
        if isinstance(obj, dict):
            obj = obj[key]
        else:
            obj = getattr(obj, key)
    if isinstance(obj, dict):
        obj[path[-1]] = value
    else:
        setattr(obj, path[-1], value)
```
