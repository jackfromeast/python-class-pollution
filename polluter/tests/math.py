import sys
sys.path.insert(0, "/home/jackfromeast/Desktop/python-class-pollution/polluter")

import math
import collections
from polluter import Pollutable
import polluter as pl

po = Pollutable(collections, max_layer=5, lookup_type="getBoth")
modules = po.select("type=module")
callables = po.select("type=callable")
dicts = po.select("type=dict")
classes = po.select("type=class") 
strings = po.select("type=string")
objects = po.select("type=object")
sys = po.select("type=module&name=sys")

print("Modules:")
for path, value in modules.items():
  print(f"{path}: {value}")

# Select callables
print("\nCallables:")
for path, value in callables.items():
  print(f"{path}: {value}")

# print("\nDicts:")
# for path, value in dicts.items():
#   print(f"{path}: {value}")

# print("\nClasses:")
# for path, value in classes.items():
#   print(f"{path}: {value}")

# print("\nStrings:")
# for path, value in strings.items():
#   print(f"{path}: {value}")

# print("\nObjects:")
# for path, value in objects.items():
#   print(f"{path}: {value}")

# print("\nSys:")
# for path, value in sys.items():
#   print(f"{path}: {value}")