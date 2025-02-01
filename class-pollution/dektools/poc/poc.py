import random

def object_path_set(obj, paths, value, sep='.'):
    cursor = obj
    if isinstance(paths, str):
        paths = paths.split(sep)
    length = len(paths)
    for i, path in enumerate(paths):
        if i == length - 1:
            if hasattr(cursor, '__setitem__'):
                cursor[path] = value
            else:
                setattr(cursor, path, value)
        else:
            if hasattr(cursor, '__getitem__'):
                try:
                    cursor = cursor[path]
                except KeyError:
                    v = cursor.__class__()
                    cursor[path] = v
                    cursor = v
            else:
                try:
                    cursor = getattr(cursor, path)
                except AttributeError:
                    v = cursor.__class__()
                    setattr(cursor, path, v)
                    cursor = v
    return value


class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

object_path_set(obj, '__init__.__globals__.__name__', 'polluted')
print(__name__)
