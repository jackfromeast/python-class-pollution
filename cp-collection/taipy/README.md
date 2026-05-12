## Taipy

### Metadata

+ Repo: Taipy
+ Link: https://github.com/Avaiga/taipy
+ Stars: 19.2K
+ Version: v4.0.3
+ CVE: CVE-2025-30374
+ VulnType: get-attr-set-attr
+ Status: Fixed
+ Foundby: Pyrl

### Vulnerable Code Snippet

`_attrsetter` in `taipy/gui/utils/_attributes.py`

```python
# taipy/gui/utils/_attributes.py
def _attrsetter(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")  # user-controlled attr_str is split by "."
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)  # traverses the attribute chain without restriction
    setattr(obj, var_name_split[-1], value)  # sets arbitrary attribute on the resolved object
```
