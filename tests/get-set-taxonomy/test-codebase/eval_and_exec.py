# ---------------------- GETTERS ----------------------

# #1 getattr(obj, name)
def eval_getattr(obj, name):
    return eval(f"o.{name}", {"o": obj})

def exec_getattr(obj, name):
    scope = {"o": obj}
    exec(f"result = o.{name}", scope)
    return scope["result"]

# #3 inspect.getattr_static(obj, name)
def eval_inspect_getattr_static(obj, name):
    import inspect
    return eval("inspect.getattr_static(o, name)", {"o": obj, "name": name, "inspect": inspect})

def exec_inspect_getattr_static(obj, name):
    import inspect
    scope = {"o": obj, "name": name, "inspect": inspect}
    exec("result = inspect.getattr_static(o, name)", scope)
    return scope["result"]

# #4 operator.attrgetter(name)(obj)
def eval_operator_attrgetter(obj, name):
    import operator
    return eval("operator.attrgetter(name)(o)", {"o": obj, "name": name, "operator": operator})

def exec_operator_attrgetter(obj, name):
    import operator
    scope = {"o": obj, "name": name, "operator": operator}
    exec("result = operator.attrgetter(name)(o)", scope)
    return scope["result"]

# #5 dir(obj)[index]
def eval_dir_index(obj, index):
    return eval(f"dir(o)[{index}]", {"o": obj})

def exec_dir_index(obj, index):
    scope = {"o": obj, "index": index}
    exec("result = dir(o)[index]", scope)
    return scope["result"]

# #6 vars(obj)[name]
def eval_vars_index(obj, name):
    return eval(f"vars(o)[{repr(name)}]", {"o": obj})

def exec_vars_index(obj, name):
    scope = {"o": obj, "name": name}
    exec("result = vars(o)[name]", scope)
    return scope["result"]

# #7 obj.__dict__[name]
def eval_obj_dict_index(obj, name):
    return eval(f"o.__dict__[{repr(name)}]", {"o": obj})

def exec_obj_dict_index(obj, name):
    scope = {"o": obj, "name": name}
    exec("result = o.__dict__[name]", scope)
    return scope["result"]

# #10 dict[key]
def eval_dict_index(d, k):
    return eval(f"o[{repr(k)}]", {"o": d})

def exec_dict_index(d, k):
    scope = {"o": d, "k": k}
    exec("result = o[k]", scope)
    return scope["result"]

# #11 dict.get(key)
def eval_dict_get(d, k):
    return eval(f"o.get({repr(k)})", {"o": d})

def exec_dict_get(d, k):
    scope = {"o": d, "k": k}
    exec("result = o.get(k)", scope)
    return scope["result"]

# #12 dict.pop(key)
def eval_dict_pop(d, k):
    return eval(f"o.pop({repr(k)})", {"o": d})

def exec_dict_pop(d, k):
    scope = {"o": d, "k": k}
    exec("result = o.pop(k)", scope)
    return scope["result"]

# #14 operator.getitem(dict, key)
def eval_operator_getitem(d, k):
    import operator
    return eval("operator.getitem(o, k)", {"o": d, "k": k, "operator": operator})

def exec_operator_getitem(d, k):
    import operator
    scope = {"o": d, "k": k, "operator": operator}
    exec("result = operator.getitem(o, k)", scope)
    return scope["result"]

# #15 operator.__getitem__(dict, key)
def eval_operator_dunder_getitem(d, k):
    import operator
    return eval("operator.__getitem__(o, k)", {"o": d, "k": k, "operator": operator})

def exec_operator_dunder_getitem(d, k):
    import operator
    scope = {"o": d, "k": k, "operator": operator}
    exec("result = operator.__getitem__(o, k)", scope)
    return scope["result"]

# #16 operator.itemgetter(key)(dict)
def eval_operator_itemgetter(d, k):
    import operator
    return eval("operator.itemgetter(k)(o)", {"o": d, "k": k, "operator": operator})

def exec_operator_itemgetter(d, k):
    import operator
    scope = {"o": d, "k": k, "operator": operator}
    exec("result = operator.itemgetter(k)(o)", scope)
    return scope["result"]

# ---------------------- SETTERS ----------------------

# #setattr(obj, name, val)
def exec_setattr(obj, name, val):
    exec(f"o.{name} = v", {"o": obj, "v": val})

# #obj.__dict__[name] = val
def exec_obj_dict(obj, name, val):
    exec(f"o.__dict__[{repr(name)}] = v", {"o": obj, "v": val})

# #dict[key] = val
def exec_dict_index_set(d, k, v):
    exec(f"o[{repr(k)}] = v", {"o": d, "v": v})

# #operator.setitem(dict, key, val)
def exec_operator_setitem(d, k, v):
    import operator
    exec("operator.setitem(o, k, v)", {"o": d, "k": k, "v": v, "operator": operator})

# #operator.__setitem__(dict, key, val)
def exec_operator_dunder_setitem(d, k, v):
    import operator
    exec("operator.__setitem__(o, k, v)", {"o": d, "k": k, "v": v, "operator": operator})