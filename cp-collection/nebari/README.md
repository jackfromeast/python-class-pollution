## nebari

### Meta

+ Repo: nebari
+ Link: https://github.com/nebari-dev/nebari
+ Stars: 286
+ Version: 2024.12.1
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def set_nested_attribute(data: Any, attrs: List[str], value: Any):
    """Takes an arbitrary set of attributes and accesses the deep
    nested object config to set value
    """

    def _get_attr(d: Any, attr: str):
        if isinstance(d, list) and re.fullmatch(r"\d+", attr):
            return d[int(attr)]
        elif hasattr(d, "__getitem__"):
            return d[attr]
        else:
            return getattr(d, attr)

    def _set_attr(d: Any, attr: str, value: Any):
        if isinstance(d, list) and re.fullmatch(r"\d+", attr):
            d[int(attr)] = value
        elif hasattr(d, "__getitem__"):
            d[attr] = value
        else:
            setattr(d, attr, value)

    data_pos = data
    for attr in attrs[:-1]:
        data_pos = _get_attr(data_pos, attr)
    _set_attr(data_pos, attrs[-1], value)

```
