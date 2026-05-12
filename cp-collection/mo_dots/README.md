## mo_dots

### Meta

+ Repo: mo_dots
+ Link: https://github.com/klahnakoski/mo-dots
+ Stars: 6
+ Version: 10.659.25005
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def _set_attr(obj_, path, value):
    obj = _get_attr(obj_, path[:-1])
    if obj is None:
        # DELIBERATE USE OF `is`: WE DO NOT WHAT TO CATCH Null HERE (THEY CAN BE SET)
        get_logger().error(PATH_NOT_FOUND + " tried to get attribute of None")

    attr_name = path[-1]

    # ACTUAL SETTING OF VALUE
    try:
        old_value = _get_attr(obj, [attr_name])
        old_type = _get(old_value, CLASS)
        if is_null(old_value) or is_primitive(old_value):
            old_value = None
            new_value = value
        elif is_null(value):
            new_value = None
        else:
            new_value = _get(old_value, CLASS)(value)  # TRY TO MAKE INSTANCE OF SAME CLASS
    except Exception:
        old_value = None
        new_value = value

    try:
        setattr(obj, attr_name, new_value)
        return old_value
    except Exception as e:
        try:
            obj[attr_name] = new_value
            return old_value
        except Exception as f:
            get_logger().error(PATH_NOT_FOUND, cause=[f, e])
```
