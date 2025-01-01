from glom import qq,Assign as c, e,  glom as d, zz
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)
spec = c('__init__.__globals__.__name__', 'polluted')
_ = d(obj, spec)

print(__name__)
