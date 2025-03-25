def merge_getboth_setboth(src, dst):
  """
  @name: merge_getboth_setboth
  @category: class-pollution-func
  @type: get-both+set-both
  @desc: Check if the taint propagates through merge operation.
  @result: merge_getboth_setboth should be marked as vulnerable.
  """
  for k, v in src.items():
    if hasattr(dst, '__getitem__'):
      if dst.get(k) and type(v) == dict:
        merge_getboth_setboth(v, dst.get(k))
      else:
        dst[k] = v
    elif hasattr(dst, k) and type(v) == dict:
      merge_getboth_setboth(v, getattr(dst, k))
    else:
      setattr(dst, k, v)

def merge_getattr_setboth(src, dst):
  """
  @name: merge_getattr_setboth
  @category: class-pollution-func
  @type: get-attr+set-both
  @desc: Check if the taint propagates through merge operation.
  @result: merge_getattr_setboth should be marked as vulnerable.
  """
  for k, v in src.items():
    if hasattr(dst, '__getitem__'):
      if dst.get(k) and type(v) == dict:
        merge_getattr_setboth(v, getattr(dst, k))
      else:
        dst[k] = v
    elif hasattr(dst, k) and type(v) == dict:
      merge_getattr_setboth(v, getattr(dst, k))
    else:
      setattr(dst, k, v)

def merge_setitem_getboth(src, dst):
  """
  @name: merge_setitem_getboth
  @category: class-pollution-func
  @type: set-item+get-both
  @desc: Check if the taint propagates through merge operation.
  @result: merge_setitem_getboth should be marked as vulnerable.
  """
  for k, v in src.items():
    if hasattr(dst, '__getitem__'):
      if dst.get(k) and type(v) == dict:
        merge_setitem_getboth(v, dst.get(k))
      else:
        dst[k] = v
    elif hasattr(dst, k) and type(v) == dict:
      merge_setitem_getboth(v, getattr(dst, k))
    else:
      dst[k] = v

def merge_setitem_getattr(src, dst):
  """
  @name: merge_setitem_getattr
  @category: class-pollution-func
  @type: set-item+get-attr
  @desc: Check if the taint propagates through merge operation.
  @result: merge_setitem_getattr should be marked as vulnerable.
  """
  for k, v in src.items():
    if hasattr(dst, '__getitem__'):
      if dst.get(k) and type(v) == dict:
        merge_setitem_getattr(v, getattr(dst, k))
      else:
        dst[k] = v
    elif hasattr(dst, k) and type(v) == dict:
      merge_setitem_getattr(v, getattr(dst, k))
    else:
      dst[k] = v

def merge_setattr_getboth(src, dst):
  """
  @name: merge_setattr_getboth
  @category: class-pollution-func
  @type: set-attr+get-both
  @desc: Check if the taint propagates through merge operation.
  @result: merge_setattr_getboth should be marked as vulnerable
  """
  for k, v in src.items():
    if hasattr(dst, '__getitem__'):
      if dst.get(k) and type(v) == dict:
        merge_setattr_getboth(v, dst.get(k))
      else:
        setattr(dst, k, v)
    elif hasattr(dst, k) and type(v) == dict:
      merge_setattr_getboth(v, getattr(dst, k))
    else:
      setattr(dst, k, v)

def merge_setattr_getattr(src, dst):
  """
  @name: merge_setattr_getattr
  @category: class-pollution-func
  @type: set-attr+get-attr
  @desc: Check if the taint propagates through merge operation.
  @result: merge_setattr_getattr should be marked as vulnerable.
  """
  for k, v in src.items():
    if hasattr(dst, '__getitem__'):
      if dst.get(k) and type(v) == dict:
        merge_setattr_getattr(v, getattr(dst, k))
      else:
        setattr(dst, k, v)
    elif hasattr(dst, k) and type(v) == dict:
      merge_setattr_getattr(v, getattr(dst, k))
    else:
      setattr(dst, k, v)