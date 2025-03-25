def getattr_through_dict_attr_1(obj, attrs, val):
  """
  @name: getattr_through_dict_attr_1
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through __dict__.get or __dict__["attr"] operation.
  @result: getattr_through_dict_attr_1 should be marked as vulnerable.
  """
  for attr in attrs[:-1]:
    obj = obj.__dict__.get(attr)
  
  setattr(obj, attrs[-1], val)

def getattr_through_dict_attr_2(obj, attrs, val):
  """
  @name: getattr_through_dict_attr_2
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through __dict__.get or __dict__["attr"] operation.
  @result: getattr_through_dict_attr_2 should be marked as vulnerable.
  """
  for attr in attrs[:-1]:
    obj = obj.__dict__[attr]
  
  setattr(obj, attrs[-1], val)


def getattr_through_dict_attr_3(obj, attrs, val):
  """
  @name: getattr_through_dict_attr_1
  @category: class-pollution-func
  @type: get-both+set-attr
  @desc: Check if the taint propagates through __dict__.get or __dict__["attr"] operation.
  @result: getattr_through_dict_attr_3 should be marked as vulnerable.
  """
  for attr in attrs[:-1]:
    if hasattr(obj, '__dict__'):
      obj = obj.__dict__.get(attr)
    else:
      obj = obj.get(attr)
  
  setattr(obj, attrs[-1], val)