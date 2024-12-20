def parent(obj, key):
  if isinstance(obj, dict):
    return child1({'obj': obj, 'attr': key})
  else:
    return child2({'obj': obj, 'attr': key})
  
def child1(path):
  return child1_1(path)

def child1_1(path):
  obj = path.get('obj')
  attr = path.get('attr')

  return obj[attr]

def child2(path):
  return child2_1(path)

def child2_1(path):
  object = path['obj']
  attribute = path['attr']

  return getattr(object, attribute)