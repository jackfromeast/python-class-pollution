#!/usr/bin/env python3

"""
@description
---------------------
This script contains the useful gadgets to find the pollutes the objects reflectively during runtime.
"""

def pollute(obj, layer=1, default_val="", method_only=False):
  """
  Pollute the object by changing its attributes or methods.

  @params obj: The object to pollute.
  @params layer: The current layer of the object.
  @params default_val: The default value to pollute the object with.
  @params method_only: If True, only pollute the methods of the object.
  """
  for attr_name in dir(obj):
    attr = getattr(obj, attr_name)
    if method_only and not callable(attr):
      continue
    try:
      setattr(obj, attr_name, default_val)
      print(f"Polluted {attr_name} to {default_val}")
    except Exception as e:
      print(f"Failed to pollute {attr_name} due to {e}")

