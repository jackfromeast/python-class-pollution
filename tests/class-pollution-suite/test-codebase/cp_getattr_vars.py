def getattr_through_vars_1(obj, attrs, val):
  """
  @name: getattr_through_vars_1
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through __dict__.get or __dict__["attr"] operation.
  @result: getattr_through_vars_1 should be marked as vulnerable.
  """
  for attr in attrs[:-1]:
    obj = vars(obj).get(attr)
  
  setattr(obj, attrs[-1], val)

def getattr_through_vars_2(obj, attrs, val):
  """
  @name: getattr_through_vars_2
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through __dict__.get or __dict__["attr"] operation.
  @result: getattr_through_vars_2 should be marked as vulnerable.
  """
  for attr in attrs[:-1]:
    obj = vars(obj)[attr]
  
  setattr(obj, attrs[-1], val)
