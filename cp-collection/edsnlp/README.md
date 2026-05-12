## edsnlp

### Meta

+ Repo: edsnlp
+ Link: https://github.com/aphp/edsnlp
+ Stars: 119
+ Version: v0.15.0
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def set_deep_attr(base, names, val):
    if isinstance(names, str):
        names = split_names(names)
    if len(names) == 0:
        return val
    if len(names) == 1:
        if isinstance(base, (dict, list)):
            base[names[0]] = val
        else:
            setattr(base, names[0], val)
    [current, *remaining] = names
    attr = base[current] if isinstance(base, (dict, list)) else getattr(base, current)
    try:
        set_deep_attr(attr, remaining, val)
    except TypeError:
        new_attr = list(attr)
        set_deep_attr(new_attr, remaining, val)
        return set_attr_item(base, current, tuple(new_attr))
    return base
```
