def getattr_with_walrus_op_1(obj, attrs, val):
  """
  @name: getattr_with_walrus_op_1
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through getattr_with_walrus_op_1 operation.
  @result: getattr_with_walrus_op_1 should be marked as vulnerable.
  """
  *pre_attrs, last_attr = attrs.split('.')
  [obj := getattr(obj, attr) for attr in pre_attrs]

  if isinstance(obj, dict):
    obj[last_attr] = val
  else:
    setattr(obj, last_attr, val)
  return obj

def getattr_with_walrus_op_2(obj, attrs, val):
  """
  @name: getattr_with_walrus_op_2
  @category: class-pollution-func
  @type: get-attr+set-attr
  @desc: Check if the taint propagates through getattr_with_walrus_op_2 operation.
  @result: getattr_with_walrus_op_2 should be marked as vulnerable.
  """
  *pre_attrs, last_attr = attrs.split('.')
  [obj := getattr(obj, attr) for attr in pre_attrs]

  setattr(obj, last_attr, val)
  return obj