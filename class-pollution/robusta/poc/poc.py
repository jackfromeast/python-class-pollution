from robusta.api import update_item_attr
from hikaru import HikaruBase
import random

class Animal(HikaruBase):
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)
update_item_attr(obj, '__init__.__globals__.__name__', 'polluted')

print(__name__)
