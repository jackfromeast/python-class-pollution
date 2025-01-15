# From riven/src/program/media/item.py
def _set_nested_attr(obj, key, value):
  if "." in key:
      parts = key.split(".", 1)
      current_key, rest_of_keys = parts[0], parts[1]

      if not hasattr(obj, current_key):
          raise AttributeError(f"Object does not have the attribute '{current_key}'.")

      current_obj = getattr(obj, current_key)
      _set_nested_attr(current_obj, rest_of_keys, value)
  elif isinstance(obj, dict):
      obj[key] = value
  else:
      setattr(obj, key, value)


from dataclasses import dataclass
@dataclass
class State:
  input: str
  output: str
  textarea_key: int

obj = State('HELLO', 'WORLD', 0)

_set_nested_attr(obj, '__init__.__globals__.__name__', 'polluted')

print(__name__)