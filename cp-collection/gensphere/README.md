## gensphere

### Meta

+ Repo: gensphere
+ Link: https://github.com/octopus2023-inc/gensphere
+ Stars: 132
+ Version: N/A
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def set_in_context(context, var_parts, value):
    obj = context
    for part in var_parts[:-1]:
        if isinstance(obj, dict):
            if part not in obj:
                obj[part] = {}
            obj = obj[part]
        else:
            if not hasattr(obj, part):
                setattr(obj, part, {})
            obj = getattr(obj, part)
    last_part = var_parts[-1]
    if isinstance(obj, dict):
        obj[last_part] = value
    else:
        setattr(obj, last_part, value)
```
