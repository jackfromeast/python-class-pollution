## pokitoki

### Meta

+ Repo: pokitoki
+ Link: https://github.com/nalgeon/pokitoki/
+ Stars: 315
+ Version: v210
+ CVE: N/A
+ VulnType: get-attr-set-both
+ Status: Pending
+ Payload: ```bot.config.ConfigEditor.set_value("openai.__init__.__globals__.__name__", "polluted")```
+ Foundby: Zhong
+ Report: Pending
+ AppType: App
+ Input: Func

### Vulnerable Code Snippet

```python
def set_value(self, property: str, value: str) -> tuple[bool, bool]:
    """
    Changes a config property value.
    Returns a tuple `(has_changed, is_immediate, new_val)`
        - `has_changed`  = True if the value has actually changed, False otherwise.
        - `is_immediate` = True if the change takes effect immediately, False otherwise.
        - `new_val`        is the new value
    """
    try:
        val = yaml.safe_load(value)
    except Exception:
        raise ValueError(f"Invalid value: {value}")

    old_val = self.get_value(property)
    if val == old_val:
        return False, False, old_val

    if isinstance(old_val, list) and isinstance(val, str):
        # allow changing list properties by adding or removing individual items
        # e.g. /config telegram.usernames +bob
        # or   /config telegram.usernames -alice
        if val[0] == "+":
            item = yaml.safe_load(val[1:])
            val = old_val.copy()
            val.append(item)
        elif val[0] == "-":
            item = yaml.safe_load(val[1:])
            val = old_val.copy()
            val.remove(item)

    old_cls = old_val.__class__
    val_cls = val.__class__
    if old_val is not None and old_cls != val_cls:
        raise ValueError(
            f"Property {property} should be of type {old_cls.__name__}, not {val_cls.__name__}"
        )

    if not isinstance(val, (list, str, int, float, bool)):
        raise ValueError(f"Cannot set composite value for property: {property}")

    names = property.split(".")
    if names[0] not in self.editable:
        raise ValueError(f"Property {property} is not editable")

    is_immediate = property not in self.delayed

    obj = self.config
    for name in names[:-1]:
        obj = getattr(obj, name, val)

    name = names[-1]
    if isinstance(obj, dict):
        obj[name] = val
        return True, is_immediate, val

    if isinstance(obj, object):
        if not hasattr(obj, name):
            raise ValueError(f"No such property: {property}")
        setattr(obj, name, val)
        return True, is_immediate, val

    raise ValueError(f"Failed to set property: {property}")
```
