import random

def set_in_context(context, var_parts, value):
    obj = context
    for part in var_parts[:-1]:
        if isinstance(obj, dict):
            if part not in obj:
                obj[part] = {}
            obj = obj[part]
        else:
            if not hasattr(obj, part):
                setattr(obj, part, {})
            obj = getattr(obj, part)
    last_part = var_parts[-1]
    if isinstance(obj, dict):
        obj[last_part] = value
    else:
        setattr(obj, last_part, value)
        
class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

set_in_context(obj, ['__init__', '__globals__', '__name__'], 'polluted')
print(__name__)