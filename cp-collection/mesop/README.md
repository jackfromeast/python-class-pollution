## mesop

### Meta

+ Repo: Mesop
+ Link: https://github.com/google/mesop
+ Stars: 6.5K
+ Version: v0.13.0
+ CVE: CVE-2025-30358
+ VulnType: get-attr-set-both
+ Status: Pending
+ Foundby: Pyrl

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
