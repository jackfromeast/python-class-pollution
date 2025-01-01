from glom import assign as a
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)
a(obj, '__init__.__globals__.__name__', 'polluted')

print(__name__)
