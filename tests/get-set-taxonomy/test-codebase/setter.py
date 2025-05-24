#1 setattr(obj,name,val)
def setattr_builtin(obj, name, val):
    setattr(obj, name, val)

#2 obj.__setattribute__(name,val)
def setattr_dunder(obj, name, val):
    obj.__setattr__(name,val)

#3 object.__setattr__(obj,name,val)
def object_setattr_dunder(obj, name, val):
    object.__setattr__(obj, name, val)

# special case of object.__setattr__(obj,name,val)
def type_setattr(obj, name, val):
    type(obj).__setattr__(obj, name, val)

#4 obj.__dict__[name]=val 
def dict_dunder_set(obj, name, val):
    obj.__dict__[name] = val

#5 dict[key]=val
def item_set(d, k, v):
    d[k] = v

#6 dict.setdefault(key, val)
def dict_setdefault(d, k, v):
    d.setdefault(k, v)

#7 dict.update(key=val)
def dict_update(d, k, v):
    d.update({k: v})

#8 dict.__setitem__(key, val) 
def setitem_dunder(obj, key, val):
    obj.__setitem__(key, val)

#9 operator.setitem(dict,key,val)
import operator
def setitem_operator(d, k, v):
    operator.setitem(d, k, v)

#10 operator.__setitem__(dict,key,val)
import operator
def setitem_dunder_operator(d, k, v):
    operator.__setitem__(d, k, v)