## Class Pollution

### Class Pollution in Python VS. Prototype Pollution in JS

In Python, properties of an object can be accessed in two distinct ways: `__getitem__` (e.g., `obj[key]`) and `__getattribute__` (e.g., `obj.key`). These approaches differ in applicability: the former is used specifically for `MutableMapping` objects like dictionaries, whereas the latter works for all objects. In contrast, JavaScript does not differentiate between these methods: `obj[key]` and `obj.key` are interchangeable, and the properties accessed through both are treated equivalently.

This makes the vulnerable pattern of class pollution and prototype pollution are different. 

In JavaScript, we are essentially looking for the pattern:

```javascript
// key1 = __proto__, key2 = anyPollutedKey
base[key1][key2] = val
```

However, in Python, this pattern does not enable class attribute pollution. Special attributes like `__init__` cannot be accessed using `base['__init__']`, regardless of whether base is an instance of a custom class (which lacks a `__getitem__` method) or a MutableMapping object (where `__init__` is not stored as a dictionary key).

Therefore, for class pollution, we need the program *not* only support retriving value through `get` function or `base[key]`, but also through `getattr` function.

```python
if hasattr(base, '__getitem__'):
    val = base[key1]  # Access through __getitem__
else:
    val = getattr(base, key1)  # Access through __getattribute__
```

The following are some examples of the library that vulnerable to class pollution:

**glom**

```
def _t_eval(target, _t, scope):
  ...
  elif op == 'P':
      # Path type stuff (fuzzy match)
      # Smartly use getattr or getitem based on the cur's type
      get = scope[TargetRegistry].get_handler('get', cur, path=t_path[2:i+2:2])
      try:
          cur = get(cur, arg)
      except Exception as e:
          pae = PathAccessError(e, Path(_t), i // 2)
```

**pydash**

```
def base_get(obj, key, default=UNSET):
  ...
  if isinstance(obj, dict):
      value = _base_get_dict(obj, key, default=default)
  elif not isinstance(obj, (Mapping, Sequence)) or (
      isinstance(obj, tuple) and hasattr(obj, "_fields")
  ):
      # Don't use getattr for dict/list objects since we don't want class methods/attributes
      # returned for them but do allow getattr for namedtuple.
      value = _base_get_object(obj, key, default=default)
  else:
      value = _base_get_item(obj, key, default=default)
```