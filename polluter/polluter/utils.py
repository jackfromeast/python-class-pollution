import os
import sys
import inspect
from dataclasses import is_dataclass
from collections import OrderedDict, defaultdict, deque, Counter, ChainMap, UserDict, UserList, UserString
from importlib.util import find_spec

stdlib_paths = {
  os.path.normpath(path) for path in sys.path
  if os.path.isdir(path) and (
    "lib/python" in path and "site-packages" not in path and "dist-packages" not in path
  )
}

def is_from_standard_library(obj):
  module = inspect.getmodule(obj)
  if module is None:
    # If obj is a method-wrapper:
    if type(obj).__name__ in ["method-wrapper", "builtin_function_or_method", "method_descriptor", "getset_descriptor"]:
      return True
    return False

  module_file = getattr(module, "__file__", None)
  # No module file, then it's module builtins
  if module_file is None:
    return True
  
  module_file = os.path.normpath(module_file)
  for path in stdlib_paths:
    if module_file.startswith(os.path.join(path, "")):
      return True
  return False

def is_standard_module(module):
  """
  Check if the module is part of the Python standard library.

  @params module: The module to check.
  @return: True if the module is part of the standard library, False otherwise.
  """
  if module is None:
    return False
  
  module_file = getattr(module, "__file__", None)
  if module_file is None:
    return False
  
  module_file = os.path.normpath(module_file)
  for path in stdlib_paths:
    if module_file.startswith(os.path.join(path, "")):
      return True
  return False

def get_type(val):
  """
  Get the type information of the object, including the full module path for class instances.

  @params val: The object to get the type information for.
  @return: A string representing the type of the object.
            Returns "class" for classes,
            full module-qualified name (e.g., `module.submodule.ClassName`) for class instances,
            and type name for other objects.
  """
  if val is None:
    return "None"

  # If val has a class type, return "class"
  if isinstance(val, type):
    return "class"

  obj_type = type(val)

  try:
    obj_type_str = str(obj_type)
    if obj_type_str.startswith("<class '"):
      cleaned_type_string = obj_type_str.replace("<class '", "").replace("'>", "")
      return cleaned_type_string
  except AttributeError:
    pass

  return obj_type.__name__

def is_class(type_info):
  """
  Check if the type name represents a class.

  @params type_info: The type name to check.
  @return: True if the type name represents a class, False otherwise.
  """
  return type_info in {"class", "ABCMeta", "method_descriptor", "type"}
  
def is_callable(type_info):
  """
  Check if the type name represents a callable.

  @params type_info: The type name to check.
  @return: True if the type name represents a callable, False otherwise.
  """
  return type_info in {
    "function", "builtin_function_or_method",
    "slot wrapper", "method-wrapper"
  }

def is_instance(type_info):
  """
  Check if the type name represents an instance.

  @params type_info: The type name to check.
  @return: True if the type name represents an instance, False otherwise.
  """
  return '.' in type_info

def is_data_structure(type_info):
  """
  Check if the type name represents a data structure.

  @params type_info: The type name to check.
  @return: True if the type name represents a data structure, False otherwise.
  """
  return type_info in {
    "dict", "list", "tuple", "set", "OrderedDict",
    "defaultdict", "deque", "Counter", "ChainMap",
    "UserDict", "UserList", "UserString"
  }

def support_getField_op(type_info):
  """
  Check if the type supports `obj[1]` operation.

  @params type_info: The type name to check.
  @return: True if the type supports getField, False otherwise.
  """
  return type_info in {
    "list", "tuple", "dict", "str", "OrderedDict",
    "defaultdict", "deque", "UserList", "UserDict",
    "ChainMap", "Counter"
  }

def is_primitive(type_info):
  """
  Check if the type is non-primitive.

  @params type_info: The type name to check.
  @return: True if the type is non-primitive, False otherwise.
  """
  return type_info in {
    "int", "float", "complex", "bool", "str"
  }

def get_name_info(val):
  """
  Get appropriate name for different object types.

  @params val: The object to inspect.
  @return: Name for modules/callables, value for strings, type name otherwise.
  """
  if val is None:
    return "None"

  type_name = type(val).__name__

  if type_name == "method-wrapper":
    return getattr(val, "__name__", "unknown_method")
  elif type_name == "builtin_function_or_method":
    return getattr(val, "__name__", "unknown_method")
  elif isinstance(val, str):
    return val
  elif type_name == "module":
    return getattr(val, "__name__", "UnknownModule")
  elif type_name == "function":
    return getattr(val, "__name__", "unknown_function")
  elif type_name == "type":
    return getattr(val, "__name__", "UnknownClass")
  elif is_data_structure(type_name):
    return type_name
  else:
    return type_name

def is_c_written(func, type_info):
  """
  Check if the function is written in C.

  @params func: The function to check.
  """
  if not is_callable(type_info):
    return False
  
  try:
    if type(func).__flags__ & (1<<9):
      return True
    else:
      return False
  except Exception as e:
    return False