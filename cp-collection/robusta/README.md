## robusta

### Meta

+ Repo: robusta
+ Link: https://github.com/robusta-dev/robusta
+ Stars: 2.6K
+ Version: 0.20.0
+ CVE: N/A
+ VulnType: get-both-set-both
+ Status: Pending
+ Foundby: Pyrl

### Vulnerable Code Snippet

```python
def update_item_attr(obj: HikaruBase, attr_key: str, attr_value):
    path_parts = regex.split("\\[|\\].|\\]|\\.", attr_key)
    parent_item = obj.object_at_path(path_parts[0 : len(path_parts) - 1])
    last_part = path_parts[len(path_parts) - 1]
    if type(parent_item) == dict:
        parent_item[last_part] = attr_value
    elif type(parent_item) == list:
        parent_item[int(last_part)] = attr_value
    else:
        setattr(parent_item, last_part, attr_value)
```
