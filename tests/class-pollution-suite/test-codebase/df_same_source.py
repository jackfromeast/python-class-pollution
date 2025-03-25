"""
@description:
--------------------
The tests help to verify the refersTo relation resolving.
"""

def same_source_one_jump1():
  """
  @name: same_source_one_jump1
  @desc: Check if two dataflow nodes share the same source with one function call jump.
  @result: `obj` and `obj1` share the same source across one function call.
  @vuln: false
  @category: dataflow-check
  """
  obj = {}  # Source node
  index = "key"
  val = "value"
  if isinstance(obj, dict):
    _same_source_one_jump_sub(obj, index, val)
  else:
    setattr(obj, index, val)

def _same_source_one_jump_sub(obj1, index, val):
  """
  Helper function for `same_source_one_jump1`.
  @result: `obj1` shares the same source as `obj`.
  """
  obj1[index] = val


def same_source_one_jump2():
  """
  @name: same_source_one_jump2
  @desc: Check if two dataflow nodes share the same source with one function call jump (split path).
  @result: `obj` shares the same source with `obj1` in one of the two sub-functions.
  @vuln: false
  @category: dataflow-check
  """
  obj = {}  # Source node
  index = "key"
  val = "value"
  if isinstance(obj, dict):
    _same_source_one_jump_sub1(obj, index, val)
  else:
    _same_source_one_jump_sub2(obj, index, val)

def _same_source_one_jump_sub1(obj1, index, val):
  """
  Helper function for `same_source_one_jump2`.
  @result: `obj1` shares the same source as `obj`.
  """
  obj1[index] = val

def _same_source_one_jump_sub2(obj1, index, val):
  """
  Helper function for `same_source_one_jump2`.
  @result: `obj1` shares the same source as `obj`.
  """
  setattr(obj1, index, val)


def same_source_two_jumps():
  """
  @name: same_source_two_jumps
  @desc: Check if two dataflow nodes share the same source across two function call jumps.
  @result: `obj` is passed through two functions and updated at the end.
  @vuln: false
  @category: dataflow-check
  """
  obj = {}  # Source node
  index = "key"
  val = "value"
  if isinstance(obj, dict):
    _same_source_two_jumps_sub1(obj, index, val)
  else:
    _same_source_two_jumps_sub2(obj, index, val)

def _same_source_two_jumps_sub1(obj1, index, val):
  """
  First helper function for `same_source_two_jumps`.
  @result: Passes `obj1` to the second function.
  """
  _same_source_two_jumps_sub2(obj1, index, val)

def _same_source_two_jumps_sub2(obj2, index, val):
  """
  Second helper function for `same_source_two_jumps`.
  @result: `obj2` shares the same source as `obj`.
  """
  obj2[index] = val
