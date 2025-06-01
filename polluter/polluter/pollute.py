#!/usr/bin/env python3

from pollutable import Pollutable

"""
@description
---------------------
This script contains the useful gadgets to find the pollutes the objects reflectively during runtime.
"""

def pollute(obj, layer=1, default_val="polluted", method_only=False):
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


def pollute_all(obj, callable_only=True, default_val="polluted", layer=-1, lookup_type="getAttr"):
  """
  Pollute all the accessible callable attributes of the object.

  @params obj: The object to pollute.
  @params callable_only: If True, only pollute the callable attributes of the object.
  @params default_val: The default value to pollute the object with.
  @params layer: The maximum layer to search for callable attributes.
  @params lookup_type: The type of pollutables to find. Default is "getAttr" and alternative is "getBoth".
  """
  po = Pollutable(obj, max_layer=layer, lookup_type=lookup_type)
  
  target_keys = po.select("type=callable").keys()
  sorted_keys = sorted(target_keys, key=lambda x: len(x), reverse=True)

  for key in sorted_keys:
    try:
      parts = key.split('.')
      current = obj
      for part in parts[:-1]:
        current = getattr(current, part)
      setattr(current, parts[-1], default_val)
      print(f"Polluted {key} to {default_val}")
    except Exception as e:
      # Ignore any error
      print(f"Failed to pollute {key}: {e}")