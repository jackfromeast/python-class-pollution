# ---------------------- GETTERS ----------------------

# #1 getattr(obj, name)
def eval_getattr(obj, name):
    return eval(f"o.{name}", {"o": obj})

def exec_getattr(obj, name):
    scope = {"o": obj}
    exec(f"result = o.{name}", scope)
    return scope["result"]

# #2 obj.__getattribute__(name)
def eval_dunder_getattribute(obj, name):
    return eval(f"o.__getattribute__({repr(name)})", {"o": obj})

def exec_dunder_getattribute(obj, name):
    scope = {"o": obj, "name": name}
    exec("result = o.__getattribute__(name)", scope)
    return scope["result"]

# #3 object.__getattribute__(obj, name)
def eval_object_dunder_getattribute(obj, name):
    return eval("object.__getattribute__(o, name)", {"o": obj, "name": name})

def exec_object_dunder_getattribute(obj, name):
    scope = {"o": obj, "name": name}
    exec("result = object.__getattribute__(o, name)", scope)
    return scope["result"]

# #4 inspect.getattr_static(obj, name)
def eval_inspect_getattr_static(obj, name):
    import inspect
    return eval("inspect.getattr_static(o, name)", {"o": obj, "name": name, "inspect": inspect})

def exec_inspect_getattr_static(obj, name):
    import inspect
    scope = {"o": obj, "name": name, "inspect": inspect}
    exec("result = inspect.getattr_static(o, name)", scope)
    return scope["result"]

# #5 operator.attrgetter(name)(obj)
def eval_operator_attrgetter(obj, name):
    import operator
    return eval("operator.attrgetter(name)(o)", {"o": obj, "name": name, "operator": operator})

def exec_operator_attrgetter(obj, name):
    import operator
    scope = {"o": obj, "name": name, "operator": operator}
    exec("result = operator.attrgetter(name)(o)", scope)
    return scope["result"]

# #6 dir(obj)[index]
def eval_dir_index(obj, index):
    return eval(f"dir(o)[{index}]", {"o": obj})

def exec_dir_index(obj, index):
    scope = {"o": obj, "index": index}
    exec("result = dir(o)[index]", scope)
    return scope["result"]

# #7 vars(obj)[name]
def eval_vars_index(obj, name):
    return eval(f"vars(o)[{repr(name)}]", {"o": obj})

def exec_vars_index(obj, name):
    scope = {"o": obj, "name": name}
    exec("result = vars(o)[name]", scope)
    return scope["result"]

# #8 obj.__dict__[name]
def eval_obj_dict_index(obj, name):
    return eval(f"o.__dict__[{repr(name)}]", {"o": obj})

def exec_obj_dict_index(obj, name):
    scope = {"o": obj, "name": name}
    exec("result = o.__dict__[name]", scope)
    return scope["result"]

# #9 dict[key]
def eval_dict_index(d, k):
    return eval(f"o[{repr(k)}]", {"o": d})

def exec_dict_index(d, k):
    scope = {"o": d, "k": k}
    exec("result = o[k]", scope)
    return scope["result"]

# #10 dict.get(key)
def eval_dict_get(d, k):
    return eval(f"o.get({repr(k)})", {"o": d})

def exec_dict_get(d, k):
    scope = {"o": d, "k": k}
    exec("result = o.get(k)", scope)
    return scope["result"]

# #11 dict.pop(key)
def eval_dict_pop(d, k):
    return eval(f"o.pop({repr(k)})", {"o": d})

def exec_dict_pop(d, k):
    scope = {"o": d, "k": k}
    exec("result = o.pop(k)", scope)
    return scope["result"]

# #12 dict.get(key)
def eval_dict_get(d, k):
    return eval(f"o.get({repr(k)})", {"o": d})

def exec_dict_get(d, k):
    scope = {"o": d, "k": k}
    exec("result = o.get(k)", scope)
    return scope["result"]

# #13 dict.pop(key)
def eval_dict_pop(d, k):
    return eval(f"o.pop({repr(k)})", {"o": d})

def exec_dict_pop(d, k):
    scope = {"o": d, "k": k}
    exec("result = o.pop(k)", scope)
    return scope["result"]

# #14 dict.__getitem__(key)
def eval_dict_dunder_getitem(d, k):
    return eval(f"o.__getitem__({repr(k)})", {"o": d})

def exec_dict_dunder_getitem(d, k):
    scope = {"o": d, "k": k}
    exec("result = o.__getitem__(k)", scope)
    return scope["result"]

# #15 operator.getitem(dict, key)
def eval_operator_getitem(d, k):
    import operator
    return eval("operator.getitem(o, k)", {"o": d, "k": k, "operator": operator})

def exec_operator_getitem(d, k):
    import operator
    scope = {"o": d, "k": k, "operator": operator}
    exec("result = operator.getitem(o, k)", scope)
    return scope["result"]

# #16 operator.__getitem__(dict, key)
def eval_operator_dunder_getitem(d, k):
    import operator
    return eval("operator.__getitem__(o, k)", {"o": d, "k": k, "operator": operator})

def exec_operator_dunder_getitem(d, k):
    import operator
    scope = {"o": d, "k": k, "operator": operator}
    exec("result = operator.__getitem__(o, k)", scope)
    return scope["result"]

# #17 operator.itemgetter(key)(dict)
def eval_operator_itemgetter(d, k):
    import operator
    return eval("operator.itemgetter(k)(o)", {"o": d, "k": k, "operator": operator})

def exec_operator_itemgetter(d, k):
    import operator
    scope = {"o": d, "k": k, "operator": operator}
    exec("result = operator.itemgetter(k)(o)", scope)
    return scope["result"]

# ---------------------- SETTERS ----------------------

# #1 setattr(obj, name, val)
def exec_setattr(obj, name, val):
    exec(f"o.{name} = v", {"o": obj, "v": val})

# #2 object.__setattr__(obj, name, val)
def eval_object_dunder_setattr(obj, name, val):
    return eval("object.__setattr__(o, n, v)", {"o": obj, "n": name, "v": val})

def exec_object_dunder_setattr(obj, name, val):
    scope = {"o": obj, "n": name, "v": val}
    exec("object.__setattr__(o, n, v)", scope)

# #3 obj.__dict__[name] = val
def exec_obj_dict(obj, name, val):
    exec(f"o.__dict__[{repr(name)}] = v", {"o": obj, "v": val})

# #4 dict[key] = val
def exec_dict_index_set(d, k, v):
    exec(f"o[{repr(k)}] = v", {"o": d, "v": v})

# #5 dict.update(key=val)
def eval_dict_update(d, k, v):
    return eval("o.update({key: val})", {"o": d, "key": k, "val": v})

def exec_dict_update(d, k, v):
    scope = {"o": d, "key": k, "val": v}
    exec("o.update({key: val})", scope)

# #6 dict.__setitem__(key, val)
def eval_dict_dunder_setitem(d, k, v):
    return eval("o.__setitem__(k, v)", {"o": d, "k": k, "v": v})

def exec_dict_dunder_setitem(d, k, v):
    scope = {"o": d, "k": k, "v": v}
    exec("o.__setitem__(k, v)", scope)

# #7 operator.setitem(dict, key, val)
def exec_operator_setitem(d, k, v):
    import operator
    exec("operator.setitem(o, k, v)", {"o": d, "k": k, "v": v, "operator": operator})

# #8 operator.__setitem__(dict, key, val)
def exec_operator_dunder_setitem(d, k, v):
    import operator
    exec("operator.__setitem__(o, k, v)", {"o": d, "k": k, "v": v, "operator": operator})