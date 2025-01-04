from torchlens.helper_funcs import nested_assign
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)
      

obj = Animal('cat', 11)
addr = [("attr", "__init__"), ("attr", "__globals__"), ("ind", "__name__") ]
nested_assign(obj, addr, 'polluted')

print(__name__)