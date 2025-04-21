def getattr_through_inspect1(obj, attrs, val):
  """
  @name: getattr_through_inspect1
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through inspect.getattr_static operation.
  @result: getattr_through_inspect1 should be marked as vulnerable.
  """
  for attr in attrs[:-1]:
    from inspect import *
    obj = getattr_static(obj, attr)
    if obj is None:
      raise AttributeError(f"Attribute {attr} not found in {obj}")
  
  setattr(obj, attrs[-1], val)