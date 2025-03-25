def getattr_through_attrgetter_op(obj, attr, val):
  """
  @name: getattr_through_attrgetter_op
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through attrgetter_op operation.
  @result: getattr_through_attrgetter_op should be marked as vulnerable.
  """
  from operator import attrgetter
  target = attrgetter(attr[:-1])(obj)
  setattr(target, attr[-1], val)
  return target