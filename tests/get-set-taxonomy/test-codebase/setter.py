#1 setattr(obj,name,val)
def setattr_builtin(obj, name, val):
    setattr(obj, name, val)

#2 object.__setattr__(obj,name,val)
def setattr_dunder(obj, name, val):
    object.__setattr__(obj, name, val)

# special case of object.__setattr__(obj,name,val)
def type_setattr(obj, name, val):
    type(obj).__setattr__(obj, name, val)

#3 obj.__dict__[name]=val 
def dict_dunder_set(obj, name, val):
    obj.__dict__[name] = val

#4 dict[key]=val
def item_set(d, k, v):
    d[k] = v

#5 dict.update(key=val)
def dict_update(d, k, v):
    d.update({k: v})

#6 dict.__setitem__(key, val) 
def setitem_dunder(obj, key, val):
    obj.__setitem__(key, val)

#7 operator.setitem(dict,key,val)
import operator
def setitem_operator(d, k, v):
    operator.setitem(d, k, v)

#8 operator.__setitem__(dict,key,val)
import operator
def setitem_dunder_operator(d, k, v):
    operator.__setitem__(d, k, v)