## GCFT

### Meta

+ Repo: GCFT
+ Link: https://github.com/LagoLunatic/GCFT
+ Stars: 101
+ Version: N/A
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def set_instance_value(instance, access_path: list[tuple], value):
  for access_type, access_arg in access_path[:-1]:
    if access_type == 'attr':
      instance = getattr(instance, access_arg)
    elif access_type == 'item':
      instance = get_instance_item(instance, access_arg)
    else:
      raise NotImplementedError
  
  access_type, access_arg = access_path[-1]
  if access_type == 'attr':
    setattr(instance, access_arg, value)
  elif access_type == 'item':
    set_instance_item(instance, access_arg, value)
  else:
    raise NotImplementedError
```
