from meta_dataset.models.experimental.reparameterizable_base_test import _init_reference_module
import subprocess
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)


_init_reference_module(Animal, {"typ":'cat',"age": 11}, [['__init__','__globals__','__name__']], ['polluted'])
print(__name__)
