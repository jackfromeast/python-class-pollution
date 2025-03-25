import functools

def getattr_through_reduce(obj, attr, val):
  """
  @name: getattr_through_reduce
  @desc: Check if the taint propagates through reduce function.
  @result: cp_func_through_reduce should be marked as vulnerable.
  @category: class-pollution-func
  @type: set-attr+get-attr
  """
  pre, _, post = attr.rpartition('.')
  return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def rgetattr(obj, attr, *args):
  def _getattr(obj, attr):
    return getattr(obj, attr, *args)
  return functools.reduce(_getattr, [obj] + attr.split('.'))

class Person:
  settings = {
    'autosave': True,
    'style': {
      'height': 30,
      'width': 200
    },
    'themes': ['light', 'dark']
  }
  def __init__(self, name, age, friends):
    self.name = name
    self.age = age
    self.friends = friends

bob = Person(name="Bob", age=31, friends=[])

class_pollution_func_through_reduce(bob, "settings.style", "a")