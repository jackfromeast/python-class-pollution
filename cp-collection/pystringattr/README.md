## pystringattr

### Meta

+ Repo: pystringattr
+ Link: https://github.com/dansimau/pystringattr
+ Stars: 2
+ Version: N/A
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def set(self, base_obj, value, string_attr_path=None):
    """Set value on an object structure using string representation
    of attributes path."""
    if string_attr_path is not None:
        stack = self._parse(string_attr_path)
    else:
        string_attr_path = self._string_attr_path
        stack = self._stack

    # Get the name of the attribute we're setting (the last item in
    # the stack)
    attr = stack.pop()

    # Get the actual object we're going to operate on
    target_obj = self._get(base_obj, stack)

    # Set the attribute or key value
    if attr.access_method == AccessorType.INDEX:
        target_obj[attr.name] = value
    else:
        setattr(target_obj, attr.name, value)


def setstrattr(obj, attr, val):
    """Set value on an object structure using string representation
    of attributes path."""
    return StringAttribute().set(obj, val, attr)
```
