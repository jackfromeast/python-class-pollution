from dataclasses import is_dataclass
from collections import OrderedDict, defaultdict, deque, Counter, ChainMap, UserDict, UserList, UserString

def short_repr(val):
  """
  Get a short representation of the object.

  Types:
  - "None" -> "None".
  - "method-wrapper" -> "method-wrapper 'method_name'".
  - "builtin method" -> "builtin method".
  - "string" -> "string".
  - "module" -> "module: module_name".
  - "function" -> "function".
  - "class" -> "class: class_name".
  - "dataclass" -> "dataclass: class_name".
  - "dict" -> "dict".
  - "OrderedDict" -> "OrderedDict".
  - "defaultdict" -> "defaultdict".
  - "deque" -> "deque".
  - "Counter" -> "Counter".
  - "ChainMap" -> "ChainMap".
  - "UserDict" -> "UserDict".
  - "UserList" -> "UserList".
  - "UserString" -> "UserString".
  - "list" -> "list".
  - "tuple" -> "tuple".
  - "set" -> "set".
  - "int", "float", "complex" -> "number".
  - "bool" -> "boolean".
  - "type" -> "type".
  - Default: type(val).__name__.
  """
  if val is None:
    return "None"

  type_name = type(val).__name__

  # Handle method-wrapper
  if type_name == "method-wrapper":
    method_name = getattr(val, "__name__", "unknown_method")
    writable = is_c_written(val)
    if writable:
      return f"method-wrapper (C-written)"
    return f"method-wrapper"

  # Handle builtin methods
  if type_name == "builtin_function_or_method":
    method_name = getattr(val, "__name__", "unknown_method")
    writable = is_c_written(val)
    if writable:
      return f"builtin method (C-written)"
    return f"builtin method"

  # Handle strings
  if isinstance(val, str) and val.__class__.__name__ == "str":
    return "string"

  # Handle modules
  if type_name == "module":
    module_name = getattr(val, "__name__", "UnknownModule")
    return f"module#{module_name}"

  # Handle functions
  if type_name == "function":
    return "function"

  # Handle classes
  if type_name == "type":
    class_name = getattr(val, "__name__", "UnknownClass")
    return f"class#{class_name}"

  # Handle dataclasses
  if is_dataclass(val):
    class_name = val.__class__.__name__
    return f"dataclass#{class_name}"

  # Handle dictionaries
  if type_name == "dict":
    return "dict"

  # Handle OrderedDict
  if isinstance(val, OrderedDict):
    return "OrderedDict"

  # Handle defaultdict
  if isinstance(val, defaultdict):
    return "defaultdict"

  # Handle deque
  if isinstance(val, deque):
    return "deque"

  # Handle Counter
  if isinstance(val, Counter):
    return "Counter"

  # Handle ChainMap
  if isinstance(val, ChainMap):
    return "ChainMap"

  # Handle UserDict
  if isinstance(val, UserDict):
    return "UserDict"

  # Handle UserList
  if isinstance(val, UserList):
    return "UserList"

  # Handle UserString
  if isinstance(val, UserString):
    return "UserString"

  # Handle lists
  if type_name == "list":
    return "list"

  # Handle tuples
  if type_name == "tuple":
    return "tuple"

  # Handle sets
  if type_name == "set":
    return "set"

  # Handle numbers
  if type_name in ["int", "float", "complex"]:
    return "number"

  # Handle booleans
  if type_name == "bool":
    return "boolean"

  # Default case
  return type_name

def is_c_written(func):
  """
  Check if the function is written in C.

  @params func: The function to check.
  """
  try:
    return type(func).__flags__ & (1<<9)
  except Exception as e:
    return False