## pyinstrument

### Meta

+ Repo: pyinstrument
+ Link: https://github.com/joerick/pyinstrument
+ Stars: 6.8K
+ Version: N/A
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Payload: ```pyinstrument.vendor.keypath.set_value_at_keypath(obj, '__class__.__init__.__globals__.__name__', 'polluted')```
+ Foundby: Pyrl
+ Report: Pending
+ AppType: Lib
+ Input: Func

### Vulnerable Code Snippet

```python

def set_value_at_keypath(obj: Any, keypath: str, val: Any):
  """
  Sets value at given key path which follows dotted-path notation.

  Each part of the keypath must already exist in the target value
  along the path.

    >>> x = dict(a=1, b=2, c=dict(d=3, e=4, f=[2,dict(x='foo', y='bar'),5]))
    >>> assert set_value_at_keypath(x, 'a', 2)
    >>> assert value_at_keypath(x, 'a') == 2
    >>> assert set_value_at_keypath(x, 'c.f.-1', 6)
    >>> assert value_at_keypath(x, 'c.f.-1') == 6
  """
  parts = keypath.split('.')
  for part in parts[:-1]:
    if isinstance(obj, dict):
      obj = obj[part]
    elif type(obj) in [tuple, list]:
      obj = obj[int(part)]
    else:
      obj = getattr(obj, part)
  last_part = parts[-1]
  if isinstance(obj, dict):
    obj[last_part] = val
  elif type(obj) in [tuple, list]:
    obj[int(last_part)] = val
  else:
    setattr(obj, last_part, val)
  return True
```
