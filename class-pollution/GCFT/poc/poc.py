from PySide6.QtWidgets import QComboBox
import random

def set_instance_value(instance, access_path: list[tuple], value):
  for access_type, access_arg in access_path[:-1]:
    if access_type == 'attr':
      instance = getattr(instance, access_arg)
    elif access_type == 'item':
      instance = get_instance_item(instance, access_arg)
    else:
      raise NotImplementedError
  
  access_type, access_arg = access_path[-1]
  if access_type == 'attr':
    setattr(instance, access_arg, value)
  elif access_type == 'item':
    set_instance_item(instance, access_arg, value)
  else:
    raise NotImplementedError

def get_instance_item( instance, index):
  if isinstance(index, QComboBox):
    # Dynamic widget indexing.
    index = index.currentIndex()
  return instance[index]

def set_instance_item( instance, index, value):
  if isinstance(index, QComboBox):
    # Dynamic widget indexing.
    index = index.currentIndex()
  instance[index] = value
    
class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

set_instance_value(obj, [('attr', '__init__'), ('attr', '__globals__'), ('item', '__name__')], 'polluted')
print(__name__)