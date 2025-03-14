#!/usr/bin/env python3

"""
@description
---------------------
This script contains the useful functions to find the pollutables reflectively during runtime.
"""


def find_all_pollutables(obj, type="getAttr", layer=0, max_layer=10, ):
  """
  @description
  ---------------------
  Find all the pollutables in the given object.

  @params obj: The object to find pollutables in.
  @params layer: The current layer of the object.
  @params type: The type of pollutables to find. Default is "getAttr" and alternative is "getBoth".

  @return pollutables: The pollutables found in the object in dictionary format.
  """
  if type == "getAttrOnly":
    return find_all_pollutables_getattr_only(obj, layer)
  elif type == "getBoth":
    pass
    # return find_all_pollutables_get_both(obj, layer)
  else:
    raise Exception(f"Unknown type: {type}")
  

def find_all_pollutables_getattr_only(obj, layer=0, max_layer=10):
  """
  @description
  ---------------------
  Find all the pollutables in the given object.

  @params obj: The object to find pollutables in.
  @params layer: The current layer of the object.
  @params max_layer: The maximum layer to search for pollutables.
  """



  