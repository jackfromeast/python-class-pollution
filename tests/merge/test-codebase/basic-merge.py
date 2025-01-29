def merge1(src, dst):
  # Recursive merge function
  for k, v in src.items():
      if hasattr(dst, '__getitem__'):
          if dst.get(k) and type(v) == dict:
              merge1(v, dst.get(k))
          else:
              dst[k] = v
      elif hasattr(dst, k) and type(v) == dict:
          merge1(v, getattr(dst, k))
      else:
          setattr(dst, k, v)


def merge2(src, dst):
  # Recursive merge function
  for k in src.keys():
      if hasattr(dst, '__getitem__'):
          if dst.get(k) and type(v) == dict:
              merge2(v, dst.get(k))
          else:
              v = src[k]
              dst[k] = v
      elif hasattr(dst, k) and type(v) == dict:
          merge2(v, getattr(dst, k))
      else:
          v = getattr(src, k)
          setattr(dst, k, v)


def merge3(src, dst):
  # Recursive merge function
  for k in src:
      if hasattr(dst, '__getitem__'):
          if dst.get(k) and type(v) == dict:
              merge3(v, dst.get(k))
          else:
              v = src[k]
              dst[k] = v
      elif hasattr(dst, k) and type(v) == dict:
          merge3(v, getattr(dst, k))
      else:
          v = getattr(src, k)
          setattr(dst, k, v)


def merge4(src, dst):
  keys = src.split('.')
  for k in keys:
      if hasattr(dst, '__getitem__'):
          if dst.get(k) and type(v) == dict:
              merge4(v, dst.get(k))
          else:
              v = src[k]
              dst[k] = v
      elif hasattr(dst, k) and type(v) == dict:
          merge4(v, getattr(dst, k))
      else:
          v = getattr(src, k)
          setattr(dst, k, v)